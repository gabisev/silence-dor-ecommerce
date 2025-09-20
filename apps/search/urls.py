from django.urls import path
from . import views

app_name = 'search'

urlpatterns = [
    # Recherche avancée
    path('', views.AdvancedSearchView.as_view(), name='advanced-search'),
    path('results/', views.SearchResultsView.as_view(), name='search-results'),
    
    # API pour l'autocomplétion
    path('api/suggestions/', views.api_search_suggestions, name='api-suggestions'),
    path('api/autocomplete/', views.api_autocomplete, name='api-autocomplete'),
    
    # Historique et analytics
    path('history/', views.SearchHistoryView.as_view(), name='search-history'),
    path('popular/', views.PopularSearchesView.as_view(), name='popular-searches'),
]