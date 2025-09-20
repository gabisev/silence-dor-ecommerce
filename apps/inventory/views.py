from django.shortcuts import render
from django.views.generic import TemplateView
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

@method_decorator(login_required, name='dispatch')
class InventoryDashboardView(TemplateView):
    """Vue du tableau de bord d'inventaire"""
    template_name = 'inventory/dashboard.html'

@method_decorator(login_required, name='dispatch')
class WarehouseListView(TemplateView):
    """Vue de la liste des entrepôts"""
    template_name = 'inventory/warehouse_list.html'

@method_decorator(login_required, name='dispatch')
class WarehouseDetailView(TemplateView):
    """Vue de détail d'un entrepôt"""
    template_name = 'inventory/warehouse_detail.html'

@method_decorator(login_required, name='dispatch')
class StockMovementListView(TemplateView):
    """Vue de la liste des mouvements de stock"""
    template_name = 'inventory/stock_movement_list.html'

@method_decorator(login_required, name='dispatch')
class StockMovementCreateView(TemplateView):
    """Vue de création de mouvement de stock"""
    template_name = 'inventory/stock_movement_create.html'

@method_decorator(login_required, name='dispatch')
class StockAlertsView(TemplateView):
    """Vue des alertes de stock"""
    template_name = 'inventory/stock_alerts.html'

@method_decorator(login_required, name='dispatch')
class InventoryReportView(TemplateView):
    """Vue des rapports d'inventaire"""
    template_name = 'inventory/report.html'

def api_stock_levels(request):
    """API pour les niveaux de stock"""
    return JsonResponse({'stock_levels': []})

def api_stock_movements(request):
    """API pour les mouvements de stock"""
    return JsonResponse({'movements': []})

