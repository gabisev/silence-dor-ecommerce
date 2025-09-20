from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import SiteInformation

@admin.register(SiteInformation)
class SiteInformationAdmin(admin.ModelAdmin):
    """Administration des informations du site"""
    
    list_display = [
        'site_name', 
        'site_tagline', 
        'contact_email', 
        'contact_phone',
        'updated_at',
        'edit_link'
    ]
    
    list_filter = ['created_at', 'updated_at']
    
    search_fields = [
        'site_name', 
        'site_tagline', 
        'contact_email', 
        'company_name'
    ]
    
    readonly_fields = ['created_at', 'updated_at', 'preview_info']
    
    fieldsets = (
        ('🏢 Informations Générales', {
            'fields': (
                'site_name',
                'site_tagline', 
                'site_description',
                'hero_image',
                'preview_info'
            )
        }),
        ('📞 Contact', {
            'fields': (
                'contact_email',
                'contact_phone',
                'contact_address'
            )
        }),
        ('🌐 Réseaux Sociaux', {
            'fields': (
                'facebook_url',
                'instagram_url', 
                'twitter_url',
                'linkedin_url'
            ),
            'classes': ('collapse',)
        }),
        ('🏛️ Informations Légales', {
            'fields': (
                'company_name',
                'siret_number',
                'vat_number'
            ),
            'classes': ('collapse',)
        }),
        ('💰 Paramètres Financiers', {
            'fields': (
                'currency',
                'currency_symbol'
            ),
            'classes': ('collapse',)
        }),
        ('🔍 SEO et Analytics', {
            'fields': (
                'meta_keywords',
                'google_analytics_id'
            ),
            'classes': ('collapse',)
        }),
        ('📅 Métadonnées', {
            'fields': (
                'created_at',
                'updated_at'
            ),
            'classes': ('collapse',)
        })
    )
    
    def edit_link(self, obj):
        """Lien pour éditer les informations"""
        if obj.pk:
            url = reverse('admin:core_siteinformation_change', args=[obj.pk])
            return format_html(
                '<a href="{}" class="button">✏️ Modifier</a>',
                url
            )
        return '-'
    edit_link.short_description = 'Actions'
    
    def preview_info(self, obj):
        """Aperçu des informations du site"""
        if obj.pk:
            hero_image_html = ''
            if obj.hero_image:
                hero_image_html = f'''
                <div style="margin: 10px 0;">
                    <strong>Image Hero:</strong><br>
                    <img src="{obj.hero_image.url}" alt="Hero Image" style="max-width: 200px; height: auto; border-radius: 5px; border: 1px solid #ddd;">
                </div>
                '''
            
            return format_html(
                '''
                <div style="background: #f8f9fa; padding: 15px; border-radius: 5px; border-left: 4px solid #007cba;">
                    <h4 style="margin: 0 0 10px 0; color: #007cba;">{}</h4>
                    <p style="margin: 0 0 5px 0; font-style: italic; color: #666;">{}</p>
                    <p style="margin: 0 0 10px 0; color: #333;">{}</p>
                    {}
                </div>
                ''',
                obj.site_name,
                obj.site_tagline,
                obj.site_description[:100] + '...' if len(obj.site_description) > 100 else obj.site_description,
                hero_image_html
            )
        return 'Aucune information disponible'
    preview_info.short_description = 'Aperçu'
    
    def has_add_permission(self, request):
        """Empêche l'ajout de plusieurs instances"""
        return not SiteInformation.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        """Empêche la suppression des informations du site"""
        return False
    
    def get_queryset(self, request):
        """Optimise la requête"""
        return super().get_queryset(request).select_related()
    
    def save_model(self, request, obj, form, change):
        """Sauvegarde avec validation"""
        super().save_model(request, obj, form, change)
        
        # Message de confirmation
        from django.contrib import messages
        messages.success(
            request, 
            f'✅ Les informations du site "{obj.site_name}" ont été mises à jour avec succès !'
        )
    
    class Media:
        css = {
            'all': ('admin/css/site-info-admin.css',)
        }
        js = ('admin/js/site-info-admin.js',)
