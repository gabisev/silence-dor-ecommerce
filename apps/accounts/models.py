from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager):
    """Manager personnalisé pour le modèle User"""
    
    def create_user(self, email, password=None, **extra_fields):
        """Créer un utilisateur normal"""
        if not email:
            raise ValueError('L\'email est obligatoire')
        
        email = self.normalize_email(email)
        # Utiliser l'email comme username si pas fourni
        if 'username' not in extra_fields:
            extra_fields['username'] = email
        
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        """Créer un superutilisateur"""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Le superutilisateur doit avoir is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Le superutilisateur doit avoir is_superuser=True.')
        
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    """Modèle utilisateur personnalisé pour Silence d'Or"""
    
    objects = UserManager()
    
    email = models.EmailField(_('email address'), unique=True)
    phone = models.CharField(_('phone number'), max_length=20, blank=True)
    birth_date = models.DateField(_('birth date'), null=True, blank=True)
    
    # Éviter les conflits avec le modèle User par défaut
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name=_('groups'),
        blank=True,
        help_text=_('The groups this user belongs to.'),
        related_name="custom_user_set",
        related_query_name="custom_user",
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name=_('user permissions'),
        blank=True,
        help_text=_('Specific permissions for this user.'),
        related_name="custom_user_set",
        related_query_name="custom_user",
    )
    address = models.TextField(_('address'), blank=True)
    city = models.CharField(_('city'), max_length=100, blank=True)
    postal_code = models.CharField(_('postal code'), max_length=10, blank=True)
    country = models.CharField(_('country'), max_length=100, default='France')
    
    # Champs pour l'e-commerce
    is_vendor = models.BooleanField(_('is vendor'), default=False)
    company_name = models.CharField(_('company name'), max_length=200, blank=True)
    tax_number = models.CharField(_('tax number'), max_length=50, blank=True)
    
    # Préférences
    newsletter_subscription = models.BooleanField(_('newsletter subscription'), default=True)
    language = models.CharField(_('language'), max_length=5, default='fr')
    
    # Stripe
    stripe_customer_id = models.CharField(_('stripe customer id'), max_length=100, blank=True)
    
    # Métadonnées
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']
    
    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')
        db_table = 'users'
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.email})"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()
    
    def get_full_name(self):
        return self.full_name


class UserProfile(models.Model):
    """Profil étendu pour les utilisateurs"""
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar = models.ImageField(_('avatar'), upload_to='avatars/', blank=True, null=True)
    bio = models.TextField(_('biography'), blank=True)
    
    # Préférences de notification
    email_notifications = models.BooleanField(_('email notifications'), default=True)
    sms_notifications = models.BooleanField(_('SMS notifications'), default=False)
    
    # Métadonnées
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('User Profile')
        verbose_name_plural = _('User Profiles')
        db_table = 'user_profiles'
    
    def __str__(self):
        return f"Profile de {self.user.get_full_name()}"


class Address(models.Model):
    """Adresses des utilisateurs"""
    
    ADDRESS_TYPES = [
        ('billing', _('Billing Address')),
        ('shipping', _('Shipping Address')),
        ('both', _('Both')),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses')
    type = models.CharField(_('address type'), max_length=10, choices=ADDRESS_TYPES)
    is_default = models.BooleanField(_('is default'), default=False)
    
    # Détails de l'adresse
    first_name = models.CharField(_('first name'), max_length=100)
    last_name = models.CharField(_('last name'), max_length=100)
    company = models.CharField(_('company'), max_length=200, blank=True)
    address_line_1 = models.CharField(_('address line 1'), max_length=255)
    address_line_2 = models.CharField(_('address line 2'), max_length=255, blank=True)
    city = models.CharField(_('city'), max_length=100)
    state = models.CharField(_('state/province'), max_length=100, blank=True)
    postal_code = models.CharField(_('postal code'), max_length=20)
    country = models.CharField(_('country'), max_length=100, default='France')
    phone = models.CharField(_('phone'), max_length=20, blank=True)
    
    # Métadonnées
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('Address')
        verbose_name_plural = _('Addresses')
        db_table = 'addresses'
        ordering = ['-is_default', '-created_at']
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.city}, {self.country}"
    
    def save(self, *args, **kwargs):
        # S'assurer qu'une seule adresse par type est marquée comme défaut
        if self.is_default:
            Address.objects.filter(
                user=self.user, 
                type=self.type, 
                is_default=True
            ).exclude(pk=self.pk).update(is_default=False)
        super().save(*args, **kwargs)
