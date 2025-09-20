from django.urls import path
from . import views

app_name = 'notifications'

urlpatterns = [
    # Gestion des notifications
    path('', views.NotificationListView.as_view(), name='notification-list'),
    path('mark-read/<int:pk>/', views.mark_notification_read, name='mark-read'),
    path('mark-all-read/', views.mark_all_notifications_read, name='mark-all-read'),
    
    # Newsletter
    path('newsletter/subscribe/', views.newsletter_subscribe, name='newsletter-subscribe'),
    path('newsletter/unsubscribe/', views.newsletter_unsubscribe, name='newsletter-unsubscribe'),
    
    # API
    path('api/unread-count/', views.api_unread_count, name='api-unread-count'),
]