from django.shortcuts import render
from django.views.generic import TemplateView
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

class ServiceWorkerView(TemplateView):
    """Vue du Service Worker"""
    def get(self, request, *args, **kwargs):
        return HttpResponse("// Service Worker placeholder", content_type="application/javascript")

class ManifestView(TemplateView):
    """Vue du manifest PWA"""
    def get(self, request, *args, **kwargs):
        manifest = {
            "name": "Silence d'Or",
            "short_name": "Silence d'Or",
            "start_url": "/",
            "display": "standalone",
            "background_color": "#ffffff",
            "theme_color": "#e91e63"
        }
        return JsonResponse(manifest)

@method_decorator(login_required, name='dispatch')
class PushSubscribeView(TemplateView):
    """Vue d'abonnement aux notifications push"""
    template_name = 'pwa/push_subscribe.html'

@method_decorator(login_required, name='dispatch')
class PushUnsubscribeView(TemplateView):
    """Vue de désabonnement aux notifications push"""
    template_name = 'pwa/push_unsubscribe.html'

class OfflinePageView(TemplateView):
    """Vue de la page hors ligne"""
    template_name = 'pwa/offline.html'

def api_send_push_notification(request):
    """API pour envoyer une notification push"""
    return JsonResponse({'status': 'success'})

