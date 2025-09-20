from django.urls import path
from . import views

app_name = 'analytics'

urlpatterns = [
    # Dashboard principal
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    
    # Rapports
    path('reports/sales/', views.SalesReportAPIView.as_view(), name='sales-report'),
    path('reports/analytics/', views.AnalyticsAPIView.as_view(), name='analytics-report'),
    path('reports/tracking/', views.TrackingAPIView.as_view(), name='tracking-report'),
]