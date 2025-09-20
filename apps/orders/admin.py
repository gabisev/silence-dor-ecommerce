from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from .models import Order, OrderItem, OrderStatusHistory, Coupon, OrderCoupon


class OrderItemInline(admin.TabularInline):
    """Inline pour les articles de commande"""
    
    model = OrderItem
    extra = 0
    readonly_fields = ('unit_price', 'total_price')
    fields = ('product', 'quantity', 'unit_price', 'total_price')


class OrderStatusHistoryInline(admin.TabularInline):
    """Inline pour l'historique des statuts"""
    
    model = OrderStatusHistory
    extra = 0
    readonly_fields = ('created_at',)
    fields = ('status', 'notes', 'created_by', 'created_at')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """Administration des commandes"""
    
    list_display = (
        'order_number', 'user', 'status', 'payment_status', 
        'total_amount', 'total_items', 'created_at'
    )
    list_filter = ('status', 'payment_status', 'created_at', 'updated_at')
    search_fields = ('order_number', 'user__email', 'user__first_name', 'user__last_name')
    readonly_fields = ('order_number', 'created_at', 'updated_at', 'total_items')
    raw_id_fields = ('user', 'billing_address', 'shipping_address')
    
    fieldsets = (
        (_('Order Information'), {
            'fields': ('order_number', 'user', 'status', 'payment_status')
        }),
        (_('Addresses'), {
            'fields': ('billing_address', 'shipping_address')
        }),
        (_('Pricing'), {
            'fields': ('subtotal', 'tax_amount', 'shipping_cost', 'discount_amount', 'total_amount')
        }),
        (_('Payment'), {
            'fields': ('payment_method', 'payment_reference', 'stripe_payment_intent_id')
        }),
        (_('Shipping'), {
            'fields': ('tracking_number', 'shipping_carrier')
        }),
        (_('Notes'), {
            'fields': ('notes', 'customer_notes')
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [OrderItemInline, OrderStatusHistoryInline]
    
    def total_items(self, obj):
        return obj.total_items
    total_items.short_description = _('Total Items')
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'user', 'billing_address', 'shipping_address'
        ).prefetch_related('items__product')


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    """Administration des articles de commande"""
    
    list_display = ('order', 'product', 'quantity', 'unit_price', 'total_price')
    list_filter = ('created_at',)
    search_fields = ('order__order_number', 'product__name', 'product__sku')
    raw_id_fields = ('order', 'product')
    readonly_fields = ('total_price', 'created_at')


@admin.register(OrderStatusHistory)
class OrderStatusHistoryAdmin(admin.ModelAdmin):
    """Administration de l'historique des statuts"""
    
    list_display = ('order', 'status', 'created_by', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('order__order_number', 'notes')
    raw_id_fields = ('order', 'created_by')
    readonly_fields = ('created_at',)


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    """Administration des coupons"""
    
    list_display = (
        'code', 'type', 'value', 'usage_limit', 'used_count', 
        'is_active', 'valid_from', 'valid_until'
    )
    list_filter = ('type', 'is_active', 'valid_from', 'valid_until', 'created_at')
    search_fields = ('code', 'description')
    readonly_fields = ('used_count', 'created_at', 'updated_at')
    
    fieldsets = (
        (_('Coupon Information'), {
            'fields': ('code', 'description', 'type', 'value')
        }),
        (_('Conditions'), {
            'fields': ('minimum_amount', 'maximum_discount')
        }),
        (_('Usage Limits'), {
            'fields': ('usage_limit', 'used_count')
        }),
        (_('Validity'), {
            'fields': ('valid_from', 'valid_until', 'is_active')
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(OrderCoupon)
class OrderCouponAdmin(admin.ModelAdmin):
    """Administration des coupons appliqués aux commandes"""
    
    list_display = ('order', 'coupon', 'discount_amount', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('order__order_number', 'coupon__code')
    raw_id_fields = ('order', 'coupon')
    readonly_fields = ('created_at',)

