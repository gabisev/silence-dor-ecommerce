from rest_framework import serializers
from .models import Cart, CartItem, Wishlist, WishlistItem
from apps.products.serializers import ProductListSerializer


class CartItemSerializer(serializers.ModelSerializer):
    """Sérialiseur pour les articles du panier"""
    
    product = ProductListSerializer(read_only=True)
    product_id = serializers.IntegerField(write_only=True)
    total_price = serializers.ReadOnlyField()
    
    class Meta:
        model = CartItem
        fields = (
            'id', 'product', 'product_id', 'quantity', 
            'total_price', 'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'created_at', 'updated_at')
    
    def validate_product_id(self, value):
        """Valider que le produit existe et est disponible"""
        from apps.products.models import Product
        
        try:
            product = Product.objects.get(id=value, status='published')
            if not product.is_in_stock:
                raise serializers.ValidationError("Ce produit n'est pas disponible.")
            return value
        except Product.DoesNotExist:
            raise serializers.ValidationError("Produit non trouvé.")


class CartSerializer(serializers.ModelSerializer):
    """Sérialiseur pour le panier"""
    
    items = CartItemSerializer(many=True, read_only=True)
    total_items = serializers.ReadOnlyField()
    total_price = serializers.ReadOnlyField()
    is_empty = serializers.ReadOnlyField()
    
    class Meta:
        model = Cart
        fields = (
            'id', 'items', 'total_items', 'total_price', 
            'is_empty', 'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'created_at', 'updated_at')


class WishlistItemSerializer(serializers.ModelSerializer):
    """Sérialiseur pour les articles de la liste de souhaits"""
    
    product = ProductListSerializer(read_only=True)
    product_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = WishlistItem
        fields = ('id', 'product', 'product_id', 'created_at')
        read_only_fields = ('id', 'created_at')
    
    def validate_product_id(self, value):
        """Valider que le produit existe"""
        from apps.products.models import Product
        
        try:
            Product.objects.get(id=value, status='published')
            return value
        except Product.DoesNotExist:
            raise serializers.ValidationError("Produit non trouvé.")


class WishlistSerializer(serializers.ModelSerializer):
    """Sérialiseur pour la liste de souhaits"""
    
    items = WishlistItemSerializer(many=True, read_only=True)
    total_items = serializers.ReadOnlyField()
    
    class Meta:
        model = Wishlist
        fields = ('id', 'items', 'total_items', 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')

