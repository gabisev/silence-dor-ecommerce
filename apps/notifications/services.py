import logging
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.html import strip_tags
from django.contrib.auth import get_user_model
from .models import EmailTemplate, EmailLog, Notification, NewsletterSubscription
from apps.orders.models import Order
from apps.products.models import Product

User = get_user_model()
logger = logging.getLogger(__name__)


class EmailService:
    """Service pour l'envoi d'emails"""
    
    @staticmethod
    def send_template_email(template_type, recipient_email, context=None, user=None):
        """Envoie un email basé sur un template"""
        try:
            template = EmailTemplate.objects.get(template_type=template_type, is_active=True)
            
            if context is None:
                context = {}
            
            # Rendu du contenu HTML
            html_content = template.html_content.format(**context)
            text_content = template.text_content.format(**context) if template.text_content else strip_tags(html_content)
            subject = template.subject.format(**context)
            
            # Création du log
            email_log = EmailLog.objects.create(
                template=template,
                recipient=user,
                recipient_email=recipient_email,
                subject=subject,
                status='pending',
                metadata=context
            )
            
            # Envoi de l'email
            msg = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[recipient_email]
            )
            msg.attach_alternative(html_content, "text/html")
            
            result = msg.send()
            
            if result:
                email_log.status = 'sent'
                email_log.sent_at = timezone.now()
                email_log.save()
                logger.info(f"Email envoyé avec succès à {recipient_email}")
                return True
            else:
                email_log.status = 'failed'
                email_log.error_message = "Échec de l'envoi"
                email_log.save()
                logger.error(f"Échec de l'envoi d'email à {recipient_email}")
                return False
                
        except EmailTemplate.DoesNotExist:
            logger.error(f"Template {template_type} non trouvé")
            return False
        except Exception as e:
            logger.error(f"Erreur lors de l'envoi d'email: {str(e)}")
            if 'email_log' in locals():
                email_log.status = 'failed'
                email_log.error_message = str(e)
                email_log.save()
            return False
    
    @staticmethod
    def send_welcome_email(user):
        """Email de bienvenue pour un nouvel utilisateur"""
        context = {
            'user_name': user.get_full_name() or user.email,
            'site_name': getattr(settings, 'SITE_NAME', 'Silence d\'Or'),
            'login_url': f"{settings.FRONTEND_URL}/accounts/login/",
        }
        return EmailService.send_template_email('welcome', user.email, context, user)
    
    @staticmethod
    def send_order_confirmation(order):
        """Email de confirmation de commande"""
        context = {
            'user_name': order.user.get_full_name() or order.user.email,
            'order_id': order.id,
            'order_total': order.get_total_price(),
            'order_date': order.created_at.strftime('%d/%m/%Y'),
            'site_name': getattr(settings, 'SITE_NAME', 'Silence d\'Or'),
            'order_url': f"{settings.FRONTEND_URL}/orders/{order.id}/",
        }
        return EmailService.send_template_email('order_confirmation', order.user.email, context, order.user)
    
    @staticmethod
    def send_order_shipped(order):
        """Email de notification d'expédition"""
        context = {
            'user_name': order.user.get_full_name() or order.user.email,
            'order_id': order.id,
            'tracking_number': getattr(order, 'tracking_number', 'N/A'),
            'site_name': getattr(settings, 'SITE_NAME', 'Silence d\'Or'),
            'order_url': f"{settings.FRONTEND_URL}/orders/{order.id}/",
        }
        return EmailService.send_template_email('order_shipped', order.user.email, context, order.user)
    
    @staticmethod
    def send_stock_alert(product):
        """Alerte de stock bas"""
        # Récupérer les administrateurs
        admins = User.objects.filter(is_staff=True, is_active=True)
        
        context = {
            'product_name': product.name,
            'current_stock': product.quantity,
            'low_stock_threshold': product.low_stock_threshold,
            'product_url': f"{settings.FRONTEND_URL}/admin/products/product/{product.id}/change/",
        }
        
        results = []
        for admin in admins:
            result = EmailService.send_template_email('stock_alert', admin.email, context, admin)
            results.append(result)
        
        return all(results)
    
    @staticmethod
    def send_newsletter(newsletter):
        """Envoi de newsletter"""
        subscribers = NewsletterSubscription.objects.filter(is_active=True)
        newsletter.recipients_count = subscribers.count()
        newsletter.status = 'sending'
        newsletter.save()
        
        context = {
            'content': newsletter.content,
            'site_name': getattr(settings, 'SITE_NAME', 'Silence d\'Or'),
            'unsubscribe_url': f"{settings.FRONTEND_URL}/newsletter/unsubscribe/",
        }
        
        sent_count = 0
        for subscriber in subscribers:
            context['subscriber_email'] = subscriber.email
            result = EmailService.send_template_email('newsletter', subscriber.email, context)
            if result:
                sent_count += 1
        
        newsletter.sent_at = timezone.now()
        newsletter.status = 'sent'
        newsletter.save()
        
        return sent_count


class NotificationService:
    """Service pour les notifications système"""
    
    @staticmethod
    def create_notification(user, title, message, notification_type='info', action_url=None, metadata=None):
        """Crée une notification pour un utilisateur"""
        notification = Notification.objects.create(
            user=user,
            title=title,
            message=message,
            notification_type=notification_type,
            action_url=action_url,
            metadata=metadata or {}
        )
        return notification
    
    @staticmethod
    def mark_as_read(notification_id, user):
        """Marque une notification comme lue"""
        try:
            notification = Notification.objects.get(id=notification_id, user=user)
            notification.is_read = True
            notification.read_at = timezone.now()
            notification.save()
            return True
        except Notification.DoesNotExist:
            return False
    
    @staticmethod
    def get_unread_count(user):
        """Retourne le nombre de notifications non lues"""
        return Notification.objects.filter(user=user, is_read=False).count()
    
    @staticmethod
    def create_order_notification(order, action):
        """Crée une notification pour une action sur une commande"""
        messages = {
            'created': f"Votre commande #{order.id} a été créée avec succès.",
            'paid': f"Votre commande #{order.id} a été payée.",
            'shipped': f"Votre commande #{order.id} a été expédiée.",
            'delivered': f"Votre commande #{order.id} a été livrée.",
            'cancelled': f"Votre commande #{order.id} a été annulée.",
        }
        
        title = f"Commande #{order.id}"
        message = messages.get(action, f"Statut de votre commande #{order.id} mis à jour.")
        action_url = f"/orders/{order.id}/"
        
        return NotificationService.create_notification(
            order.user, title, message, 'info', action_url
        )


class NewsletterService:
    """Service pour la gestion des newsletters"""
    
    @staticmethod
    def subscribe(email, user=None):
        """Abonne un email à la newsletter"""
        subscription, created = NewsletterSubscription.objects.get_or_create(
            email=email,
            defaults={'user': user, 'is_active': True}
        )
        
        if not created and not subscription.is_active:
            subscription.is_active = True
            subscription.unsubscribed_at = None
            subscription.save()
        
        return subscription
    
    @staticmethod
    def unsubscribe(email):
        """Désabonne un email de la newsletter"""
        try:
            subscription = NewsletterSubscription.objects.get(email=email)
            subscription.is_active = False
            subscription.unsubscribed_at = timezone.now()
            subscription.save()
            return True
        except NewsletterSubscription.DoesNotExist:
            return False
    
    @staticmethod
    def get_subscriber_count():
        """Retourne le nombre d'abonnés actifs"""
        return NewsletterSubscription.objects.filter(is_active=True).count()

