from django.urls import path
from . import views

app_name = 'i18n'

urlpatterns = [
    # Gestion des langues et devises
    path('languages/', views.LanguageListView.as_view(), name='language-list'),
    path('currencies/', views.CurrencyListView.as_view(), name='currency-list'),
    path('countries/', views.CountryListView.as_view(), name='country-list'),
    
    # Zones de livraison
    path('shipping-zones/', views.ShippingZoneListView.as_view(), name='shipping-zone-list'),
    path('shipping-methods/', views.ShippingMethodListView.as_view(), name='shipping-method-list'),
    
    # Règles de taxation
    path('tax-rules/', views.TaxRuleListView.as_view(), name='tax-rule-list'),
    
    # API
    path('api/change-language/', views.api_change_language, name='api-change-language'),
    path('api/change-currency/', views.api_change_currency, name='api-change-currency'),
    path('api/countries/', views.api_countries, name='api-countries'),
]

