from .models import Cart


def cart(request):
    """Processeur de contexte pour le panier"""
    cart = None
    cart_items_count = 0
    cart_total = 0
    
    if request.user.is_authenticated:
        # Utilisateur connecté
        cart, created = Cart.objects.get_or_create(user=request.user)
    else:
        # Utilisateur anonyme - utiliser la session
        session_key = request.session.session_key
        if session_key:
            cart, created = Cart.objects.get_or_create(session_key=session_key)
    
    if cart:
        cart_items_count = cart.total_items
        cart_total = cart.total_price
    
    return {
        'cart': cart,
        'cart_items_count': cart_items_count,
        'cart_total': cart_total,
    }

