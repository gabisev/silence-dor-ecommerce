from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator
from decimal import Decimal
from apps.accounts.models import User, Address
from apps.products.models import Product


class Order(models.Model):
    """Commandes"""
    
    STATUS_CHOICES = [
        ('pending', _('Pending')),
        ('confirmed', _('Confirmed')),
        ('processing', _('Processing')),
        ('shipped', _('Shipped')),
        ('delivered', _('Delivered')),
        ('cancelled', _('Cancelled')),
        ('refunded', _('Refunded')),
    ]
    
    PAYMENT_STATUS_CHOICES = [
        ('pending', _('Pending')),
        ('paid', _('Paid')),
        ('failed', _('Failed')),
        ('refunded', _('Refunded')),
    ]
    
    # Informations de base
    order_number = models.CharField(_('order number'), max_length=20, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    
    # Statuts
    status = models.CharField(_('status'), max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_status = models.CharField(_('payment status'), max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    
    # Adresses
    billing_address = models.ForeignKey(
        Address, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='billing_orders'
    )
    shipping_address = models.ForeignKey(
        Address, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='shipping_orders'
    )
    
    # Prix
    subtotal = models.DecimalField(_('subtotal'), max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    tax_amount = models.DecimalField(_('tax amount'), max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    shipping_cost = models.DecimalField(_('shipping cost'), max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    discount_amount = models.DecimalField(_('discount amount'), max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    total_amount = models.DecimalField(_('total amount'), max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    
    # Informations de paiement
    payment_method = models.CharField(_('payment method'), max_length=50, blank=True)
    payment_reference = models.CharField(_('payment reference'), max_length=100, blank=True)
    stripe_payment_intent_id = models.CharField(_('stripe payment intent id'), max_length=100, blank=True)
    
    # Informations d'expédition
    tracking_number = models.CharField(_('tracking number'), max_length=100, blank=True)
    shipping_carrier = models.CharField(_('shipping carrier'), max_length=100, blank=True)
    
    # Notes
    notes = models.TextField(_('notes'), blank=True)
    customer_notes = models.TextField(_('customer notes'), blank=True)
    
    # Métadonnées
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('Order')
        verbose_name_plural = _('Orders')
        db_table = 'orders'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['order_number']),
            models.Index(fields=['status', 'payment_status']),
            models.Index(fields=['user', 'created_at']),
        ]
    
    def __str__(self):
        return f"Commande {self.order_number}"
    
    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = self.generate_order_number()
        super().save(*args, **kwargs)
    
    def generate_order_number(self):
        """Générer un numéro de commande unique"""
        import uuid
        return f"SD{str(uuid.uuid4())[:8].upper()}"
    
    @property
    def total_items(self):
        """Nombre total d'articles dans la commande"""
        return sum(item.quantity for item in self.items.all())
    
    def calculate_totals(self):
        """Calculer les totaux de la commande"""
        self.subtotal = sum(item.total_price for item in self.items.all())
        # Calculer la taxe (20% par défaut)
        self.tax_amount = self.subtotal * Decimal('0.20')
        # Calculer le total
        self.total_amount = self.subtotal + self.tax_amount + self.shipping_cost - self.discount_amount


class OrderItem(models.Model):
    """Articles dans une commande"""
    
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(_('quantity'), validators=[MinValueValidator(1)])
    unit_price = models.DecimalField(_('unit price'), max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    
    # Métadonnées
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('Order Item')
        verbose_name_plural = _('Order Items')
        db_table = 'order_items'
        unique_together = ['order', 'product']
    
    def __str__(self):
        return f"{self.product.name} x{self.quantity} - {self.order.order_number}"
    
    @property
    def total_price(self):
        """Prix total pour cet article"""
        return self.unit_price * self.quantity


class OrderStatusHistory(models.Model):
    """Historique des statuts de commande"""
    
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='status_history')
    status = models.CharField(_('status'), max_length=20, choices=Order.STATUS_CHOICES)
    notes = models.TextField(_('notes'), blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Métadonnées
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('Order Status History')
        verbose_name_plural = _('Order Status Histories')
        db_table = 'order_status_history'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.order.order_number} - {self.get_status_display()}"


class Coupon(models.Model):
    """Codes de réduction"""
    
    TYPE_CHOICES = [
        ('percentage', _('Percentage')),
        ('fixed', _('Fixed Amount')),
    ]
    
    code = models.CharField(_('code'), max_length=50, unique=True)
    description = models.TextField(_('description'), blank=True)
    type = models.CharField(_('type'), max_length=20, choices=TYPE_CHOICES, default='percentage')
    value = models.DecimalField(_('value'), max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    minimum_amount = models.DecimalField(_('minimum amount'), max_digits=10, decimal_places=2, null=True, blank=True, validators=[MinValueValidator(0)])
    maximum_discount = models.DecimalField(_('maximum discount'), max_digits=10, decimal_places=2, null=True, blank=True, validators=[MinValueValidator(0)])
    
    # Limites d'utilisation
    usage_limit = models.PositiveIntegerField(_('usage limit'), null=True, blank=True)
    used_count = models.PositiveIntegerField(_('used count'), default=0)
    
    # Dates de validité
    valid_from = models.DateTimeField(_('valid from'))
    valid_until = models.DateTimeField(_('valid until'))
    
    # Statut
    is_active = models.BooleanField(_('is active'), default=True)
    
    # Métadonnées
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('Coupon')
        verbose_name_plural = _('Coupons')
        db_table = 'coupons'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.code} - {self.get_type_display()}"
    
    def is_valid(self):
        """Vérifier si le coupon est valide"""
        from django.utils import timezone
        
        if not self.is_active:
            return False
        
        now = timezone.now()
        if self.valid_from > now or self.valid_until < now:
            return False
        
        if self.usage_limit and self.used_count >= self.usage_limit:
            return False
        
        return True
    
    def calculate_discount(self, order_amount):
        """Calculer le montant de la réduction"""
        if not self.is_valid():
            return Decimal('0')
        
        if self.minimum_amount and order_amount < self.minimum_amount:
            return Decimal('0')
        
        if self.type == 'percentage':
            discount = order_amount * (self.value / 100)
        else:  # fixed
            discount = self.value
        
        if self.maximum_discount and discount > self.maximum_discount:
            discount = self.maximum_discount
        
        return min(discount, order_amount)


class OrderCoupon(models.Model):
    """Coupons appliqués aux commandes"""
    
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='applied_coupons')
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE)
    discount_amount = models.DecimalField(_('discount amount'), max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    
    # Métadonnées
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('Order Coupon')
        verbose_name_plural = _('Order Coupons')
        db_table = 'order_coupons'
        unique_together = ['order', 'coupon']
    
    def __str__(self):
        return f"{self.coupon.code} - {self.order.order_number}"

