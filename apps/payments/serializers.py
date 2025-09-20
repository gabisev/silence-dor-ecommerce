from rest_framework import serializers
from .models import Payment, Refund, PaymentMethod


class PaymentMethodSerializer(serializers.ModelSerializer):
    """Sérialiseur pour les méthodes de paiement"""
    
    class Meta:
        model = PaymentMethod
        fields = (
            'id', 'type', 'is_default', 'card_last_four', 
            'card_brand', 'card_exp_month', 'card_exp_year', 'created_at'
        )
        read_only_fields = ('id', 'created_at')


class PaymentSerializer(serializers.ModelSerializer):
    """Sérialiseur pour les paiements"""
    
    order_number = serializers.CharField(source='order.order_number', read_only=True)
    
    class Meta:
        model = Payment
        fields = (
            'id', 'order', 'order_number', 'amount', 'currency', 
            'method', 'status', 'external_id', 'transaction_id',
            'card_last_four', 'card_brand', 'failure_reason',
            'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'created_at', 'updated_at')


class RefundSerializer(serializers.ModelSerializer):
    """Sérialiseur pour les remboursements"""
    
    order_number = serializers.CharField(source='order.order_number', read_only=True)
    payment_external_id = serializers.CharField(source='payment.external_id', read_only=True)
    
    class Meta:
        model = Refund
        fields = (
            'id', 'payment', 'order', 'order_number', 'payment_external_id',
            'amount', 'currency', 'status', 'external_id', 'reason', 
            'notes', 'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'created_at', 'updated_at')


class CreatePaymentSerializer(serializers.Serializer):
    """Sérialiseur pour créer un paiement"""
    
    order_id = serializers.IntegerField()
    payment_method_id = serializers.IntegerField(required=False)
    save_payment_method = serializers.BooleanField(default=False)
    
    def validate_order_id(self, value):
        """Valider que la commande existe et appartient à l'utilisateur"""
        from apps.orders.models import Order
        
        try:
            order = Order.objects.get(id=value, user=self.context['request'].user)
            if order.payment_status == 'paid':
                raise serializers.ValidationError("Cette commande est déjà payée.")
            return value
        except Order.DoesNotExist:
            raise serializers.ValidationError("Commande non trouvée.")
    
    def validate_payment_method_id(self, value):
        """Valider que la méthode de paiement existe et appartient à l'utilisateur"""
        if value:
            try:
                PaymentMethod.objects.get(id=value, user=self.context['request'].user)
                return value
            except PaymentMethod.DoesNotExist:
                raise serializers.ValidationError("Méthode de paiement non trouvée.")


class CreateRefundSerializer(serializers.Serializer):
    """Sérialiseur pour créer un remboursement"""
    
    payment_id = serializers.IntegerField()
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    reason = serializers.CharField(max_length=500, required=False, allow_blank=True)
    
    def validate_payment_id(self, value):
        """Valider que le paiement existe et appartient à l'utilisateur"""
        try:
            payment = Payment.objects.get(id=value, user=self.context['request'].user)
            if payment.status != 'succeeded':
                raise serializers.ValidationError("Seuls les paiements réussis peuvent être remboursés.")
            return value
        except Payment.DoesNotExist:
            raise serializers.ValidationError("Paiement non trouvé.")
    
    def validate_amount(self, value):
        """Valider le montant du remboursement"""
        if value <= 0:
            raise serializers.ValidationError("Le montant du remboursement doit être positif.")
        return value

