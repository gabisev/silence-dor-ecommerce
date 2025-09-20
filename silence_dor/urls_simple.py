"""
URL configuration for silence_dor project (version simplifiée)
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.core.urls')),
    path('products/', include('apps.products.urls')),
    path('accounts/', include('apps.accounts.urls')),
    path('orders/', include('apps.orders.urls')),
    path('cart/', include('apps.cart.urls')),
    
    # Nouvelles fonctionnalités avancées
    path('analytics/', include('apps.analytics.urls')),
    path('search/', include('apps.search.urls')),
    path('notifications/', include('apps.notifications.urls')),
    path('recommendations/', include('apps.recommendations.urls')),
    path('security/', include('apps.security.urls')),
    path('inventory/', include('apps.inventory.urls')),
    path('marketing/', include('apps.marketing.urls')),
    path('pwa/', include('apps.pwa.urls')),
    path('automation/', include('apps.automation.urls')),
    path('i18n/', include('apps.i18n.urls')),
    
    # path('api/', include('apps.payments.urls')),  # Désactivé pour éviter les erreurs Stripe
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
