from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Payment, Refund, PaymentMethod


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    """Administration des paiements"""
    
    list_display = (
        'external_id', 'order', 'user', 'amount', 'currency', 
        'method', 'status', 'created_at'
    )
    list_filter = ('status', 'method', 'currency', 'created_at')
    search_fields = ('external_id', 'transaction_id', 'order__order_number', 'user__email')
    raw_id_fields = ('order', 'user')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        (_('Payment Information'), {
            'fields': ('order', 'user', 'amount', 'currency', 'method', 'status')
        }),
        (_('External References'), {
            'fields': ('external_id', 'transaction_id', 'stripe_payment_intent_id', 'stripe_charge_id')
        }),
        (_('Card Details'), {
            'fields': ('card_last_four', 'card_brand', 'card_exp_month', 'card_exp_year'),
            'classes': ('collapse',)
        }),
        (_('Additional Information'), {
            'fields': ('failure_reason', 'metadata'),
            'classes': ('collapse',)
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Refund)
class RefundAdmin(admin.ModelAdmin):
    """Administration des remboursements"""
    
    list_display = (
        'external_id', 'payment', 'order', 'amount', 'currency', 
        'status', 'created_at'
    )
    list_filter = ('status', 'currency', 'created_at')
    search_fields = ('external_id', 'stripe_refund_id', 'order__order_number')
    raw_id_fields = ('payment', 'order')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        (_('Refund Information'), {
            'fields': ('payment', 'order', 'amount', 'currency', 'status')
        }),
        (_('External References'), {
            'fields': ('external_id', 'stripe_refund_id')
        }),
        (_('Details'), {
            'fields': ('reason', 'notes')
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    """Administration des méthodes de paiement"""
    
    list_display = (
        'user', 'type', 'card_brand', 'card_last_four', 
        'is_default', 'created_at'
    )
    list_filter = ('type', 'is_default', 'created_at')
    search_fields = ('user__email', 'external_id', 'stripe_payment_method_id')
    raw_id_fields = ('user',)
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        (_('Payment Method Information'), {
            'fields': ('user', 'type', 'is_default')
        }),
        (_('External References'), {
            'fields': ('external_id', 'stripe_payment_method_id')
        }),
        (_('Card Details'), {
            'fields': ('card_last_four', 'card_brand', 'card_exp_month', 'card_exp_year'),
            'classes': ('collapse',)
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

