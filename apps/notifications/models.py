from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator

User = get_user_model()


class EmailTemplate(models.Model):
    """Modèles pour les templates d'emails"""
    
    TEMPLATE_TYPES = [
        ('welcome', _('Email de bienvenue')),
        ('order_confirmation', _('Confirmation de commande')),
        ('order_shipped', _('Commande expédiée')),
        ('order_delivered', _('Commande livrée')),
        ('password_reset', _('Réinitialisation de mot de passe')),
        ('newsletter', _('Newsletter')),
        ('stock_alert', _('Alerte de stock')),
        ('promotion', _('Promotion')),
        ('abandoned_cart', _('Panier abandonné')),
    ]
    
    name = models.CharField(_('nom'), max_length=100)
    template_type = models.CharField(_('type de template'), max_length=50, choices=TEMPLATE_TYPES, unique=True)
    subject = models.CharField(_('sujet'), max_length=200)
    html_content = models.TextField(_('contenu HTML'))
    text_content = models.TextField(_('contenu texte'), blank=True)
    is_active = models.BooleanField(_('actif'), default=True)
    created_at = models.DateTimeField(_('créé le'), auto_now_add=True)
    updated_at = models.DateTimeField(_('modifié le'), auto_now=True)
    
    class Meta:
        verbose_name = _('Template email')
        verbose_name_plural = _('Templates email')
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.get_template_type_display()})"


class EmailLog(models.Model):
    """Log des emails envoyés"""
    
    STATUS_CHOICES = [
        ('pending', _('En attente')),
        ('sent', _('Envoyé')),
        ('failed', _('Échoué')),
        ('bounced', _('Rejeté')),
    ]
    
    template = models.ForeignKey(EmailTemplate, on_delete=models.CASCADE, related_name='logs')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='email_logs')
    recipient_email = models.EmailField(_('email destinataire'))
    subject = models.CharField(_('sujet'), max_length=200)
    status = models.CharField(_('statut'), max_length=20, choices=STATUS_CHOICES, default='pending')
    sent_at = models.DateTimeField(_('envoyé le'), null=True, blank=True)
    error_message = models.TextField(_('message d\'erreur'), blank=True)
    metadata = models.JSONField(_('métadonnées'), default=dict, blank=True)
    created_at = models.DateTimeField(_('créé le'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('Log email')
        verbose_name_plural = _('Logs email')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.recipient_email} - {self.subject} ({self.get_status_display()})"


class Notification(models.Model):
    """Notifications système"""
    
    NOTIFICATION_TYPES = [
        ('info', _('Information')),
        ('success', _('Succès')),
        ('warning', _('Avertissement')),
        ('error', _('Erreur')),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(_('titre'), max_length=200)
    message = models.TextField(_('message'))
    notification_type = models.CharField(_('type'), max_length=20, choices=NOTIFICATION_TYPES, default='info')
    is_read = models.BooleanField(_('lu'), default=False)
    action_url = models.URLField(_('URL d\'action'), blank=True)
    metadata = models.JSONField(_('métadonnées'), default=dict, blank=True)
    created_at = models.DateTimeField(_('créé le'), auto_now_add=True)
    read_at = models.DateTimeField(_('lu le'), null=True, blank=True)
    
    class Meta:
        verbose_name = _('Notification')
        verbose_name_plural = _('Notifications')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.email} - {self.title}"


class Newsletter(models.Model):
    """Gestion des newsletters"""
    
    STATUS_CHOICES = [
        ('draft', _('Brouillon')),
        ('scheduled', _('Programmé')),
        ('sending', _('En cours d\'envoi')),
        ('sent', _('Envoyé')),
        ('cancelled', _('Annulé')),
    ]
    
    title = models.CharField(_('titre'), max_length=200)
    subject = models.CharField(_('sujet'), max_length=200)
    content = models.TextField(_('contenu'))
    status = models.CharField(_('statut'), max_length=20, choices=STATUS_CHOICES, default='draft')
    scheduled_at = models.DateTimeField(_('programmé pour'), null=True, blank=True)
    sent_at = models.DateTimeField(_('envoyé le'), null=True, blank=True)
    recipients_count = models.PositiveIntegerField(_('nombre de destinataires'), default=0)
    opened_count = models.PositiveIntegerField(_('nombre d\'ouvertures'), default=0)
    clicked_count = models.PositiveIntegerField(_('nombre de clics'), default=0)
    created_at = models.DateTimeField(_('créé le'), auto_now_add=True)
    updated_at = models.DateTimeField(_('modifié le'), auto_now=True)
    
    class Meta:
        verbose_name = _('Newsletter')
        verbose_name_plural = _('Newsletters')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} ({self.get_status_display()})"


class NewsletterSubscription(models.Model):
    """Abonnements à la newsletter"""
    
    email = models.EmailField(_('email'), unique=True)
    is_active = models.BooleanField(_('actif'), default=True)
    subscribed_at = models.DateTimeField(_('abonné le'), auto_now_add=True)
    unsubscribed_at = models.DateTimeField(_('désabonné le'), null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='newsletter_subscriptions')
    
    class Meta:
        verbose_name = _('Abonnement newsletter')
        verbose_name_plural = _('Abonnements newsletter')
        ordering = ['-subscribed_at']
    
    def __str__(self):
        return f"{self.email} ({'Actif' if self.is_active else 'Inactif'})"

