from django.db.models import Count, Sum, Avg, Q
from django.utils import timezone
from datetime import datetime, timedelta
from django.contrib.auth import get_user_model
from apps.orders.models import Order, OrderItem
from apps.products.models import Product
from apps.cart.models import Cart, CartItem
from apps.accounts.models import User
from .models import PageView, ProductView, SearchQuery, Conversion, UserActivity, SalesReport

User = get_user_model()


class AnalyticsService:
    """Service pour les analytics et statistiques"""
    
    @staticmethod
    def get_dashboard_stats():
        """Statistiques principales pour le tableau de bord"""
        today = timezone.now().date()
        this_month = today.replace(day=1)
        last_month = (this_month - timedelta(days=1)).replace(day=1)
        
        # Statistiques générales
        total_users = User.objects.count()
        total_products = Product.objects.count()
        total_orders = Order.objects.count()
        
        # Revenus
        total_revenue = Order.objects.filter(
            status__in=['completed', 'delivered']
        ).aggregate(total=Sum('total_price'))['total'] or 0
        
        monthly_revenue = Order.objects.filter(
            created_at__gte=this_month,
            status__in=['completed', 'delivered']
        ).aggregate(total=Sum('total_price'))['total'] or 0
        
        # Commandes du mois
        monthly_orders = Order.objects.filter(created_at__gte=this_month).count()
        
        # Nouveaux utilisateurs du mois
        new_users_this_month = User.objects.filter(date_joined__gte=this_month).count()
        
        # Produits en rupture de stock
        out_of_stock_products = Product.objects.filter(quantity=0).count()
        
        # Panier moyen
        avg_order_value = Order.objects.filter(
            status__in=['completed', 'delivered']
        ).aggregate(avg=Avg('total_price'))['avg'] or 0
        
        return {
            'total_users': total_users,
            'total_products': total_products,
            'total_orders': total_orders,
            'total_revenue': float(total_revenue),
            'monthly_revenue': float(monthly_revenue),
            'monthly_orders': monthly_orders,
            'new_users_this_month': new_users_this_month,
            'out_of_stock_products': out_of_stock_products,
            'avg_order_value': float(avg_order_value),
        }
    
    @staticmethod
    def get_sales_chart_data(days=30):
        """Données pour le graphique des ventes"""
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=days)
        
        sales_data = []
        for i in range(days):
            date = start_date + timedelta(days=i)
            daily_revenue = Order.objects.filter(
                created_at__date=date,
                status__in=['completed', 'delivered']
            ).aggregate(total=Sum('total_price'))['total'] or 0
            
            daily_orders = Order.objects.filter(created_at__date=date).count()
            
            sales_data.append({
                'date': date.isoformat(),
                'revenue': float(daily_revenue),
                'orders': daily_orders,
            })
        
        return sales_data
    
    @staticmethod
    def get_top_products(limit=10):
        """Produits les plus vendus"""
        top_products = OrderItem.objects.values(
            'product__name', 'product__id'
        ).annotate(
            total_sold=Sum('quantity'),
            total_revenue=Sum('price')
        ).order_by('-total_sold')[:limit]
        
        return list(top_products)
    
    @staticmethod
    def get_top_categories(limit=10):
        """Catégories les plus vendues"""
        top_categories = OrderItem.objects.values(
            'product__category__name'
        ).annotate(
            total_sold=Sum('quantity'),
            total_revenue=Sum('price')
        ).order_by('-total_sold')[:limit]
        
        return list(top_categories)
    
    @staticmethod
    def get_user_analytics():
        """Analytiques utilisateur"""
        total_users = User.objects.count()
        active_users = User.objects.filter(is_active=True).count()
        
        # Utilisateurs par mois (derniers 12 mois)
        user_growth = []
        for i in range(12):
            month_start = timezone.now().date().replace(day=1) - timedelta(days=30*i)
            month_end = month_start + timedelta(days=30)
            
            users_this_month = User.objects.filter(
                date_joined__date__gte=month_start,
                date_joined__date__lt=month_end
            ).count()
            
            user_growth.append({
                'month': month_start.strftime('%Y-%m'),
                'count': users_this_month,
            })
        
        return {
            'total_users': total_users,
            'active_users': active_users,
            'user_growth': user_growth,
        }
    
    @staticmethod
    def get_conversion_metrics():
        """Métriques de conversion"""
        # Taux de conversion (commandes / visiteurs uniques)
        total_orders = Order.objects.count()
        unique_visitors = PageView.objects.values('session_key').distinct().count()
        conversion_rate = (total_orders / unique_visitors * 100) if unique_visitors > 0 else 0
        
        # Taux d'abandon de panier
        total_carts = Cart.objects.count()
        abandoned_carts = Cart.objects.filter(
            created_at__lt=timezone.now() - timedelta(hours=24)
        ).count()
        abandonment_rate = (abandoned_carts / total_carts * 100) if total_carts > 0 else 0
        
        return {
            'conversion_rate': round(conversion_rate, 2),
            'cart_abandonment_rate': round(abandonment_rate, 2),
        }
    
    @staticmethod
    def get_recent_activity(limit=20):
        """Activité récente"""
        activities = []
        
        # Commandes récentes
        recent_orders = Order.objects.select_related('user').order_by('-created_at')[:limit//2]
        for order in recent_orders:
            activities.append({
                'type': 'order',
                'message': f"Nouvelle commande #{order.id} de {order.user.email}",
                'timestamp': order.created_at,
                'value': float(order.total_price),
            })
        
        # Inscriptions récentes
        recent_users = User.objects.order_by('-date_joined')[:limit//2]
        for user in recent_users:
            activities.append({
                'type': 'user',
                'message': f"Nouvel utilisateur: {user.email}",
                'timestamp': user.date_joined,
                'value': None,
            })
        
        # Trier par timestamp et limiter
        activities.sort(key=lambda x: x['timestamp'], reverse=True)
        return activities[:limit]
    
    @staticmethod
    def generate_sales_report(report_type, start_date, end_date):
        """Génère un rapport de ventes"""
        orders = Order.objects.filter(
            created_at__date__gte=start_date,
            created_at__date__lte=end_date
        )
        
        # Métriques de base
        total_orders = orders.count()
        total_revenue = orders.filter(
            status__in=['completed', 'delivered']
        ).aggregate(total=Sum('total_price'))['total'] or 0
        
        avg_order_value = orders.filter(
            status__in=['completed', 'delivered']
        ).aggregate(avg=Avg('total_price'))['avg'] or 0
        
        # Nouveaux vs clients de retour
        new_customers = orders.values('user').distinct().count()
        returning_customers = orders.exclude(
            user__in=Order.objects.filter(
                created_at__date__lt=start_date
            ).values_list('user', flat=True)
        ).values('user').distinct().count()
        
        # Produits vendus
        total_products_sold = OrderItem.objects.filter(
            order__in=orders
        ).aggregate(total=Sum('quantity'))['total'] or 0
        
        # Produit le plus vendu
        top_product = OrderItem.objects.filter(
            order__in=orders
        ).values('product__name').annotate(
            total_sold=Sum('quantity')
        ).order_by('-total_sold').first()
        
        # Créer le rapport
        report = SalesReport.objects.create(
            report_type=report_type,
            period_start=start_date,
            period_end=end_date,
            total_orders=total_orders,
            total_revenue=total_revenue,
            average_order_value=avg_order_value,
            new_customers=new_customers,
            returning_customers=returning_customers,
            total_products_sold=total_products_sold,
            top_selling_product=top_product['product__name'] if top_product else '',
        )
        
        return report


class TrackingService:
    """Service pour le tracking des utilisateurs"""
    
    @staticmethod
    def track_page_view(request, url):
        """Enregistre une vue de page"""
        PageView.objects.create(
            user=request.user if request.user.is_authenticated else None,
            session_key=request.session.session_key,
            url=url,
            referrer=request.META.get('HTTP_REFERER', ''),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            ip_address=request.META.get('REMOTE_ADDR'),
        )
    
    @staticmethod
    def track_product_view(request, product):
        """Enregistre une vue de produit"""
        ProductView.objects.create(
            user=request.user if request.user.is_authenticated else None,
            session_key=request.session.session_key,
            product_id=product.id,
            product_name=product.name,
            category=product.category.name if product.category else '',
            price=product.price,
        )
    
    @staticmethod
    def track_search(request, query, results_count):
        """Enregistre une recherche"""
        SearchQuery.objects.create(
            user=request.user if request.user.is_authenticated else None,
            session_key=request.session.session_key,
            query=query,
            results_count=results_count,
        )
    
    @staticmethod
    def track_conversion(request, conversion_type, value=None, metadata=None):
        """Enregistre une conversion"""
        Conversion.objects.create(
            user=request.user if request.user.is_authenticated else None,
            session_key=request.session.session_key,
            conversion_type=conversion_type,
            value=value,
            metadata=metadata or {},
        )
    
    @staticmethod
    def track_user_activity(user, activity_type, metadata=None):
        """Enregistre une activité utilisateur"""
        UserActivity.objects.create(
            user=user,
            activity_type=activity_type,
            metadata=metadata or {},
        )

