from django.contrib import admin
from django.utils.html import format_html
from .models import PageView, ProductView, SearchQuery, Conversion, UserActivity, SalesReport


@admin.register(PageView)
class PageViewAdmin(admin.ModelAdmin):
    list_display = ['url', 'user', 'ip_address', 'timestamp']
    list_filter = ['timestamp', 'user']
    search_fields = ['url', 'user__email', 'ip_address']
    readonly_fields = ['timestamp']
    date_hierarchy = 'timestamp'
    
    def has_add_permission(self, request):
        return False


@admin.register(ProductView)
class ProductViewAdmin(admin.ModelAdmin):
    list_display = ['product_name', 'category', 'price', 'user', 'timestamp']
    list_filter = ['category', 'timestamp', 'user']
    search_fields = ['product_name', 'user__email']
    readonly_fields = ['timestamp']
    date_hierarchy = 'timestamp'
    
    def has_add_permission(self, request):
        return False


@admin.register(SearchQuery)
class SearchQueryAdmin(admin.ModelAdmin):
    list_display = ['query', 'results_count', 'user', 'timestamp']
    list_filter = ['timestamp', 'user']
    search_fields = ['query', 'user__email']
    readonly_fields = ['timestamp']
    date_hierarchy = 'timestamp'
    
    def has_add_permission(self, request):
        return False


@admin.register(Conversion)
class ConversionAdmin(admin.ModelAdmin):
    list_display = ['conversion_type', 'value', 'user', 'timestamp']
    list_filter = ['conversion_type', 'timestamp', 'user']
    search_fields = ['user__email']
    readonly_fields = ['timestamp']
    date_hierarchy = 'timestamp'
    
    def has_add_permission(self, request):
        return False


@admin.register(UserActivity)
class UserActivityAdmin(admin.ModelAdmin):
    list_display = ['user', 'activity_type', 'timestamp']
    list_filter = ['activity_type', 'timestamp']
    search_fields = ['user__email']
    readonly_fields = ['timestamp']
    date_hierarchy = 'timestamp'
    
    def has_add_permission(self, request):
        return False


@admin.register(SalesReport)
class SalesReportAdmin(admin.ModelAdmin):
    list_display = ['report_type', 'period_start', 'period_end', 'total_orders', 'total_revenue']
    list_filter = ['report_type', 'period_start', 'period_end']
    search_fields = ['top_selling_product']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('report_type', 'period_start', 'period_end')
        }),
        ('Métriques de vente', {
            'fields': ('total_orders', 'total_revenue', 'average_order_value')
        }),
        ('Métriques utilisateur', {
            'fields': ('new_customers', 'returning_customers')
        }),
        ('Métriques produit', {
            'fields': ('total_products_sold', 'top_selling_product')
        }),
        ('Métriques de conversion', {
            'fields': ('conversion_rate', 'cart_abandonment_rate')
        }),
        ('Métadonnées', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def has_add_permission(self, request):
        return False

