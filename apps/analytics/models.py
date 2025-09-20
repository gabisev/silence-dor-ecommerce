from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

User = get_user_model()


class PageView(models.Model):
    """Vues de pages pour analytics"""
    
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    session_key = models.CharField(_('clé de session'), max_length=40, blank=True)
    url = models.URLField(_('URL'))
    referrer = models.URLField(_('référent'), blank=True)
    user_agent = models.TextField(_('user agent'), blank=True)
    ip_address = models.GenericIPAddressField(_('adresse IP'), null=True, blank=True)
    timestamp = models.DateTimeField(_('horodatage'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('Vue de page')
        verbose_name_plural = _('Vues de pages')
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.url} - {self.timestamp}"


class ProductView(models.Model):
    """Vues de produits pour analytics"""
    
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    session_key = models.CharField(_('clé de session'), max_length=40, blank=True)
    product_id = models.PositiveIntegerField(_('ID produit'))
    product_name = models.CharField(_('nom du produit'), max_length=200)
    category = models.CharField(_('catégorie'), max_length=100, blank=True)
    price = models.DecimalField(_('prix'), max_digits=10, decimal_places=2, null=True, blank=True)
    timestamp = models.DateTimeField(_('horodatage'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('Vue de produit')
        verbose_name_plural = _('Vues de produits')
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.product_name} - {self.timestamp}"


class SearchQuery(models.Model):
    """Requêtes de recherche pour analytics"""
    
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    session_key = models.CharField(_('clé de session'), max_length=40, blank=True)
    query = models.CharField(_('requête'), max_length=200)
    results_count = models.PositiveIntegerField(_('nombre de résultats'), default=0)
    timestamp = models.DateTimeField(_('horodatage'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('Requête de recherche')
        verbose_name_plural = _('Requêtes de recherche')
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.query} ({self.results_count} résultats)"


class Conversion(models.Model):
    """Conversions pour analytics"""
    
    CONVERSION_TYPES = [
        ('purchase', _('Achat')),
        ('signup', _('Inscription')),
        ('newsletter', _('Newsletter')),
        ('contact', _('Contact')),
    ]
    
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    session_key = models.CharField(_('clé de session'), max_length=40, blank=True)
    conversion_type = models.CharField(_('type de conversion'), max_length=20, choices=CONVERSION_TYPES)
    value = models.DecimalField(_('valeur'), max_digits=10, decimal_places=2, null=True, blank=True)
    metadata = models.JSONField(_('métadonnées'), default=dict, blank=True)
    timestamp = models.DateTimeField(_('horodatage'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('Conversion')
        verbose_name_plural = _('Conversions')
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.get_conversion_type_display()} - {self.timestamp}"


class UserActivity(models.Model):
    """Activité utilisateur pour analytics"""
    
    ACTIVITY_TYPES = [
        ('login', _('Connexion')),
        ('logout', _('Déconnexion')),
        ('register', _('Inscription')),
        ('profile_update', _('Mise à jour profil')),
        ('password_change', _('Changement mot de passe')),
        ('cart_add', _('Ajout au panier')),
        ('cart_remove', _('Retrait du panier')),
        ('wishlist_add', _('Ajout aux favoris')),
        ('wishlist_remove', _('Retrait des favoris')),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    activity_type = models.CharField(_('type d\'activité'), max_length=20, choices=ACTIVITY_TYPES)
    metadata = models.JSONField(_('métadonnées'), default=dict, blank=True)
    timestamp = models.DateTimeField(_('horodatage'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('Activité utilisateur')
        verbose_name_plural = _('Activités utilisateur')
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.user.email} - {self.get_activity_type_display()}"


class SalesReport(models.Model):
    """Rapports de ventes"""
    
    REPORT_TYPES = [
        ('daily', _('Quotidien')),
        ('weekly', _('Hebdomadaire')),
        ('monthly', _('Mensuel')),
        ('yearly', _('Annuel')),
    ]
    
    report_type = models.CharField(_('type de rapport'), max_length=20, choices=REPORT_TYPES)
    period_start = models.DateField(_('début de période'))
    period_end = models.DateField(_('fin de période'))
    
    # Métriques de vente
    total_orders = models.PositiveIntegerField(_('total commandes'), default=0)
    total_revenue = models.DecimalField(_('chiffre d\'affaires total'), max_digits=12, decimal_places=2, default=0)
    average_order_value = models.DecimalField(_('panier moyen'), max_digits=10, decimal_places=2, default=0)
    
    # Métriques utilisateur
    new_customers = models.PositiveIntegerField(_('nouveaux clients'), default=0)
    returning_customers = models.PositiveIntegerField(_('clients de retour'), default=0)
    
    # Métriques produit
    total_products_sold = models.PositiveIntegerField(_('produits vendus'), default=0)
    top_selling_product = models.CharField(_('produit le plus vendu'), max_length=200, blank=True)
    
    # Métriques de conversion
    conversion_rate = models.FloatField(_('taux de conversion'), default=0.0)
    cart_abandonment_rate = models.FloatField(_('taux d\'abandon de panier'), default=0.0)
    
    created_at = models.DateTimeField(_('créé le'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('Rapport de ventes')
        verbose_name_plural = _('Rapports de ventes')
        ordering = ['-created_at']
        unique_together = ['report_type', 'period_start', 'period_end']
    
    def __str__(self):
        return f"Rapport {self.get_report_type_display()} - {self.period_start} à {self.period_end}"

