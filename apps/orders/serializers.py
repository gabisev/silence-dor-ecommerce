from rest_framework import serializers
from .models import Order, OrderItem, OrderStatusHistory, Coupon, OrderCoupon
from apps.products.serializers import ProductListSerializer
from apps.accounts.serializers import AddressSerializer


class OrderItemSerializer(serializers.ModelSerializer):
    """Sérialiseur pour les articles de commande"""
    
    product = ProductListSerializer(read_only=True)
    total_price = serializers.ReadOnlyField()
    
    class Meta:
        model = OrderItem
        fields = (
            'id', 'product', 'quantity', 'unit_price', 
            'total_price', 'created_at'
        )
        read_only_fields = ('id', 'created_at')


class OrderStatusHistorySerializer(serializers.ModelSerializer):
    """Sérialiseur pour l'historique des statuts"""
    
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    
    class Meta:
        model = OrderStatusHistory
        fields = (
            'id', 'status', 'notes', 'created_by', 
            'created_by_name', 'created_at'
        )
        read_only_fields = ('id', 'created_at')


class OrderSerializer(serializers.ModelSerializer):
    """Sérialiseur pour les commandes"""
    
    items = OrderItemSerializer(many=True, read_only=True)
    status_history = OrderStatusHistorySerializer(many=True, read_only=True)
    billing_address = AddressSerializer(read_only=True)
    shipping_address = AddressSerializer(read_only=True)
    total_items = serializers.ReadOnlyField()
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    
    class Meta:
        model = Order
        fields = (
            'id', 'order_number', 'user', 'user_name', 'status', 'payment_status',
            'billing_address', 'shipping_address', 'subtotal', 'tax_amount',
            'shipping_cost', 'discount_amount', 'total_amount', 'payment_method',
            'payment_reference', 'tracking_number', 'shipping_carrier',
            'notes', 'customer_notes', 'items', 'status_history', 'total_items',
            'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'order_number', 'created_at', 'updated_at')


class OrderCreateSerializer(serializers.ModelSerializer):
    """Sérialiseur pour la création de commandes"""
    
    items = OrderItemSerializer(many=True, write_only=True)
    billing_address_id = serializers.IntegerField(write_only=True)
    shipping_address_id = serializers.IntegerField(write_only=True)
    coupon_code = serializers.CharField(write_only=True, required=False, allow_blank=True)
    
    class Meta:
        model = Order
        fields = (
            'billing_address_id', 'shipping_address_id', 'items',
            'coupon_code', 'customer_notes'
        )
    
    def validate_billing_address_id(self, value):
        """Valider l'adresse de facturation"""
        from apps.accounts.models import Address
        
        try:
            address = Address.objects.get(id=value, user=self.context['request'].user)
            return value
        except Address.DoesNotExist:
            raise serializers.ValidationError("Adresse de facturation non trouvée.")
    
    def validate_shipping_address_id(self, value):
        """Valider l'adresse de livraison"""
        from apps.accounts.models import Address
        
        try:
            address = Address.objects.get(id=value, user=self.context['request'].user)
            return value
        except Address.DoesNotExist:
            raise serializers.ValidationError("Adresse de livraison non trouvée.")
    
    def validate_items(self, value):
        """Valider les articles de la commande"""
        if not value:
            raise serializers.ValidationError("La commande doit contenir au moins un article.")
        
        for item in value:
            product = item['product']
            quantity = item['quantity']
            
            # Vérifier la disponibilité
            if not product.is_in_stock:
                raise serializers.ValidationError(f"Le produit {product.name} n'est pas disponible.")
            
            # Vérifier le stock
            if product.track_inventory and quantity > product.quantity:
                raise serializers.ValidationError(
                    f"Quantité demandée ({quantity}) supérieure au stock disponible ({product.quantity}) pour {product.name}."
                )
        
        return value
    
    def create(self, validated_data):
        """Créer une nouvelle commande"""
        from decimal import Decimal
        
        items_data = validated_data.pop('items')
        billing_address_id = validated_data.pop('billing_address_id')
        shipping_address_id = validated_data.pop('shipping_address_id')
        coupon_code = validated_data.pop('coupon_code', '')
        
        # Récupérer les adresses
        from apps.accounts.models import Address
        billing_address = Address.objects.get(id=billing_address_id)
        shipping_address = Address.objects.get(id=shipping_address_id)
        
        # Créer la commande
        order = Order.objects.create(
            user=self.context['request'].user,
            billing_address=billing_address,
            shipping_address=shipping_address,
            **validated_data
        )
        
        # Créer les articles de commande
        subtotal = Decimal('0')
        for item_data in items_data:
            product = item_data['product']
            quantity = item_data['quantity']
            unit_price = product.price
            
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=quantity,
                unit_price=unit_price
            )
            
            subtotal += unit_price * quantity
        
        # Appliquer le coupon si fourni
        discount_amount = Decimal('0')
        if coupon_code:
            try:
                coupon = Coupon.objects.get(code=coupon_code, is_active=True)
                if coupon.is_valid():
                    discount_amount = coupon.calculate_discount(subtotal)
                    if discount_amount > 0:
                        OrderCoupon.objects.create(
                            order=order,
                            coupon=coupon,
                            discount_amount=discount_amount
                        )
                        coupon.used_count += 1
                        coupon.save()
            except Coupon.DoesNotExist:
                pass  # Coupon invalide, ignorer
        
        # Calculer les totaux
        order.subtotal = subtotal
        order.discount_amount = discount_amount
        order.tax_amount = subtotal * Decimal('0.20')  # 20% de TVA
        order.shipping_cost = Decimal('0')  # Livraison gratuite par défaut
        order.total_amount = order.subtotal + order.tax_amount + order.shipping_cost - order.discount_amount
        order.save()
        
        # Créer l'historique de statut
        OrderStatusHistory.objects.create(
            order=order,
            status='pending',
            notes='Commande créée'
        )
        
        return order


class CouponSerializer(serializers.ModelSerializer):
    """Sérialiseur pour les coupons"""
    
    is_valid = serializers.SerializerMethodField()
    
    class Meta:
        model = Coupon
        fields = (
            'id', 'code', 'description', 'type', 'value',
            'minimum_amount', 'maximum_discount', 'usage_limit',
            'used_count', 'valid_from', 'valid_until', 'is_active',
            'is_valid', 'created_at'
        )
        read_only_fields = ('id', 'used_count', 'created_at')
    
    def get_is_valid(self, obj):
        return obj.is_valid()


class OrderCouponSerializer(serializers.ModelSerializer):
    """Sérialiseur pour les coupons appliqués aux commandes"""
    
    coupon = CouponSerializer(read_only=True)
    
    class Meta:
        model = OrderCoupon
        fields = ('id', 'coupon', 'discount_amount', 'created_at')
        read_only_fields = ('id', 'created_at')

