from django.db import models
from django.utils.translation import gettext_lazy as _
from decimal import Decimal
from apps.accounts.models import User
from apps.orders.models import Order


class Payment(models.Model):
    """Paiements"""
    
    STATUS_CHOICES = [
        ('pending', _('Pending')),
        ('processing', _('Processing')),
        ('succeeded', _('Succeeded')),
        ('failed', _('Failed')),
        ('cancelled', _('Cancelled')),
        ('refunded', _('Refunded')),
    ]
    
    METHOD_CHOICES = [
        ('card', _('Credit Card')),
        ('bank_transfer', _('Bank Transfer')),
        ('paypal', _('PayPal')),
        ('stripe', _('Stripe')),
        ('cash_on_delivery', _('Cash on Delivery')),
    ]
    
    # Informations de base
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='payments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments')
    
    # Détails du paiement
    amount = models.DecimalField(_('amount'), max_digits=10, decimal_places=2)
    currency = models.CharField(_('currency'), max_length=3, default='EUR')
    method = models.CharField(_('method'), max_length=20, choices=METHOD_CHOICES)
    status = models.CharField(_('status'), max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Références externes
    external_id = models.CharField(_('external id'), max_length=100, blank=True)
    transaction_id = models.CharField(_('transaction id'), max_length=100, blank=True)
    
    # Informations Stripe
    stripe_payment_intent_id = models.CharField(_('stripe payment intent id'), max_length=100, blank=True)
    stripe_charge_id = models.CharField(_('stripe charge id'), max_length=100, blank=True)
    
    # Détails de la carte (chiffrés)
    card_last_four = models.CharField(_('card last four'), max_length=4, blank=True)
    card_brand = models.CharField(_('card brand'), max_length=20, blank=True)
    card_exp_month = models.PositiveIntegerField(_('card exp month'), null=True, blank=True)
    card_exp_year = models.PositiveIntegerField(_('card exp year'), null=True, blank=True)
    
    # Métadonnées
    failure_reason = models.TextField(_('failure reason'), blank=True)
    metadata = models.JSONField(_('metadata'), default=dict, blank=True)
    
    # Métadonnées
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('Payment')
        verbose_name_plural = _('Payments')
        db_table = 'payments'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['external_id']),
            models.Index(fields=['stripe_payment_intent_id']),
        ]
    
    def __str__(self):
        return f"Paiement {self.external_id or self.id} - {self.order.order_number}"


class Refund(models.Model):
    """Remboursements"""
    
    STATUS_CHOICES = [
        ('pending', _('Pending')),
        ('succeeded', _('Succeeded')),
        ('failed', _('Failed')),
        ('cancelled', _('Cancelled')),
    ]
    
    # Informations de base
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name='refunds')
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='refunds')
    
    # Détails du remboursement
    amount = models.DecimalField(_('amount'), max_digits=10, decimal_places=2)
    currency = models.CharField(_('currency'), max_length=3, default='EUR')
    status = models.CharField(_('status'), max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Références externes
    external_id = models.CharField(_('external id'), max_length=100, blank=True)
    stripe_refund_id = models.CharField(_('stripe refund id'), max_length=100, blank=True)
    
    # Raison du remboursement
    reason = models.TextField(_('reason'), blank=True)
    notes = models.TextField(_('notes'), blank=True)
    
    # Métadonnées
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('Refund')
        verbose_name_plural = _('Refunds')
        db_table = 'refunds'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Remboursement {self.external_id or self.id} - {self.payment.external_id}"


class PaymentMethod(models.Model):
    """Méthodes de paiement sauvegardées"""
    
    TYPE_CHOICES = [
        ('card', _('Credit Card')),
        ('bank_account', _('Bank Account')),
        ('paypal', _('PayPal')),
    ]
    
    # Informations de base
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payment_methods')
    type = models.CharField(_('type'), max_length=20, choices=TYPE_CHOICES)
    is_default = models.BooleanField(_('is default'), default=False)
    
    # Références externes
    external_id = models.CharField(_('external id'), max_length=100)
    stripe_payment_method_id = models.CharField(_('stripe payment method id'), max_length=100, blank=True)
    
    # Détails de la carte
    card_last_four = models.CharField(_('card last four'), max_length=4, blank=True)
    card_brand = models.CharField(_('card brand'), max_length=20, blank=True)
    card_exp_month = models.PositiveIntegerField(_('card exp month'), null=True, blank=True)
    card_exp_year = models.PositiveIntegerField(_('card exp year'), null=True, blank=True)
    
    # Métadonnées
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('Payment Method')
        verbose_name_plural = _('Payment Methods')
        db_table = 'payment_methods'
        ordering = ['-is_default', '-created_at']
    
    def __str__(self):
        if self.type == 'card':
            return f"{self.card_brand} ****{self.card_last_four}"
        return f"{self.get_type_display()} - {self.external_id}"
    
    def save(self, *args, **kwargs):
        # S'assurer qu'une seule méthode de paiement est marquée comme défaut
        if self.is_default:
            PaymentMethod.objects.filter(
                user=self.user, 
                is_default=True
            ).exclude(pk=self.pk).update(is_default=False)
        super().save(*args, **kwargs)

