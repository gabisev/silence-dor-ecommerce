from django.urls import path
from . import views

app_name = 'inventory'

urlpatterns = [
    # Gestion des stocks
    path('', views.InventoryDashboardView.as_view(), name='inventory-dashboard'),
    path('warehouses/', views.WarehouseListView.as_view(), name='warehouse-list'),
    path('warehouses/<int:pk>/', views.WarehouseDetailView.as_view(), name='warehouse-detail'),
    
    # Mouvements de stock
    path('movements/', views.StockMovementListView.as_view(), name='stock-movement-list'),
    path('movements/create/', views.StockMovementCreateView.as_view(), name='stock-movement-create'),
    
    # Alertes et rapports
    path('alerts/', views.StockAlertsView.as_view(), name='stock-alerts'),
    path('reports/', views.InventoryReportView.as_view(), name='inventory-report'),
    
    # API
    path('api/stock-levels/', views.api_stock_levels, name='api-stock-levels'),
    path('api/movements/', views.api_stock_movements, name='api-stock-movements'),
]

