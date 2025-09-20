from django.contrib import admin
from .models import SearchIndex, SearchSuggestion, SearchFilter, SearchHistory, SearchAnalytics


@admin.register(SearchIndex)
class SearchIndexAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'brand', 'price', 'is_active', 'popularity_score']
    list_filter = ['category', 'brand', 'is_active', 'created_at']
    search_fields = ['title', 'description', 'keywords']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Contenu indexé', {
            'fields': ('content_type', 'object_id', 'title', 'description', 'keywords')
        }),
        ('Métadonnées', {
            'fields': ('category', 'brand', 'tags', 'price', 'popularity_score')
        }),
        ('Statut', {
            'fields': ('is_active',)
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(SearchSuggestion)
class SearchSuggestionAdmin(admin.ModelAdmin):
    list_display = ['query', 'count', 'last_used', 'is_active']
    list_filter = ['is_active', 'last_used']
    search_fields = ['query']
    readonly_fields = ['last_used']
    ordering = ['-count', '-last_used']


@admin.register(SearchFilter)
class SearchFilterAdmin(admin.ModelAdmin):
    list_display = ['display_name', 'filter_type', 'field_name', 'is_active', 'order']
    list_filter = ['filter_type', 'is_active']
    search_fields = ['name', 'display_name', 'field_name']
    ordering = ['order', 'name']


@admin.register(SearchHistory)
class SearchHistoryAdmin(admin.ModelAdmin):
    list_display = ['query', 'user', 'results_count', 'timestamp']
    list_filter = ['timestamp', 'user']
    search_fields = ['query', 'user__email']
    readonly_fields = ['timestamp']
    date_hierarchy = 'timestamp'
    
    def has_add_permission(self, request):
        return False


@admin.register(SearchAnalytics)
class SearchAnalyticsAdmin(admin.ModelAdmin):
    list_display = ['query', 'results_count', 'click_through_rate', 'conversion_rate', 'date']
    list_filter = ['date']
    search_fields = ['query']
    readonly_fields = ['date']
    date_hierarchy = 'date'
    
    def has_add_permission(self, request):
        return False

