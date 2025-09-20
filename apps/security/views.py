from django.shortcuts import render
from django.views.generic import TemplateView
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

@method_decorator(login_required, name='dispatch')
class TwoFactorSetupView(TemplateView):
    """Vue de configuration 2FA"""
    template_name = 'security/2fa_setup.html'

@method_decorator(login_required, name='dispatch')
class TwoFactorVerifyView(TemplateView):
    """Vue de vérification 2FA"""
    template_name = 'security/2fa_verify.html'

@method_decorator(login_required, name='dispatch')
class TwoFactorDisableView(TemplateView):
    """Vue de désactivation 2FA"""
    template_name = 'security/2fa_disable.html'

@method_decorator(login_required, name='dispatch')
class AuditLogView(TemplateView):
    """Vue du journal d'audit"""
    template_name = 'security/audit_log.html'

@method_decorator(login_required, name='dispatch')
class SecurityEventsView(TemplateView):
    """Vue des événements de sécurité"""
    template_name = 'security/security_events.html'

@method_decorator(login_required, name='dispatch')
class FailedLoginsView(TemplateView):
    """Vue des tentatives de connexion échouées"""
    template_name = 'security/failed_logins.html'

@method_decorator(login_required, name='dispatch')
class SecuritySettingsView(TemplateView):
    """Vue des paramètres de sécurité"""
    template_name = 'security/settings.html'

def api_security_status(request):
    """API pour le statut de sécurité"""
    return JsonResponse({'status': 'secure'})

