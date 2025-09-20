from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from django.shortcuts import get_object_or_404, render, redirect
from django.views.generic import ListView, DetailView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from .models import Order, OrderItem, OrderStatusHistory, Coupon, OrderCoupon
from .serializers import (
    OrderSerializer, OrderCreateSerializer, OrderItemSerializer,
    CouponSerializer, OrderCouponSerializer
)
from apps.cart.models import Cart, CartItem
from apps.accounts.models import Address


class OrderListView(generics.ListAPIView):
    """Vue pour lister les commandes de l'utilisateur"""
    
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).select_related(
            'billing_address', 'shipping_address'
        ).prefetch_related('items__product', 'status_history')


class OrderDetailView(generics.RetrieveAPIView):
    """Vue pour les détails d'une commande"""
    
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).select_related(
            'billing_address', 'shipping_address'
        ).prefetch_related('items__product', 'status_history')


class OrderCreateView(generics.CreateAPIView):
    """Vue pour créer une commande depuis le panier"""
    
    serializer_class = OrderCreateSerializer
    permission_classes = [IsAuthenticated]
    
    def create(self, request, *args, **kwargs):
        # Vérifier que le panier n'est pas vide
        try:
            cart = Cart.objects.get(user=request.user)
        except Cart.DoesNotExist:
            return Response(
                {'error': _('Votre panier est vide.')}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if cart.is_empty:
            return Response(
                {'error': _('Votre panier est vide.')}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Préparer les données pour la commande
        order_data = {
            'billing_address_id': request.data.get('billing_address_id'),
            'shipping_address_id': request.data.get('shipping_address_id'),
            'customer_notes': request.data.get('customer_notes', ''),
            'coupon_code': request.data.get('coupon_code', ''),
            'items': []
        }
        
        # Convertir les articles du panier
        for cart_item in cart.items.all():
            order_data['items'].append({
                'product': cart_item.product,
                'quantity': cart_item.quantity
            })
        
        serializer = self.get_serializer(data=order_data)
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        
        # Vider le panier après création de la commande
        cart.items.all().delete()
        
        return Response({
            'order': OrderSerializer(order).data,
            'message': _('Commande créée avec succès!')
        }, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_order_from_cart_view(request):
    """Vue pour créer une commande directement depuis le panier"""
    
    # Vérifier que le panier n'est pas vide
    try:
        cart = Cart.objects.get(user=request.user)
    except Cart.DoesNotExist:
        return Response(
            {'error': _('Votre panier est vide.')}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if cart.is_empty:
        return Response(
            {'error': _('Votre panier est vide.')}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Récupérer les adresses
    billing_address_id = request.data.get('billing_address_id')
    shipping_address_id = request.data.get('shipping_address_id')
    
    if not billing_address_id or not shipping_address_id:
        return Response(
            {'error': _('Adresses de facturation et de livraison requises.')}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Créer la commande
    from .serializers import OrderCreateSerializer
    
    order_data = {
        'billing_address_id': billing_address_id,
        'shipping_address_id': shipping_address_id,
        'customer_notes': request.data.get('customer_notes', ''),
        'coupon_code': request.data.get('coupon_code', ''),
        'items': []
    }
    
    # Convertir les articles du panier
    for cart_item in cart.items.all():
        order_data['items'].append({
            'product': cart_item.product,
            'quantity': cart_item.quantity
        })
    
    serializer = OrderCreateSerializer(data=order_data, context={'request': request})
    if serializer.is_valid():
        order = serializer.save()
        
        # Vider le panier après création de la commande
        cart.items.all().delete()
        
        return Response({
            'order': OrderSerializer(order).data,
            'message': _('Commande créée avec succès!')
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def cancel_order_view(request, order_id):
    """Vue pour annuler une commande"""
    
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    if order.status in ['delivered', 'cancelled', 'refunded']:
        return Response(
            {'error': _('Cette commande ne peut pas être annulée.')}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    order.status = 'cancelled'
    order.save()
    
    # Ajouter à l'historique
    OrderStatusHistory.objects.create(
        order=order,
        status='cancelled',
        notes='Commande annulée par le client'
    )
    
    return Response({
        'message': _('Commande annulée avec succès.'),
        'order': OrderSerializer(order).data
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def order_tracking_view(request, order_number):
    """Vue pour suivre une commande"""
    
    order = get_object_or_404(Order, order_number=order_number, user=request.user)
    
    tracking_info = {
        'order_number': order.order_number,
        'status': order.status,
        'status_display': order.get_status_display(),
        'tracking_number': order.tracking_number,
        'shipping_carrier': order.shipping_carrier,
        'status_history': []
    }
    
    # Ajouter l'historique des statuts
    for history in order.status_history.all():
        tracking_info['status_history'].append({
            'status': history.status,
            'status_display': history.get_status_display(),
            'notes': history.notes,
            'created_at': history.created_at
        })
    
    return Response(tracking_info)


class CouponListView(generics.ListAPIView):
    """Vue pour lister les coupons disponibles"""
    
    queryset = Coupon.objects.filter(is_active=True)
    serializer_class = CouponSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def validate_coupon_view(request):
    """Vue pour valider un coupon"""
    
    code = request.data.get('code', '').strip().upper()
    order_amount = request.data.get('order_amount', 0)
    
    if not code:
        return Response(
            {'error': _('Code de coupon requis.')}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        coupon = Coupon.objects.get(code=code, is_active=True)
    except Coupon.DoesNotExist:
        return Response(
            {'error': _('Code de coupon invalide.')}, 
            status=status.HTTP_404_NOT_FOUND
        )
    
    if not coupon.is_valid():
        return Response(
            {'error': _('Ce coupon a expiré ou a atteint sa limite d\'utilisation.')}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    discount_amount = coupon.calculate_discount(order_amount)
    
    if discount_amount == 0:
        return Response(
            {'error': _('Ce coupon ne peut pas être appliqué à ce montant.')}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    return Response({
        'coupon': CouponSerializer(coupon).data,
        'discount_amount': discount_amount,
        'message': _('Coupon valide!')
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def order_stats_view(request):
    """Vue pour les statistiques de commandes de l'utilisateur"""
    
    orders = Order.objects.filter(user=request.user)
    
    stats = {
        'total_orders': orders.count(),
        'total_spent': sum(order.total_amount for order in orders),
        'pending_orders': orders.filter(status='pending').count(),
        'delivered_orders': orders.filter(status='delivered').count(),
        'cancelled_orders': orders.filter(status='cancelled').count(),
    }
    
    return Response(stats)


# Vues de base pour les commandes
class OrderPageListView(LoginRequiredMixin, ListView):
    """Vue pour lister les commandes de l'utilisateur (page)"""
    model = Order
    template_name = 'orders/order_list.html'
    context_object_name = 'orders'
    paginate_by = 10
    
    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).order_by('-created_at')


class OrderPageDetailView(LoginRequiredMixin, DetailView):
    """Vue pour afficher une commande (page)"""
    model = Order
    template_name = 'orders/order_detail.html'
    context_object_name = 'order'
    
    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).prefetch_related('items__product', 'status_history')


class CheckoutView(LoginRequiredMixin, TemplateView):
    """Vue pour le processus de commande"""
    template_name = 'orders/checkout.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart, created = Cart.objects.get_or_create(user=self.request.user)
        context['cart'] = cart
        context['cart_items'] = cart.items.select_related('product').all()
        context['addresses'] = Address.objects.filter(user=self.request.user)
        return context
    
    def post(self, request, *args, **kwargs):
        """Traiter la commande"""
        cart, created = Cart.objects.get_or_create(user=request.user)
        
        if not cart.items.exists():
            messages.error(request, 'Votre panier est vide.')
            return redirect('cart:cart')
        
        # Récupérer les données du formulaire
        shipping_address_id = request.POST.get('shipping_address')
        billing_address_id = request.POST.get('billing_address')
        payment_method = request.POST.get('payment_method')
        
        try:
            shipping_address = Address.objects.get(id=shipping_address_id, user=request.user)
            billing_address = Address.objects.get(id=billing_address_id, user=request.user)
        except Address.DoesNotExist:
            messages.error(request, 'Adresse invalide.')
            return redirect('orders:checkout')
        
        # Créer la commande
        order = Order.objects.create(
            user=request.user,
            shipping_address=shipping_address,
            billing_address=billing_address,
            payment_method=payment_method,
            status='pending'
        )
        
        # Ajouter les articles de la commande
        total = 0
        for cart_item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                quantity=cart_item.quantity,
                price=cart_item.product.price
            )
            total += cart_item.product.price * cart_item.quantity
        
        order.total_amount = total
        order.save()
        
        # Vider le panier
        cart.items.all().delete()
        
        messages.success(request, 'Commande créée avec succès !')
        return redirect('orders:order-detail', pk=order.pk)


@login_required
def cancel_order_view(request, order_id):
    """Vue pour annuler une commande"""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    if order.status in ['pending', 'processing']:
        order.status = 'cancelled'
        order.save()
        
        # Ajouter un historique
        OrderStatusHistory.objects.create(
            order=order,
            status='cancelled',
            note='Commande annulée par l\'utilisateur'
        )
        
        messages.success(request, 'Commande annulée avec succès.')
    else:
        messages.error(request, 'Cette commande ne peut pas être annulée.')
    
    return redirect('orders:order-detail', pk=order.pk)
