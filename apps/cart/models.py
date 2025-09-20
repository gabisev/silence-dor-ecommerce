from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator
from apps.accounts.models import User
from apps.products.models import Product


class Cart(models.Model):
    """Panier d'achat"""
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart', null=True, blank=True)
    session_key = models.CharField(_('session key'), max_length=40, null=True, blank=True)
    
    # Métadonnées
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('Cart')
        verbose_name_plural = _('Carts')
        db_table = 'carts'
    
    def __str__(self):
        if self.user:
            return f"Panier de {self.user.get_full_name()}"
        return f"Panier session {self.session_key}"
    
    @property
    def total_items(self):
        """Nombre total d'articles dans le panier"""
        return sum(item.quantity for item in self.items.all())
    
    @property
    def total_price(self):
        """Prix total du panier"""
        return sum(item.total_price for item in self.items.all())
    
    @property
    def is_empty(self):
        """Vérifie si le panier est vide"""
        return self.items.count() == 0


class CartItem(models.Model):
    """Articles dans le panier"""
    
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(_('quantity'), default=1, validators=[MinValueValidator(1)])
    
    # Métadonnées
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('Cart Item')
        verbose_name_plural = _('Cart Items')
        db_table = 'cart_items'
        unique_together = ['cart', 'product']
    
    def __str__(self):
        return f"{self.product.name} x{self.quantity}"
    
    @property
    def total_price(self):
        """Prix total pour cet article"""
        return self.product.price * self.quantity
    
    def clean(self):
        """Validation personnalisée"""
        from django.core.exceptions import ValidationError
        
        # Vérifier que le produit est disponible
        if not self.product.is_in_stock:
            raise ValidationError(_('Ce produit n\'est pas disponible.'))
        
        # Vérifier la quantité en stock
        if self.product.track_inventory and self.quantity > self.product.quantity:
            raise ValidationError(
                _('Quantité demandée ({}) supérieure au stock disponible ({}).').format(
                    self.quantity, self.product.quantity
                )
            )


class Wishlist(models.Model):
    """Liste de souhaits"""
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='wishlist')
    
    # Métadonnées
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('Wishlist')
        verbose_name_plural = _('Wishlists')
        db_table = 'wishlists'
    
    def __str__(self):
        return f"Liste de souhaits de {self.user.get_full_name()}"
    
    @property
    def total_items(self):
        """Nombre total d'articles dans la liste de souhaits"""
        return self.items.count()


class WishlistItem(models.Model):
    """Articles dans la liste de souhaits"""
    
    wishlist = models.ForeignKey(Wishlist, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    
    # Métadonnées
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('Wishlist Item')
        verbose_name_plural = _('Wishlist Items')
        db_table = 'wishlist_items'
        unique_together = ['wishlist', 'product']
    
    def __str__(self):
        return f"{self.product.name} dans la liste de souhaits de {self.wishlist.user.get_full_name()}"

