from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
from .models import EmailTemplate, EmailLog, Notification, Newsletter, NewsletterSubscription


@admin.register(EmailTemplate)
class EmailTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'template_type', 'is_active', 'created_at']
    list_filter = ['template_type', 'is_active', 'created_at']
    search_fields = ['name', 'subject']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('name', 'template_type', 'is_active')
        }),
        ('Contenu', {
            'fields': ('subject', 'html_content', 'text_content')
        }),
        ('Métadonnées', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(EmailLog)
class EmailLogAdmin(admin.ModelAdmin):
    list_display = ['recipient_email', 'subject', 'status', 'sent_at', 'created_at']
    list_filter = ['status', 'template__template_type', 'sent_at', 'created_at']
    search_fields = ['recipient_email', 'subject']
    readonly_fields = ['created_at', 'sent_at', 'error_message', 'metadata']
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('template', 'recipient', 'recipient_email', 'subject')
        }),
        ('Statut', {
            'fields': ('status', 'sent_at', 'error_message')
        }),
        ('Métadonnées', {
            'fields': ('metadata', 'created_at'),
            'classes': ('collapse',)
        }),
    )
    
    def has_add_permission(self, request):
        return False


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'title', 'notification_type', 'is_read', 'created_at']
    list_filter = ['notification_type', 'is_read', 'created_at']
    search_fields = ['user__email', 'title', 'message']
    readonly_fields = ['created_at', 'read_at']
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('user', 'title', 'message', 'notification_type')
        }),
        ('Actions', {
            'fields': ('action_url', 'metadata')
        }),
        ('Statut', {
            'fields': ('is_read', 'read_at', 'created_at')
        }),
    )
    
    actions = ['mark_as_read', 'mark_as_unread']
    
    def mark_as_read(self, request, queryset):
        updated = queryset.update(is_read=True, read_at=timezone.now())
        self.message_user(request, f"{updated} notifications marquées comme lues.")
    mark_as_read.short_description = "Marquer comme lues"
    
    def mark_as_unread(self, request, queryset):
        updated = queryset.update(is_read=False, read_at=None)
        self.message_user(request, f"{updated} notifications marquées comme non lues.")
    mark_as_unread.short_description = "Marquer comme non lues"


@admin.register(Newsletter)
class NewsletterAdmin(admin.ModelAdmin):
    list_display = ['title', 'status', 'scheduled_at', 'sent_at', 'recipients_count', 'opened_count']
    list_filter = ['status', 'created_at', 'sent_at']
    search_fields = ['title', 'subject']
    readonly_fields = ['sent_at', 'recipients_count', 'opened_count', 'clicked_count', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('title', 'subject', 'content', 'status')
        }),
        ('Programmation', {
            'fields': ('scheduled_at',)
        }),
        ('Statistiques', {
            'fields': ('recipients_count', 'opened_count', 'clicked_count', 'sent_at'),
            'classes': ('collapse',)
        }),
        ('Métadonnées', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['send_newsletter']
    
    def send_newsletter(self, request, queryset):
        from .services import EmailService
        for newsletter in queryset:
            if newsletter.status == 'draft':
                sent_count = EmailService.send_newsletter(newsletter)
                self.message_user(request, f"Newsletter '{newsletter.title}' envoyée à {sent_count} destinataires.")
    send_newsletter.short_description = "Envoyer la newsletter"


@admin.register(NewsletterSubscription)
class NewsletterSubscriptionAdmin(admin.ModelAdmin):
    list_display = ['email', 'user', 'is_active', 'subscribed_at', 'unsubscribed_at']
    list_filter = ['is_active', 'subscribed_at', 'unsubscribed_at']
    search_fields = ['email', 'user__email']
    readonly_fields = ['subscribed_at', 'unsubscribed_at']
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('email', 'user', 'is_active')
        }),
        ('Dates', {
            'fields': ('subscribed_at', 'unsubscribed_at')
        }),
    )
    
    actions = ['activate_subscriptions', 'deactivate_subscriptions']
    
    def activate_subscriptions(self, request, queryset):
        updated = queryset.update(is_active=True, unsubscribed_at=None)
        self.message_user(request, f"{updated} abonnements activés.")
    activate_subscriptions.short_description = "Activer les abonnements"
    
    def deactivate_subscriptions(self, request, queryset):
        updated = queryset.update(is_active=False, unsubscribed_at=timezone.now())
        self.message_user(request, f"{updated} abonnements désactivés.")
    deactivate_subscriptions.short_description = "Désactiver les abonnements"

