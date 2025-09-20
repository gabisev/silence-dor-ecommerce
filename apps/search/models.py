from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

User = get_user_model()


class SearchIndex(models.Model):
    """Index de recherche pour les produits"""
    
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    
    # Contenu indexé
    title = models.CharField(_('titre'), max_length=200)
    description = models.TextField(_('description'))
    keywords = models.TextField(_('mots-clés'), blank=True)
    category = models.CharField(_('catégorie'), max_length=100, blank=True)
    brand = models.CharField(_('marque'), max_length=100, blank=True)
    tags = models.TextField(_('tags'), blank=True)
    
    # Métadonnées
    price = models.DecimalField(_('prix'), max_digits=10, decimal_places=2, null=True, blank=True)
    is_active = models.BooleanField(_('actif'), default=True)
    popularity_score = models.FloatField(_('score de popularité'), default=0.0)
    
    # Dates
    created_at = models.DateTimeField(_('créé le'), auto_now_add=True)
    updated_at = models.DateTimeField(_('modifié le'), auto_now=True)
    
    class Meta:
        verbose_name = _('Index de recherche')
        verbose_name_plural = _('Index de recherche')
        unique_together = ['content_type', 'object_id']
        indexes = [
            models.Index(fields=['title']),
            models.Index(fields=['category']),
            models.Index(fields=['brand']),
            models.Index(fields=['is_active', 'popularity_score']),
        ]
    
    def __str__(self):
        return f"{self.title} ({self.content_type.model})"


class SearchSuggestion(models.Model):
    """Suggestions de recherche populaires"""
    
    query = models.CharField(_('requête'), max_length=200, unique=True)
    count = models.PositiveIntegerField(_('nombre d\'utilisations'), default=1)
    last_used = models.DateTimeField(_('dernière utilisation'), auto_now=True)
    is_active = models.BooleanField(_('actif'), default=True)
    
    class Meta:
        verbose_name = _('Suggestion de recherche')
        verbose_name_plural = _('Suggestions de recherche')
        ordering = ['-count', '-last_used']
    
    def __str__(self):
        return f"{self.query} ({self.count} utilisations)"


class SearchFilter(models.Model):
    """Filtres de recherche disponibles"""
    
    FILTER_TYPES = [
        ('category', _('Catégorie')),
        ('brand', _('Marque')),
        ('price_range', _('Gamme de prix')),
        ('rating', _('Note')),
        ('availability', _('Disponibilité')),
        ('color', _('Couleur')),
        ('size', _('Taille')),
        ('material', _('Matériau')),
    ]
    
    name = models.CharField(_('nom'), max_length=100)
    filter_type = models.CharField(_('type de filtre'), max_length=20, choices=FILTER_TYPES)
    field_name = models.CharField(_('nom du champ'), max_length=100)
    display_name = models.CharField(_('nom d\'affichage'), max_length=100)
    is_active = models.BooleanField(_('actif'), default=True)
    order = models.PositiveIntegerField(_('ordre'), default=0)
    
    class Meta:
        verbose_name = _('Filtre de recherche')
        verbose_name_plural = _('Filtres de recherche')
        ordering = ['order', 'name']
    
    def __str__(self):
        return f"{self.display_name} ({self.get_filter_type_display()})"


class SearchHistory(models.Model):
    """Historique des recherches utilisateur"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    session_key = models.CharField(_('clé de session'), max_length=40, blank=True)
    query = models.CharField(_('requête'), max_length=200)
    filters = models.JSONField(_('filtres appliqués'), default=dict, blank=True)
    results_count = models.PositiveIntegerField(_('nombre de résultats'), default=0)
    timestamp = models.DateTimeField(_('horodatage'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('Historique de recherche')
        verbose_name_plural = _('Historiques de recherche')
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.query} - {self.timestamp}"


class SearchAnalytics(models.Model):
    """Analytics des recherches"""
    
    query = models.CharField(_('requête'), max_length=200)
    results_count = models.PositiveIntegerField(_('nombre de résultats'), default=0)
    click_through_rate = models.FloatField(_('taux de clic'), default=0.0)
    conversion_rate = models.FloatField(_('taux de conversion'), default=0.0)
    date = models.DateField(_('date'))
    
    class Meta:
        verbose_name = _('Analytics de recherche')
        verbose_name_plural = _('Analytics de recherche')
        unique_together = ['query', 'date']
        ordering = ['-date', '-results_count']
    
    def __str__(self):
        return f"{self.query} - {self.date}"

