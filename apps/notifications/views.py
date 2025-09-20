from django.shortcuts import render
from django.views.generic import TemplateView
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

@method_decorator(login_required, name='dispatch')
class NotificationListView(TemplateView):
    """Vue de la liste des notifications"""
    template_name = 'notifications/list.html'

def mark_notification_read(request, pk):
    """Marquer une notification comme lue"""
    return JsonResponse({'status': 'success'})

def mark_all_notifications_read(request):
    """Marquer toutes les notifications comme lues"""
    return JsonResponse({'status': 'success'})

def newsletter_subscribe(request):
    """S'abonner à la newsletter"""
    return JsonResponse({'status': 'success'})

def newsletter_unsubscribe(request):
    """Se désabonner de la newsletter"""
    return JsonResponse({'status': 'success'})

def api_unread_count(request):
    """API pour le nombre de notifications non lues"""
    return JsonResponse({'count': 0})