from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError

class SiteInformation(models.Model):
    """Modèle pour gérer les informations générales du site"""
    
    # Informations de base
    site_name = models.CharField(
        _('nom du site'), 
        max_length=100, 
        default='Silence d\'Or',
        help_text=_('Nom officiel du site e-commerce')
    )
    
    site_tagline = models.CharField(
        _('slogan'), 
        max_length=200, 
        default='Votre boutique de luxe en ligne',
        help_text=_('Slogan ou description courte du site')
    )
    
    site_description = models.TextField(
        _('description du site'), 
        default='Découvrez notre sélection exclusive de produits de qualité pour tous vos besoins.',
        help_text=_('Description détaillée du site pour le SEO')
    )
    
    # Image hero pour la page d'accueil
    hero_image = models.ImageField(
        _('image hero'), 
        upload_to='site_images/',
        blank=True, 
        null=True,
        help_text=_('Image principale de la page d\'accueil (recommandé: 800x400px)')
    )
    
    # Informations de contact
    contact_email = models.EmailField(
        _('email de contact'), 
        default='contact@silence-dor.com',
        help_text=_('Email principal pour les contacts clients')
    )
    
    contact_phone = models.CharField(
        _('téléphone'), 
        max_length=20, 
        default='+33 1 23 45 67 89',
        help_text=_('Numéro de téléphone de contact')
    )
    
    contact_address = models.TextField(
        _('adresse'), 
        default='123 Rue de la Paix\n75001 Paris, France',
        help_text=_('Adresse physique de l\'entreprise')
    )
    
    # Réseaux sociaux
    facebook_url = models.URLField(
        _('Facebook'), 
        blank=True, 
        null=True,
        help_text=_('URL de la page Facebook')
    )
    
    instagram_url = models.URLField(
        _('Instagram'), 
        blank=True, 
        null=True,
        help_text=_('URL du compte Instagram')
    )
    
    twitter_url = models.URLField(
        _('Twitter'), 
        blank=True, 
        null=True,
        help_text=_('URL du compte Twitter')
    )
    
    linkedin_url = models.URLField(
        _('LinkedIn'), 
        blank=True, 
        null=True,
        help_text=_('URL de la page LinkedIn')
    )
    
    # Informations légales
    company_name = models.CharField(
        _('nom de l\'entreprise'), 
        max_length=100, 
        default='Silence d\'Or SARL',
        help_text=_('Nom légal de l\'entreprise')
    )
    
    siret_number = models.CharField(
        _('numéro SIRET'), 
        max_length=14, 
        blank=True,
        help_text=_('Numéro SIRET de l\'entreprise')
    )
    
    vat_number = models.CharField(
        _('numéro TVA'), 
        max_length=20, 
        blank=True,
        help_text=_('Numéro de TVA intracommunautaire')
    )
    
    # Paramètres du site
    currency = models.CharField(
        _('devise'), 
        max_length=3, 
        default='EUR',
        help_text=_('Devise principale du site')
    )
    
    currency_symbol = models.CharField(
        _('symbole de devise'), 
        max_length=5, 
        default='€',
        help_text=_('Symbole de la devise')
    )
    
    # SEO
    meta_keywords = models.TextField(
        _('mots-clés SEO'), 
        blank=True,
        help_text=_('Mots-clés pour le référencement (séparés par des virgules)')
    )
    
    google_analytics_id = models.CharField(
        _('ID Google Analytics'), 
        max_length=20, 
        blank=True,
        help_text=_('Identifiant Google Analytics (ex: GA-XXXXXXXXX)')
    )
    
    # Dates
    created_at = models.DateTimeField(_('créé le'), auto_now_add=True)
    updated_at = models.DateTimeField(_('modifié le'), auto_now=True)
    
    class Meta:
        verbose_name = _('Informations du site')
        verbose_name_plural = _('Informations du site')
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"{self.site_name} - {self.site_tagline}"
    
    def clean(self):
        """Validation personnalisée"""
        super().clean()
        
        # Validation des URLs des réseaux sociaux
        social_urls = [
            ('facebook_url', 'Facebook'),
            ('instagram_url', 'Instagram'),
            ('twitter_url', 'Twitter'),
            ('linkedin_url', 'LinkedIn')
        ]
        
        for field_name, platform in social_urls:
            url = getattr(self, field_name)
            if url:
                validator = URLValidator()
                try:
                    validator(url)
                except ValidationError:
                    raise ValidationError({
                        field_name: f'URL {platform} invalide'
                    })
    
    def save(self, *args, **kwargs):
        """Sauvegarde avec validation"""
        self.clean()
        super().save(*args, **kwargs)
    
    @classmethod
    def get_site_info(cls):
        """Récupère les informations du site (singleton)"""
        site_info, created = cls.objects.get_or_create(
            pk=1,
            defaults={
                'site_name': 'Silence d\'Or',
                'site_tagline': 'Votre boutique de luxe en ligne',
                'site_description': 'Découvrez notre sélection exclusive de produits de qualité pour tous vos besoins.',
                'contact_email': 'contact@silence-dor.com',
                'contact_phone': '+33 1 23 45 67 89',
                'contact_address': '123 Rue de la Paix\n75001 Paris, France',
                'company_name': 'Silence d\'Or SARL',
                'currency': 'EUR',
                'currency_symbol': '€'
            }
        )
        return site_info
