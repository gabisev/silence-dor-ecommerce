from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.text import slugify
from apps.accounts.models import User


class Category(models.Model):
    """Catégories de produits"""
    
    name = models.CharField(_('name'), max_length=100, unique=True)
    slug = models.SlugField(_('slug'), max_length=100, unique=True, blank=True)
    description = models.TextField(_('description'), blank=True)
    image = models.ImageField(_('image'), upload_to='categories/', blank=True, null=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    is_active = models.BooleanField(_('is active'), default=True)
    sort_order = models.PositiveIntegerField(_('sort order'), default=0)
    
    # Métadonnées
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('Category')
        verbose_name_plural = _('Categories')
        db_table = 'categories'
        ordering = ['sort_order', 'name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    @property
    def full_path(self):
        """Retourne le chemin complet de la catégorie"""
        if self.parent:
            return f"{self.parent.full_path} > {self.name}"
        return self.name


class Brand(models.Model):
    """Marques de produits"""
    
    name = models.CharField(_('name'), max_length=100, unique=True)
    slug = models.SlugField(_('slug'), max_length=100, unique=True, blank=True)
    description = models.TextField(_('description'), blank=True)
    logo = models.ImageField(_('logo'), upload_to='brands/', blank=True, null=True)
    website = models.URLField(_('website'), blank=True)
    is_active = models.BooleanField(_('is active'), default=True)
    
    # Métadonnées
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('Brand')
        verbose_name_plural = _('Brands')
        db_table = 'brands'
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Product(models.Model):
    """Produits du catalogue"""
    
    STATUS_CHOICES = [
        ('draft', _('Draft')),
        ('published', _('Published')),
        ('archived', _('Archived')),
    ]
    
    # Informations de base
    name = models.CharField(_('name'), max_length=200)
    slug = models.SlugField(_('slug'), max_length=200, unique=True, blank=True)
    description = models.TextField(_('description'))
    short_description = models.TextField(_('short description'), max_length=500, blank=True)
    sku = models.CharField(_('SKU'), max_length=100, unique=True)
    
    # Relations
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True, blank=True, related_name='products')
    vendor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='products', null=True, blank=True)
    
    # Prix et stock
    price = models.DecimalField(_('price'), max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    compare_price = models.DecimalField(_('compare price'), max_digits=10, decimal_places=2, null=True, blank=True, validators=[MinValueValidator(0)])
    cost_price = models.DecimalField(_('cost price'), max_digits=10, decimal_places=2, null=True, blank=True, validators=[MinValueValidator(0)])
    
    # Stock
    track_inventory = models.BooleanField(_('track inventory'), default=True)
    quantity = models.PositiveIntegerField(_('quantity'), default=0)
    low_stock_threshold = models.PositiveIntegerField(_('low stock threshold'), default=5)
    
    # Statut et visibilité
    status = models.CharField(_('status'), max_length=20, choices=STATUS_CHOICES, default='draft')
    is_featured = models.BooleanField(_('is featured'), default=False)
    is_digital = models.BooleanField(_('is digital'), default=False)
    
    # Poids et dimensions (pour l'expédition)
    weight = models.DecimalField(_('weight'), max_digits=8, decimal_places=2, null=True, blank=True, validators=[MinValueValidator(0)])
    length = models.DecimalField(_('length'), max_digits=8, decimal_places=2, null=True, blank=True, validators=[MinValueValidator(0)])
    width = models.DecimalField(_('width'), max_digits=8, decimal_places=2, null=True, blank=True, validators=[MinValueValidator(0)])
    height = models.DecimalField(_('height'), max_digits=8, decimal_places=2, null=True, blank=True, validators=[MinValueValidator(0)])
    
    # SEO
    meta_title = models.CharField(_('meta title'), max_length=200, blank=True)
    meta_description = models.TextField(_('meta description'), max_length=500, blank=True)
    
    # Métadonnées
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('Product')
        verbose_name_plural = _('Products')
        db_table = 'products'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'is_featured']),
            models.Index(fields=['category', 'status']),
            models.Index(fields=['price']),
        ]
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    @property
    def is_in_stock(self):
        """Vérifie si le produit est en stock"""
        if not self.track_inventory:
            return True
        return self.quantity > 0
    
    @property
    def is_low_stock(self):
        """Vérifie si le stock est faible"""
        if not self.track_inventory:
            return False
        return self.quantity <= self.low_stock_threshold
    
    @property
    def discount_percentage(self):
        """Calcule le pourcentage de remise"""
        if self.compare_price and self.compare_price > self.price:
            return round(((self.compare_price - self.price) / self.compare_price) * 100, 2)
        return 0


class ProductImage(models.Model):
    """Images des produits"""
    
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(_('image'), upload_to='products/')
    alt_text = models.CharField(_('alt text'), max_length=200, blank=True)
    is_primary = models.BooleanField(_('is primary'), default=False)
    sort_order = models.PositiveIntegerField(_('sort order'), default=0)
    
    # Métadonnées
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('Product Image')
        verbose_name_plural = _('Product Images')
        db_table = 'product_images'
        ordering = ['sort_order', 'created_at']
    
    def __str__(self):
        return f"{self.product.name} - Image {self.sort_order}"
    
    def save(self, *args, **kwargs):
        # S'assurer qu'une seule image est marquée comme primaire
        if self.is_primary:
            ProductImage.objects.filter(
                product=self.product, 
                is_primary=True
            ).exclude(pk=self.pk).update(is_primary=False)
        super().save(*args, **kwargs)


class ProductAttribute(models.Model):
    """Attributs des produits (couleur, taille, etc.)"""
    
    name = models.CharField(_('name'), max_length=100, unique=True)
    slug = models.SlugField(_('slug'), max_length=100, unique=True, blank=True)
    type = models.CharField(_('type'), max_length=20, choices=[
        ('text', _('Text')),
        ('number', _('Number')),
        ('select', _('Select')),
        ('multiselect', _('Multi Select')),
        ('boolean', _('Boolean')),
    ], default='text')
    is_required = models.BooleanField(_('is required'), default=False)
    is_filterable = models.BooleanField(_('is filterable'), default=False)
    
    class Meta:
        verbose_name = _('Product Attribute')
        verbose_name_plural = _('Product Attributes')
        db_table = 'product_attributes'
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class ProductAttributeValue(models.Model):
    """Valeurs des attributs de produits"""
    
    attribute = models.ForeignKey(ProductAttribute, on_delete=models.CASCADE, related_name='values')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='attribute_values')
    value = models.TextField(_('value'))
    
    class Meta:
        verbose_name = _('Product Attribute Value')
        verbose_name_plural = _('Product Attribute Values')
        db_table = 'product_attribute_values'
        unique_together = ['attribute', 'product']
    
    def __str__(self):
        return f"{self.product.name} - {self.attribute.name}: {self.value}"


class ProductReview(models.Model):
    """Avis sur les produits"""
    
    RATING_CHOICES = [
        (1, _('1 Star')),
        (2, _('2 Stars')),
        (3, _('3 Stars')),
        (4, _('4 Stars')),
        (5, _('5 Stars')),
    ]
    
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveIntegerField(_('rating'), choices=RATING_CHOICES)
    title = models.CharField(_('title'), max_length=200)
    comment = models.TextField(_('comment'))
    is_verified_purchase = models.BooleanField(_('is verified purchase'), default=False)
    is_approved = models.BooleanField(_('is approved'), default=False)
    
    # Métadonnées
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('Product Review')
        verbose_name_plural = _('Product Reviews')
        db_table = 'product_reviews'
        ordering = ['-created_at']
        unique_together = ['product', 'user']
    
    def __str__(self):
        return f"{self.product.name} - {self.user.get_full_name()} ({self.rating}★)"

