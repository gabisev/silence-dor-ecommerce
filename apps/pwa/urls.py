from django.urls import path
from . import views

app_name = 'pwa'

urlpatterns = [
    # Service Worker et PWA
    path('sw.js', views.ServiceWorkerView.as_view(), name='service-worker'),
    path('manifest.json', views.ManifestView.as_view(), name='manifest'),
    
    # Notifications push
    path('push/subscribe/', views.PushSubscribeView.as_view(), name='push-subscribe'),
    path('push/unsubscribe/', views.PushUnsubscribeView.as_view(), name='push-unsubscribe'),
    
    # Pages hors ligne
    path('offline/', views.OfflinePageView.as_view(), name='offline-page'),
    
    # API
    path('api/push/send/', views.api_send_push_notification, name='api-send-push'),
]

