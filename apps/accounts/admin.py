from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User, UserProfile, Address


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Administration des utilisateurs"""
    
    list_display = ('email', 'first_name', 'last_name', 'is_vendor', 'is_active', 'date_joined')
    list_filter = ('is_vendor', 'is_active', 'is_staff', 'is_superuser', 'date_joined')
    search_fields = ('email', 'first_name', 'last_name', 'phone')
    ordering = ('-date_joined',)
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {
            'fields': ('first_name', 'last_name', 'phone', 'birth_date')
        }),
        (_('Address'), {
            'fields': ('address', 'city', 'postal_code', 'country')
        }),
        (_('Business info'), {
            'fields': ('is_vendor', 'company_name', 'tax_number'),
            'classes': ('collapse',)
        }),
        (_('Preferences'), {
            'fields': ('newsletter_subscription', 'language'),
            'classes': ('collapse',)
        }),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'password1', 'password2'),
        }),
    )


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """Administration des profils utilisateurs"""
    
    list_display = ('user', 'email_notifications', 'sms_notifications', 'created_at')
    list_filter = ('email_notifications', 'sms_notifications', 'created_at')
    search_fields = ('user__email', 'user__first_name', 'user__last_name')
    raw_id_fields = ('user',)


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    """Administration des adresses"""
    
    list_display = ('user', 'type', 'first_name', 'last_name', 'city', 'country', 'is_default')
    list_filter = ('type', 'country', 'is_default', 'created_at')
    search_fields = ('user__email', 'first_name', 'last_name', 'city', 'postal_code')
    raw_id_fields = ('user',)
    
    fieldsets = (
        (None, {
            'fields': ('user', 'type', 'is_default')
        }),
        (_('Contact info'), {
            'fields': ('first_name', 'last_name', 'company', 'phone')
        }),
        (_('Address details'), {
            'fields': ('address_line_1', 'address_line_2', 'city', 'state', 'postal_code', 'country')
        }),
    )

