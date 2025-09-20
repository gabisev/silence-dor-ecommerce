from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes
from .services import AnalyticsService, TrackingService
from datetime import datetime, timedelta
from django.utils import timezone


@method_decorator(staff_member_required, name='dispatch')
class DashboardView(TemplateView):
    """Vue du tableau de bord admin"""
    template_name = 'analytics/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Statistiques principales
        context['stats'] = AnalyticsService.get_dashboard_stats()
        
        # Données pour les graphiques
        context['sales_data'] = AnalyticsService.get_sales_chart_data(30)
        context['user_analytics'] = AnalyticsService.get_user_analytics()
        
        # Top produits et catégories
        context['top_products'] = AnalyticsService.get_top_products(10)
        context['top_categories'] = AnalyticsService.get_top_categories(10)
        
        # Métriques de conversion
        context['conversion_metrics'] = AnalyticsService.get_conversion_metrics()
        
        # Activité récente
        context['recent_activity'] = AnalyticsService.get_recent_activity(20)
        
        return context


class AnalyticsAPIView(APIView):
    """API pour les analytics"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Retourne les statistiques pour l'utilisateur connecté"""
        if not request.user.is_staff:
            return Response({'error': 'Accès non autorisé'}, status=403)
        
        # Paramètres de la requête
        days = int(request.GET.get('days', 30))
        report_type = request.GET.get('type', 'overview')
        
        if report_type == 'overview':
            data = {
                'stats': AnalyticsService.get_dashboard_stats(),
                'sales_data': AnalyticsService.get_sales_chart_data(days),
                'top_products': AnalyticsService.get_top_products(10),
                'top_categories': AnalyticsService.get_top_categories(10),
                'conversion_metrics': AnalyticsService.get_conversion_metrics(),
                'recent_activity': AnalyticsService.get_recent_activity(20),
            }
        elif report_type == 'sales':
            data = {
                'sales_data': AnalyticsService.get_sales_chart_data(days),
                'top_products': AnalyticsService.get_top_products(20),
            }
        elif report_type == 'users':
            data = AnalyticsService.get_user_analytics()
        else:
            data = AnalyticsService.get_dashboard_stats()
        
        return Response(data)


class SalesReportAPIView(APIView):
    """API pour les rapports de ventes"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Génère un rapport de ventes"""
        if not request.user.is_staff:
            return Response({'error': 'Accès non autorisé'}, status=403)
        
        # Paramètres
        report_type = request.GET.get('type', 'monthly')
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        
        if not start_date or not end_date:
            # Par défaut, le mois dernier
            end_date = timezone.now().date()
            start_date = end_date - timedelta(days=30)
        else:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        
        # Générer le rapport
        report = AnalyticsService.generate_sales_report(report_type, start_date, end_date)
        
        return Response({
            'report_id': report.id,
            'period_start': report.period_start.isoformat(),
            'period_end': report.period_end.isoformat(),
            'total_orders': report.total_orders,
            'total_revenue': float(report.total_revenue),
            'average_order_value': float(report.average_order_value),
            'new_customers': report.new_customers,
            'returning_customers': report.returning_customers,
            'total_products_sold': report.total_products_sold,
            'top_selling_product': report.top_selling_product,
        })


class TrackingAPIView(APIView):
    """API pour le tracking des événements"""
    
    def post(self, request):
        """Enregistre un événement de tracking"""
        event_type = request.data.get('type')
        data = request.data.get('data', {})
        
        if event_type == 'page_view':
            TrackingService.track_page_view(request, data.get('url', ''))
        elif event_type == 'product_view':
            # Nécessite l'ID du produit
            from apps.products.models import Product
            try:
                product = Product.objects.get(id=data.get('product_id'))
                TrackingService.track_product_view(request, product)
            except Product.DoesNotExist:
                pass
        elif event_type == 'search':
            TrackingService.track_search(
                request, 
                data.get('query', ''), 
                data.get('results_count', 0)
            )
        elif event_type == 'conversion':
            TrackingService.track_conversion(
                request,
                data.get('conversion_type', ''),
                data.get('value'),
                data.get('metadata', {})
            )
        
        return Response({'status': 'success'})

