from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views.generic import TemplateView
from django.utils.translation import gettext_lazy as _
from .models import Cart, CartItem, Wishlist, WishlistItem
from .serializers import CartSerializer, CartItemSerializer, WishlistSerializer, WishlistItemSerializer
from apps.products.models import Product


class CartView(generics.RetrieveAPIView):
    """Vue pour récupérer le panier de l'utilisateur"""
    
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        cart, created = Cart.objects.get_or_create(user=self.request.user)
        return cart


class CartItemCreateView(generics.CreateAPIView):
    """Vue pour ajouter un article au panier"""
    
    serializer_class = CartItemSerializer
    permission_classes = [IsAuthenticated]
    
    def perform_create(self, serializer):
        cart, created = Cart.objects.get_or_create(user=self.request.user)
        product_id = serializer.validated_data['product_id']
        quantity = serializer.validated_data['quantity']
        
        # Vérifier si l'article existe déjà dans le panier
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product_id=product_id,
            defaults={'quantity': quantity}
        )
        
        if not created:
            # Mettre à jour la quantité si l'article existe déjà
            cart_item.quantity += quantity
            cart_item.save()
            serializer.instance = cart_item


class CartItemUpdateView(generics.UpdateAPIView):
    """Vue pour mettre à jour un article du panier"""
    
    serializer_class = CartItemSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return CartItem.objects.filter(cart__user=self.request.user)


class CartItemDeleteView(generics.DestroyAPIView):
    """Vue pour supprimer un article du panier"""
    
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return CartItem.objects.filter(cart__user=self.request.user)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_to_cart_view(request, product_id):
    """Vue pour ajouter un produit au panier"""
    
    try:
        product = Product.objects.get(id=product_id, status='published')
    except Product.DoesNotExist:
        return Response(
            {'error': _('Produit non trouvé.')}, 
            status=status.HTTP_404_NOT_FOUND
        )
    
    if not product.is_in_stock:
        return Response(
            {'error': _('Ce produit n\'est pas disponible.')}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    quantity = request.data.get('quantity', 1)
    if quantity < 1:
        return Response(
            {'error': _('La quantité doit être supérieure à 0.')}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    cart, created = Cart.objects.get_or_create(user=request.user)
    
    # Vérifier si l'article existe déjà dans le panier
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        defaults={'quantity': quantity}
    )
    
    if not created:
        # Mettre à jour la quantité si l'article existe déjà
        cart_item.quantity += quantity
        cart_item.save()
    
    serializer = CartItemSerializer(cart_item)
    return Response({
        'message': _('Produit ajouté au panier avec succès.'),
        'cart_item': serializer.data
    })


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def remove_from_cart_view(request, product_id):
    """Vue pour retirer un produit du panier"""
    
    try:
        cart_item = CartItem.objects.get(
            cart__user=request.user,
            product_id=product_id
        )
        cart_item.delete()
        
        return Response({
            'message': _('Produit retiré du panier avec succès.')
        })
    except CartItem.DoesNotExist:
        return Response(
            {'error': _('Article non trouvé dans le panier.')}, 
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def clear_cart_view(request):
    """Vue pour vider le panier"""
    
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart.items.all().delete()
    
    return Response({
        'message': _('Panier vidé avec succès.')
    })


# Vues pour la liste de souhaits
class WishlistView(generics.RetrieveAPIView):
    """Vue pour récupérer la liste de souhaits de l'utilisateur"""
    
    serializer_class = WishlistSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        wishlist, created = Wishlist.objects.get_or_create(user=self.request.user)
        return wishlist


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_to_wishlist_view(request, product_id):
    """Vue pour ajouter un produit à la liste de souhaits"""
    
    try:
        product = Product.objects.get(id=product_id, status='published')
    except Product.DoesNotExist:
        return Response(
            {'error': _('Produit non trouvé.')}, 
            status=status.HTTP_404_NOT_FOUND
        )
    
    wishlist, created = Wishlist.objects.get_or_create(user=request.user)
    
    # Vérifier si le produit est déjà dans la liste de souhaits
    wishlist_item, created = WishlistItem.objects.get_or_create(
        wishlist=wishlist,
        product=product
    )
    
    if created:
        serializer = WishlistItemSerializer(wishlist_item)
        return Response({
            'message': _('Produit ajouté à la liste de souhaits avec succès.'),
            'wishlist_item': serializer.data
        })
    else:
        return Response({
            'message': _('Ce produit est déjà dans votre liste de souhaits.')
        })


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def remove_from_wishlist_view(request, product_id):
    """Vue pour retirer un produit de la liste de souhaits"""
    
    try:
        wishlist_item = WishlistItem.objects.get(
            wishlist__user=request.user,
            product_id=product_id
        )
        wishlist_item.delete()
        
        return Response({
            'message': _('Produit retiré de la liste de souhaits avec succès.')
        })
    except WishlistItem.DoesNotExist:
        return Response(
            {'error': _('Produit non trouvé dans la liste de souhaits.')}, 
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def move_to_cart_view(request, product_id):
    """Vue pour déplacer un produit de la liste de souhaits vers le panier"""
    
    try:
        wishlist_item = WishlistItem.objects.get(
            wishlist__user=request.user,
            product_id=product_id
        )
        product = wishlist_item.product
        
        if not product.is_in_stock:
            return Response(
                {'error': _('Ce produit n\'est pas disponible.')}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Ajouter au panier
        cart, created = Cart.objects.get_or_create(user=request.user)
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'quantity': 1}
        )
        
        if not created:
            cart_item.quantity += 1
            cart_item.save()
        
        # Retirer de la liste de souhaits
        wishlist_item.delete()
        
        return Response({
            'message': _('Produit déplacé vers le panier avec succès.')
        })
    except WishlistItem.DoesNotExist:
        return Response(
            {'error': _('Produit non trouvé dans la liste de souhaits.')}, 
            status=status.HTTP_404_NOT_FOUND
        )


# Vues de base pour le panier
class CartPageView(LoginRequiredMixin, TemplateView):
    """Vue de la page panier"""
    template_name = 'cart/cart.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart, created = Cart.objects.get_or_create(user=self.request.user)
        context['cart'] = cart
        context['cart_items'] = cart.items.select_related('product').all()
        return context


class WishlistPageView(LoginRequiredMixin, TemplateView):
    """Vue de la page liste de souhaits"""
    template_name = 'cart/wishlist.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        wishlist, created = Wishlist.objects.get_or_create(user=self.request.user)
        context['wishlist'] = wishlist
        context['wishlist_items'] = wishlist.items.select_related('product').all()
        return context


@login_required
def add_to_cart_page_view(request, product_id):
    """Vue pour ajouter un produit au panier (page)"""
    try:
        product = Product.objects.get(id=product_id, status='published')
    except Product.DoesNotExist:
        messages.error(request, 'Produit non trouvé.')
        return redirect('core:home')
    
    if not product.is_in_stock:
        messages.error(request, 'Ce produit n\'est pas disponible.')
        return redirect('products:product-detail', slug=product.slug)
    
    quantity = int(request.POST.get('quantity', 1))
    if quantity < 1:
        messages.error(request, 'La quantité doit être supérieure à 0.')
        return redirect('products:product-detail', slug=product.slug)
    
    cart, created = Cart.objects.get_or_create(user=request.user)
    
    # Vérifier si l'article existe déjà dans le panier
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        defaults={'quantity': quantity}
    )
    
    if not created:
        # Mettre à jour la quantité si l'article existe déjà
        cart_item.quantity += quantity
        cart_item.save()
        messages.success(request, f'Quantité mise à jour pour {product.name}.')
    else:
        messages.success(request, f'{product.name} ajouté au panier.')
    
    return redirect('cart:cart')


@login_required
def remove_from_cart_page_view(request, product_id):
    """Vue pour retirer un produit du panier (page)"""
    try:
        cart_item = CartItem.objects.get(
            cart__user=request.user,
            product_id=product_id
        )
        product_name = cart_item.product.name
        cart_item.delete()
        messages.success(request, f'{product_name} retiré du panier.')
    except CartItem.DoesNotExist:
        messages.error(request, 'Article non trouvé dans le panier.')
    
    return redirect('cart:cart')


@login_required
def update_cart_item_view(request, product_id):
    """Vue pour mettre à jour la quantité d'un article du panier"""
    try:
        cart_item = CartItem.objects.get(
            cart__user=request.user,
            product_id=product_id
        )
        quantity = int(request.POST.get('quantity', 1))
        
        if quantity <= 0:
            cart_item.delete()
            messages.success(request, f'{cart_item.product.name} retiré du panier.')
        else:
            cart_item.quantity = quantity
            cart_item.save()
            messages.success(request, f'Quantité mise à jour pour {cart_item.product.name}.')
    except CartItem.DoesNotExist:
        messages.error(request, 'Article non trouvé dans le panier.')
    except ValueError:
        messages.error(request, 'Quantité invalide.')
    
    return redirect('cart:cart')


@login_required
def add_to_wishlist_page_view(request, product_id):
    """Vue pour ajouter un produit à la liste de souhaits (page)"""
    try:
        product = Product.objects.get(id=product_id, status='published')
    except Product.DoesNotExist:
        messages.error(request, 'Produit non trouvé.')
        return redirect('core:home')
    
    wishlist, created = Wishlist.objects.get_or_create(user=request.user)
    
    # Vérifier si le produit est déjà dans la liste de souhaits
    wishlist_item, created = WishlistItem.objects.get_or_create(
        wishlist=wishlist,
        product=product
    )
    
    if created:
        messages.success(request, f'{product.name} ajouté à votre liste de souhaits.')
    else:
        messages.info(request, f'{product.name} est déjà dans votre liste de souhaits.')
    
    return redirect(request.META.get('HTTP_REFERER', 'core:home'))


@login_required
def remove_from_wishlist_page_view(request, product_id):
    """Vue pour retirer un produit de la liste de souhaits (page)"""
    try:
        wishlist_item = WishlistItem.objects.get(
            wishlist__user=request.user,
            product_id=product_id
        )
        product_name = wishlist_item.product.name
        wishlist_item.delete()
        messages.success(request, f'{product_name} retiré de votre liste de souhaits.')
    except WishlistItem.DoesNotExist:
        messages.error(request, 'Produit non trouvé dans la liste de souhaits.')
    
    return redirect('cart:wishlist')
