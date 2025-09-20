from django.shortcuts import render
from django.views.generic import TemplateView
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

@method_decorator(login_required, name='dispatch')
class AdvancedSearchView(TemplateView):
    """Vue de recherche avancée"""
    template_name = 'search/advanced_search.html'

@method_decorator(login_required, name='dispatch')
class SearchResultsView(TemplateView):
    """Vue des résultats de recherche"""
    template_name = 'search/results.html'

@method_decorator(login_required, name='dispatch')
class SearchHistoryView(TemplateView):
    """Vue de l'historique de recherche"""
    template_name = 'search/history.html'

@method_decorator(login_required, name='dispatch')
class PopularSearchesView(TemplateView):
    """Vue des recherches populaires"""
    template_name = 'search/popular.html'

def api_search_suggestions(request):
    """API pour les suggestions de recherche"""
    return JsonResponse({'suggestions': []})

def api_autocomplete(request):
    """API pour l'autocomplétion"""
    return JsonResponse({'results': []})