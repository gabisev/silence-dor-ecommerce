from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    # Pages de base
    path('', views.OrderPageListView.as_view(), name='order-list'),
    path('<int:pk>/', views.OrderPageDetailView.as_view(), name='order-detail'),
    path('checkout/', views.CheckoutView.as_view(), name='checkout'),
    path('<int:order_id>/cancel/', views.cancel_order_view, name='cancel-order'),
    
    # API URLs
    path('api/', views.OrderListView.as_view(), name='order-list-api'),
    path('api/<int:pk>/', views.OrderDetailView.as_view(), name='order-detail-api'),
    path('api/create/', views.OrderCreateView.as_view(), name='order-create-api'),
    path('api/create-from-cart/', views.create_order_from_cart_view, name='create-from-cart-api'),
    path('api/<int:order_id>/cancel/', views.cancel_order_view, name='cancel-order-api'),
    path('api/track/<str:order_number>/', views.order_tracking_view, name='order-tracking-api'),
    path('api/stats/', views.order_stats_view, name='order-stats-api'),
    
    # Coupons API
    path('api/coupons/', views.CouponListView.as_view(), name='coupon-list-api'),
    path('api/coupons/validate/', views.validate_coupon_view, name='validate-coupon-api'),
]
