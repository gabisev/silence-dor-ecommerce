from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from .models import (
    Category, Brand, Product, ProductImage, 
    ProductAttribute, ProductAttributeValue, ProductReview
)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Administration des catégories"""
    
    list_display = ('name', 'parent', 'is_active', 'sort_order', 'product_count')
    list_filter = ('is_active', 'parent', 'created_at')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    ordering = ('sort_order', 'name')
    
    def product_count(self, obj):
        return obj.products.count()
    product_count.short_description = _('Products')
    product_count.admin_order_field = 'products__count'


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    """Administration des marques"""
    
    list_display = ('name', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """Administration des produits"""
    
    list_display = ('name', 'sku', 'category', 'brand', 'price', 'quantity', 'status', 'is_featured', 'created_at')
    list_filter = ('status', 'is_featured', 'is_digital', 'category', 'brand', 'created_at')
    search_fields = ('name', 'sku', 'description')
    prepopulated_fields = {'slug': ('name',)}
    raw_id_fields = ('vendor',)
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        (_('Basic Information'), {
            'fields': ('name', 'slug', 'description', 'short_description', 'sku')
        }),
        (_('Relations'), {
            'fields': ('category', 'brand', 'vendor')
        }),
        (_('Pricing'), {
            'fields': ('price', 'compare_price', 'cost_price')
        }),
        (_('Inventory'), {
            'fields': ('track_inventory', 'quantity', 'low_stock_threshold')
        }),
        (_('Status & Visibility'), {
            'fields': ('status', 'is_featured', 'is_digital')
        }),
        (_('Shipping'), {
            'fields': ('weight', 'length', 'width', 'height'),
            'classes': ('collapse',)
        }),
        (_('SEO'), {
            'fields': ('meta_title', 'meta_description'),
            'classes': ('collapse',)
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('category', 'brand', 'vendor')


class ProductImageInline(admin.TabularInline):
    """Inline pour les images de produits"""
    
    model = ProductImage
    extra = 1
    fields = ('image', 'alt_text', 'is_primary', 'sort_order')


class ProductAttributeValueInline(admin.TabularInline):
    """Inline pour les valeurs d'attributs de produits"""
    
    model = ProductAttributeValue
    extra = 1
    fields = ('attribute', 'value')


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    """Administration des images de produits"""
    
    list_display = ('product', 'image_preview', 'is_primary', 'sort_order')
    list_filter = ('is_primary', 'created_at')
    raw_id_fields = ('product',)
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" />', obj.image.url)
        return _('No image')
    image_preview.short_description = _('Preview')


@admin.register(ProductAttribute)
class ProductAttributeAdmin(admin.ModelAdmin):
    """Administration des attributs de produits"""
    
    list_display = ('name', 'type', 'is_required', 'is_filterable')
    list_filter = ('type', 'is_required', 'is_filterable')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}


@admin.register(ProductAttributeValue)
class ProductAttributeValueAdmin(admin.ModelAdmin):
    """Administration des valeurs d'attributs de produits"""
    
    list_display = ('product', 'attribute', 'value')
    list_filter = ('attribute',)
    search_fields = ('product__name', 'attribute__name', 'value')
    raw_id_fields = ('product',)


@admin.register(ProductReview)
class ProductReviewAdmin(admin.ModelAdmin):
    """Administration des avis sur les produits"""
    
    list_display = ('product', 'user', 'rating', 'title', 'is_approved', 'is_verified_purchase', 'created_at')
    list_filter = ('rating', 'is_approved', 'is_verified_purchase', 'created_at')
    search_fields = ('product__name', 'user__email', 'title', 'comment')
    raw_id_fields = ('product', 'user')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        (_('Review Information'), {
            'fields': ('product', 'user', 'rating', 'title', 'comment')
        }),
        (_('Status'), {
            'fields': ('is_verified_purchase', 'is_approved')
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
