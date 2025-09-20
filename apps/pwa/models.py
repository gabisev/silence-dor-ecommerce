from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

User = get_user_model()


class PushSubscription(models.Model):
    """Abonnements aux notifications push"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='push_subscriptions')
    endpoint = models.URLField(_('endpoint'), max_length=500)
    p256dh_key = models.CharField(_('clé P256DH'), max_length=200)
    auth_key = models.CharField(_('clé d\'authentification'), max_length=200)
    
    # Métadonnées
    user_agent = models.TextField(_('user agent'), blank=True)
    is_active = models.BooleanField(_('actif'), default=True)
    
    created_at = models.DateTimeField(_('créé le'), auto_now_add=True)
    updated_at = models.DateTimeField(_('modifié le'), auto_now=True)
    
    class Meta:
        verbose_name = _('Abonnement push')
        verbose_name_plural = _('Abonnements push')
        unique_together = ['user', 'endpoint']
    
    def __str__(self):
        return f"{self.user.email} - {self.endpoint[:50]}..."


class OfflinePage(models.Model):
    """Pages disponibles hors ligne"""
    
    name = models.CharField(_('nom'), max_length=200)
    url = models.CharField(_('URL'), max_length=200)
    content = models.TextField(_('contenu'))
    is_active = models.BooleanField(_('actif'), default=True)
    
    created_at = models.DateTimeField(_('créé le'), auto_now_add=True)
    updated_at = models.DateTimeField(_('modifié le'), auto_now=True)
    
    class Meta:
        verbose_name = _('Page hors ligne')
        verbose_name_plural = _('Pages hors ligne')
    
    def __str__(self):
        return f"{self.name} - {self.url}"


class ServiceWorker(models.Model):
    """Configuration du Service Worker"""
    
    name = models.CharField(_('nom'), max_length=200)
    version = models.CharField(_('version'), max_length=20)
    script_content = models.TextField(_('contenu du script'))
    is_active = models.BooleanField(_('actif'), default=True)
    
    created_at = models.DateTimeField(_('créé le'), auto_now_add=True)
    updated_at = models.DateTimeField(_('modifié le'), auto_now=True)
    
    class Meta:
        verbose_name = _('Service Worker')
        verbose_name_plural = _('Service Workers')
    
    def __str__(self):
        return f"{self.name} v{self.version}"

