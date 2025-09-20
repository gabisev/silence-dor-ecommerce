from django.urls import path
from . import views

app_name = 'cart'

urlpatterns = [
    # Pages de base
    path('', views.CartPageView.as_view(), name='cart'),
    path('wishlist/', views.WishlistPageView.as_view(), name='wishlist'),
    
    # Actions panier
    path('add/<int:product_id>/', views.add_to_cart_page_view, name='add-to-cart'),
    path('remove/<int:product_id>/', views.remove_from_cart_page_view, name='remove-from-cart'),
    path('update/<int:product_id>/', views.update_cart_item_view, name='update-cart-item'),
    
    # Actions liste de souhaits
    path('wishlist/add/<int:product_id>/', views.add_to_wishlist_page_view, name='add-to-wishlist'),
    path('wishlist/remove/<int:product_id>/', views.remove_from_wishlist_page_view, name='remove-from-wishlist'),
    
    # API URLs
    path('api/', views.CartView.as_view(), name='cart-api'),
    path('api/items/', views.CartItemCreateView.as_view(), name='cart-item-create-api'),
    path('api/items/<int:pk>/', views.CartItemUpdateView.as_view(), name='cart-item-update-api'),
    path('api/items/<int:pk>/delete/', views.CartItemDeleteView.as_view(), name='cart-item-delete-api'),
    path('api/add/<int:product_id>/', views.add_to_cart_view, name='add-to-cart-api'),
    path('api/remove/<int:product_id>/', views.remove_from_cart_view, name='remove-from-cart-api'),
    path('api/clear/', views.clear_cart_view, name='clear-cart-api'),
    
    # Wishlist API URLs
    path('api/wishlist/', views.WishlistView.as_view(), name='wishlist-api'),
    path('api/wishlist/add/<int:product_id>/', views.add_to_wishlist_view, name='add-to-wishlist-api'),
    path('api/wishlist/remove/<int:product_id>/', views.remove_from_wishlist_view, name='remove-from-wishlist-api'),
    path('api/wishlist/move-to-cart/<int:product_id>/', views.move_to_cart_view, name='move-to-cart-api'),
]
