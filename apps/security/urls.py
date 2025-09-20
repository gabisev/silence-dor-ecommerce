from django.urls import path
from . import views

app_name = 'security'

urlpatterns = [
    # 2FA
    path('2fa/setup/', views.TwoFactorSetupView.as_view(), name='2fa-setup'),
    path('2fa/verify/', views.TwoFactorVerifyView.as_view(), name='2fa-verify'),
    path('2fa/disable/', views.TwoFactorDisableView.as_view(), name='2fa-disable'),
    
    # Audit et sécurité
    path('audit-log/', views.AuditLogView.as_view(), name='audit-log'),
    path('security-events/', views.SecurityEventsView.as_view(), name='security-events'),
    path('failed-logins/', views.FailedLoginsView.as_view(), name='failed-logins'),
    
    # Paramètres de sécurité
    path('settings/', views.SecuritySettingsView.as_view(), name='security-settings'),
    
    # API
    path('api/security-status/', views.api_security_status, name='api-security-status'),
]

