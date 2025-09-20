from django.db import models
from django.utils.translation import gettext_lazy as _


class Language(models.Model):
    """Langues supportées"""
    
    code = models.CharField(_('code'), max_length=5, unique=True)  # ex: 'fr', 'en', 'es'
    name = models.CharField(_('nom'), max_length=100)  # ex: 'Français', 'English'
    native_name = models.CharField(_('nom natif'), max_length=100)  # ex: 'Français', 'English'
    
    # Configuration
    is_active = models.BooleanField(_('actif'), default=True)
    is_default = models.BooleanField(_('langue par défaut'), default=False)
    is_rtl = models.BooleanField(_('écriture de droite à gauche'), default=False)
    
    # Métadonnées
    flag_emoji = models.CharField(_('emoji du drapeau'), max_length=10, blank=True)
    sort_order = models.PositiveIntegerField(_('ordre de tri'), default=0)
    
    created_at = models.DateTimeField(_('créé le'), auto_now_add=True)
    updated_at = models.DateTimeField(_('modifié le'), auto_now=True)
    
    class Meta:
        verbose_name = _('Langue')
        verbose_name_plural = _('Langues')
        ordering = ['sort_order', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.code})"
    
    def save(self, *args, **kwargs):
        # S'assurer qu'il n'y a qu'une seule langue par défaut
        if self.is_default:
            Language.objects.filter(is_default=True).update(is_default=False)
        super().save(*args, **kwargs)


class Currency(models.Model):
    """Devises supportées"""
    
    code = models.CharField(_('code'), max_length=3, unique=True)  # ex: 'EUR', 'USD', 'GBP'
    name = models.CharField(_('nom'), max_length=100)  # ex: 'Euro', 'US Dollar'
    symbol = models.CharField(_('symbole'), max_length=10)  # ex: '€', '$', '£'
    
    # Configuration
    is_active = models.BooleanField(_('actif'), default=True)
    is_default = models.BooleanField(_('devise par défaut'), default=False)
    
    # Taux de change
    exchange_rate = models.DecimalField(_('taux de change'), max_digits=10, decimal_places=6, default=1.0)
    last_updated = models.DateTimeField(_('dernière mise à jour'), auto_now=True)
    
    # Formatage
    decimal_places = models.PositiveIntegerField(_('nombre de décimales'), default=2)
    symbol_position = models.CharField(_('position du symbole'), max_length=10, choices=[
        ('before', _('Avant')),
        ('after', _('Après')),
    ], default='after')
    
    created_at = models.DateTimeField(_('créé le'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('Devise')
        verbose_name_plural = _('Devises')
        ordering = ['code']
    
    def __str__(self):
        return f"{self.name} ({self.code})"
    
    def save(self, *args, **kwargs):
        # S'assurer qu'il n'y a qu'une seule devise par défaut
        if self.is_default:
            Currency.objects.filter(is_default=True).update(is_default=False)
        super().save(*args, **kwargs)
    
    def format_amount(self, amount):
        """Formate un montant selon la devise"""
        if self.symbol_position == 'before':
            return f"{self.symbol}{amount:,.{self.decimal_places}f}"
        else:
            return f"{amount:,.{self.decimal_places}f} {self.symbol}"


class Country(models.Model):
    """Pays supportés"""
    
    code = models.CharField(_('code'), max_length=2, unique=True)  # ISO 3166-1 alpha-2
    name = models.CharField(_('nom'), max_length=100)
    native_name = models.CharField(_('nom natif'), max_length=100)
    
    # Configuration
    is_active = models.BooleanField(_('actif'), default=True)
    is_default = models.BooleanField(_('pays par défaut'), default=False)
    
    # Devise et langue par défaut
    default_currency = models.ForeignKey(Currency, on_delete=models.SET_NULL, null=True, blank=True, related_name='countries')
    default_language = models.ForeignKey(Language, on_delete=models.SET_NULL, null=True, blank=True, related_name='countries')
    
    # Informations géographiques
    continent = models.CharField(_('continent'), max_length=50, blank=True)
    region = models.CharField(_('région'), max_length=100, blank=True)
    
    # Métadonnées
    flag_emoji = models.CharField(_('emoji du drapeau'), max_length=10, blank=True)
    phone_code = models.CharField(_('indicatif téléphonique'), max_length=10, blank=True)
    
    created_at = models.DateTimeField(_('créé le'), auto_now_add=True)
    updated_at = models.DateTimeField(_('modifié le'), auto_now=True)
    
    class Meta:
        verbose_name = _('Pays')
        verbose_name_plural = _('Pays')
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.code})"


class Region(models.Model):
    """Régions/États/Provinces"""
    
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name='regions')
    code = models.CharField(_('code'), max_length=10)
    name = models.CharField(_('nom'), max_length=100)
    
    # Configuration
    is_active = models.BooleanField(_('actif'), default=True)
    
    # Informations fiscales
    tax_rate = models.DecimalField(_('taux de taxe'), max_digits=5, decimal_places=2, default=0.0)
    
    created_at = models.DateTimeField(_('créé le'), auto_now_add=True)
    updated_at = models.DateTimeField(_('modifié le'), auto_now=True)
    
    class Meta:
        verbose_name = _('Région')
        verbose_name_plural = _('Régions')
        unique_together = ['country', 'code']
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name}, {self.country.name}"


class Translation(models.Model):
    """Traductions de contenu"""
    
    CONTENT_TYPES = [
        ('product', _('Produit')),
        ('category', _('Catégorie')),
        ('brand', _('Marque')),
        ('page', _('Page')),
        ('email', _('Email')),
        ('notification', _('Notification')),
    ]
    
    language = models.ForeignKey(Language, on_delete=models.CASCADE, related_name='translations')
    content_type = models.CharField(_('type de contenu'), max_length=20, choices=CONTENT_TYPES)
    object_id = models.PositiveIntegerField(_('ID de l\'objet'))
    
    # Champs traduits
    field_name = models.CharField(_('nom du champ'), max_length=100)
    original_text = models.TextField(_('texte original'))
    translated_text = models.TextField(_('texte traduit'))
    
    # Statut
    is_approved = models.BooleanField(_('approuvé'), default=False)
    is_auto_translated = models.BooleanField(_('traduit automatiquement'), default=False)
    
    # Métadonnées
    translator = models.CharField(_('traducteur'), max_length=100, blank=True)
    translation_service = models.CharField(_('service de traduction'), max_length=100, blank=True)
    
    created_at = models.DateTimeField(_('créé le'), auto_now_add=True)
    updated_at = models.DateTimeField(_('modifié le'), auto_now=True)
    
    class Meta:
        verbose_name = _('Traduction')
        verbose_name_plural = _('Traductions')
        unique_together = ['language', 'content_type', 'object_id', 'field_name']
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"{self.language.name} - {self.get_content_type_display()} - {self.field_name}"


class LocalizedContent(models.Model):
    """Contenu localisé"""
    
    language = models.ForeignKey(Language, on_delete=models.CASCADE, related_name='localized_content')
    content_type = models.CharField(_('type de contenu'), max_length=20, choices=Translation.CONTENT_TYPES)
    object_id = models.PositiveIntegerField(_('ID de l\'objet'))
    
    # Contenu localisé
    title = models.CharField(_('titre'), max_length=200, blank=True)
    description = models.TextField(_('description'), blank=True)
    content = models.TextField(_('contenu'), blank=True)
    
    # Métadonnées SEO
    meta_title = models.CharField(_('titre SEO'), max_length=200, blank=True)
    meta_description = models.TextField(_('description SEO'), blank=True)
    meta_keywords = models.CharField(_('mots-clés SEO'), max_length=500, blank=True)
    
    # Statut
    is_published = models.BooleanField(_('publié'), default=True)
    
    created_at = models.DateTimeField(_('créé le'), auto_now_add=True)
    updated_at = models.DateTimeField(_('modifié le'), auto_now=True)
    
    class Meta:
        verbose_name = _('Contenu localisé')
        verbose_name_plural = _('Contenus localisés')
        unique_together = ['language', 'content_type', 'object_id']
        ordering = ['language', 'content_type']
    
    def __str__(self):
        return f"{self.language.name} - {self.get_content_type_display()} - {self.title}"


class TaxRule(models.Model):
    """Règles de taxation"""
    
    name = models.CharField(_('nom'), max_length=200)
    description = models.TextField(_('description'), blank=True)
    
    # Ciblage
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name='tax_rules', null=True, blank=True)
    region = models.ForeignKey(Region, on_delete=models.CASCADE, related_name='tax_rules', null=True, blank=True)
    
    # Produits concernés
    applicable_products = models.ManyToManyField('products.Product', blank=True, related_name='tax_rules', verbose_name=_('produits applicables'))
    applicable_categories = models.ManyToManyField('products.Category', blank=True, related_name='tax_rules', verbose_name=_('catégories applicables'))
    
    # Taux de taxe
    tax_rate = models.DecimalField(_('taux de taxe'), max_digits=5, decimal_places=2)
    tax_type = models.CharField(_('type de taxe'), max_length=20, choices=[
        ('vat', _('TVA')),
        ('sales_tax', _('Taxe de vente')),
        ('gst', _('GST')),
        ('other', _('Autre')),
    ], default='vat')
    
    # Configuration
    is_active = models.BooleanField(_('actif'), default=True)
    priority = models.PositiveIntegerField(_('priorité'), default=0)
    
    created_at = models.DateTimeField(_('créé le'), auto_now_add=True)
    updated_at = models.DateTimeField(_('modifié le'), auto_now=True)
    
    class Meta:
        verbose_name = _('Règle de taxation')
        verbose_name_plural = _('Règles de taxation')
        ordering = ['-priority', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.tax_rate}%)"


class ShippingZone(models.Model):
    """Zones de livraison"""
    
    name = models.CharField(_('nom'), max_length=200)
    description = models.TextField(_('description'), blank=True)
    
    # Pays inclus
    countries = models.ManyToManyField(Country, related_name='shipping_zones', verbose_name=_('pays'))
    
    # Configuration
    is_active = models.BooleanField(_('actif'), default=True)
    is_default = models.BooleanField(_('zone par défaut'), default=False)
    
    created_at = models.DateTimeField(_('créé le'), auto_now_add=True)
    updated_at = models.DateTimeField(_('modifié le'), auto_now=True)
    
    class Meta:
        verbose_name = _('Zone de livraison')
        verbose_name_plural = _('Zones de livraison')
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        # S'assurer qu'il n'y a qu'une seule zone par défaut
        if self.is_default:
            ShippingZone.objects.filter(is_default=True).update(is_default=False)
        super().save(*args, **kwargs)


class ShippingMethod(models.Model):
    """Méthodes de livraison"""
    
    METHOD_TYPES = [
        ('standard', _('Standard')),
        ('express', _('Express')),
        ('overnight', _('Livraison du jour au lendemain')),
        ('pickup', _('Retrait en magasin')),
        ('digital', _('Livraison numérique')),
    ]
    
    name = models.CharField(_('nom'), max_length=200)
    description = models.TextField(_('description'), blank=True)
    method_type = models.CharField(_('type de méthode'), max_length=20, choices=METHOD_TYPES, default='standard')
    
    # Zone de livraison
    shipping_zone = models.ForeignKey(ShippingZone, on_delete=models.CASCADE, related_name='shipping_methods')
    
    # Coûts
    base_cost = models.DecimalField(_('coût de base'), max_digits=10, decimal_places=2, default=0)
    cost_per_kg = models.DecimalField(_('coût par kg'), max_digits=10, decimal_places=2, default=0)
    free_shipping_threshold = models.DecimalField(_('seuil de livraison gratuite'), max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Délais
    min_delivery_days = models.PositiveIntegerField(_('délai minimum (jours)'), default=1)
    max_delivery_days = models.PositiveIntegerField(_('délai maximum (jours)'), default=7)
    
    # Configuration
    is_active = models.BooleanField(_('actif'), default=True)
    is_default = models.BooleanField(_('méthode par défaut'), default=False)
    
    created_at = models.DateTimeField(_('créé le'), auto_now_add=True)
    updated_at = models.DateTimeField(_('modifié le'), auto_now=True)
    
    class Meta:
        verbose_name = _('Méthode de livraison')
        verbose_name_plural = _('Méthodes de livraison')
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} - {self.shipping_zone.name}"
    
    def calculate_cost(self, weight=None, order_value=None):
        """Calcule le coût de livraison"""
        cost = self.base_cost
        
        # Ajouter le coût par poids
        if weight and self.cost_per_kg:
            cost += weight * self.cost_per_kg
        
        # Livraison gratuite si le seuil est atteint
        if order_value and self.free_shipping_threshold and order_value >= self.free_shipping_threshold:
            cost = 0
        
        return cost

