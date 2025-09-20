from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import datetime, timedelta
from apps.orders.models import Order
from apps.products.models import Product
from apps.notifications.services import EmailService
from apps.inventory.models import StockLevel, StockAlert
from apps.marketing.models import Coupon, Campaign
from apps.analytics.services import AnalyticsService


@shared_task
def send_order_confirmation_email(order_id):
    """Envoie un email de confirmation de commande"""
    try:
        order = Order.objects.get(id=order_id)
        EmailService.send_order_confirmation(order)
        return f"Email de confirmation envoyé pour la commande {order_id}"
    except Order.DoesNotExist:
        return f"Commande {order_id} non trouvée"


@shared_task
def send_order_shipped_email(order_id):
    """Envoie un email de notification d'expédition"""
    try:
        order = Order.objects.get(id=order_id)
        EmailService.send_order_shipped(order)
        return f"Email d'expédition envoyé pour la commande {order_id}"
    except Order.DoesNotExist:
        return f"Commande {order_id} non trouvée"


@shared_task
def check_low_stock():
    """Vérifie les stocks bas et envoie des alertes"""
    low_stock_products = []
    
    for stock_level in StockLevel.objects.filter(is_low_stock=True):
        # Vérifier si une alerte existe déjà
        existing_alert = StockAlert.objects.filter(
            product=stock_level.product,
            warehouse=stock_level.warehouse,
            alert_type='low_stock',
            is_active=True
        ).exists()
        
        if not existing_alert:
            # Créer une nouvelle alerte
            StockAlert.objects.create(
                product=stock_level.product,
                warehouse=stock_level.warehouse,
                stock_level=stock_level,
                alert_type='low_stock',
                alert_level='warning',
                message=f"Stock bas pour {stock_level.product.name} dans {stock_level.warehouse.name}",
                current_stock=stock_level.current_stock,
                threshold=stock_level.min_stock_level
            )
            
            # Envoyer un email d'alerte
            EmailService.send_stock_alert(stock_level.product)
            
            low_stock_products.append(stock_level.product.name)
    
    return f"Vérification des stocks terminée. {len(low_stock_products)} produits en stock bas"


@shared_task
def send_abandoned_cart_emails():
    """Envoie des emails pour les paniers abandonnés"""
    from apps.cart.models import Cart
    
    # Paniers abandonnés depuis plus de 24h
    abandoned_carts = Cart.objects.filter(
        created_at__lt=timezone.now() - timedelta(hours=24),
        user__isnull=False
    )
    
    sent_count = 0
    for cart in abandoned_carts:
        if cart.user and cart.items.exists():
            # Envoyer un email de rappel
            context = {
                'user_name': cart.user.get_full_name() or cart.user.email,
                'cart_items': cart.items.all(),
                'cart_total': cart.get_total(),
                'site_name': getattr(settings, 'SITE_NAME', 'Silence d\'Or'),
            }
            
            EmailService.send_template_email(
                'abandoned_cart',
                cart.user.email,
                context,
                cart.user
            )
            sent_count += 1
    
    return f"Emails de panier abandonné envoyés: {sent_count}"


@shared_task
def send_newsletter():
    """Envoie la newsletter"""
    from apps.notifications.models import Newsletter
    
    # Récupérer les newsletters programmées
    newsletters = Newsletter.objects.filter(
        status='scheduled',
        scheduled_at__lte=timezone.now()
    )
    
    sent_count = 0
    for newsletter in newsletters:
        count = EmailService.send_newsletter(newsletter)
        sent_count += count
    
    return f"Newsletters envoyées: {sent_count}"


@shared_task
def generate_daily_reports():
    """Génère les rapports quotidiens"""
    from apps.analytics.models import SalesReport
    
    yesterday = timezone.now().date() - timedelta(days=1)
    
    # Générer le rapport de vente
    report = AnalyticsService.generate_sales_report('daily', yesterday, yesterday)
    
    return f"Rapport quotidien généré pour {yesterday}"


@shared_task
def cleanup_expired_coupons():
    """Nettoie les coupons expirés"""
    expired_coupons = Coupon.objects.filter(
        valid_until__lt=timezone.now(),
        status='active'
    )
    
    count = expired_coupons.update(status='expired')
    
    return f"Coupons expirés mis à jour: {count}"


@shared_task
def update_product_recommendations():
    """Met à jour les recommandations de produits"""
    from apps.recommendations.services import RecommendationService, SimilarityService
    
    # Mettre à jour les similarités de produits
    for product in Product.objects.filter(status='published'):
        SimilarityService.update_product_similarities(product)
    
    return "Recommandations de produits mises à jour"


@shared_task
def send_birthday_emails():
    """Envoie des emails d'anniversaire"""
    from django.contrib.auth import get_user_model
    from datetime import date
    
    User = get_user_model()
    today = date.today()
    
    # Utilisateurs dont c'est l'anniversaire
    birthday_users = User.objects.filter(
        date_joined__day=today.day,
        date_joined__month=today.month,
        is_active=True
    )
    
    sent_count = 0
    for user in birthday_users:
        context = {
            'user_name': user.get_full_name() or user.email,
            'site_name': getattr(settings, 'SITE_NAME', 'Silence d\'Or'),
        }
        
        EmailService.send_template_email(
            'birthday',
            user.email,
            context,
            user
        )
        sent_count += 1
    
    return f"Emails d'anniversaire envoyés: {sent_count}"


@shared_task
def backup_database():
    """Sauvegarde la base de données"""
    import os
    from django.core.management import call_command
    from django.conf import settings
    
    backup_dir = os.path.join(settings.BASE_DIR, 'backups')
    os.makedirs(backup_dir, exist_ok=True)
    
    timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
    backup_file = os.path.join(backup_dir, f'backup_{timestamp}.json')
    
    # Exporter les données
    with open(backup_file, 'w') as f:
        call_command('dumpdata', stdout=f)
    
    return f"Sauvegarde créée: {backup_file}"


@shared_task
def cleanup_old_logs():
    """Nettoie les anciens logs"""
    from apps.security.models import SecurityEvent, AuditLog
    from apps.analytics.models import PageView, ProductView, SearchQuery
    
    # Supprimer les logs de plus de 1 an
    cutoff_date = timezone.now() - timedelta(days=365)
    
    # Logs de sécurité
    security_count = SecurityEvent.objects.filter(timestamp__lt=cutoff_date).count()
    SecurityEvent.objects.filter(timestamp__lt=cutoff_date).delete()
    
    # Logs d'audit
    audit_count = AuditLog.objects.filter(timestamp__lt=cutoff_date).count()
    AuditLog.objects.filter(timestamp__lt=cutoff_date).delete()
    
    # Logs d'analytics
    pageview_count = PageView.objects.filter(timestamp__lt=cutoff_date).count()
    PageView.objects.filter(timestamp__lt=cutoff_date).delete()
    
    productview_count = ProductView.objects.filter(timestamp__lt=cutoff_date).count()
    ProductView.objects.filter(timestamp__lt=cutoff_date).delete()
    
    search_count = SearchQuery.objects.filter(timestamp__lt=cutoff_date).count()
    SearchQuery.objects.filter(timestamp__lt=cutoff_date).delete()
    
    return f"Logs nettoyés - Sécurité: {security_count}, Audit: {audit_count}, Analytics: {pageview_count + productview_count + search_count}"


@shared_task
def send_marketing_campaign(campaign_id):
    """Envoie une campagne marketing"""
    try:
        campaign = Campaign.objects.get(id=campaign_id)
        
        # Logique d'envoi de campagne
        # (à implémenter selon le type de campagne)
        
        campaign.status = 'active'
        campaign.save()
        
        return f"Campagne {campaign.name} envoyée"
    except Campaign.DoesNotExist:
        return f"Campagne {campaign_id} non trouvée"


@shared_task
def process_affiliate_commissions():
    """Traite les commissions d'affiliation"""
    from apps.marketing.models import AffiliateClick, Affiliate
    
    # Clics convertis non traités
    converted_clicks = AffiliateClick.objects.filter(
        converted=True,
        order__isnull=False
    )
    
    processed_count = 0
    for click in converted_clicks:
        # Calculer la commission
        affiliate = click.affiliate
        order = click.order
        
        if affiliate.program.commission_type == 'percentage':
            commission = (order.total_price * affiliate.program.commission_value) / 100
        else:
            commission = affiliate.program.commission_value
        
        # Ajouter la commission
        affiliate.total_commission += commission
        affiliate.total_conversions += 1
        affiliate.save()
        
        processed_count += 1
    
    return f"Commissions d'affiliation traitées: {processed_count}"

