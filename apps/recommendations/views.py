from django.shortcuts import render
from django.views.generic import TemplateView
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

@method_decorator(login_required, name='dispatch')
class UserRecommendationsView(TemplateView):
    """Vue des recommandations pour l'utilisateur"""
    template_name = 'recommendations/user_recommendations.html'

@method_decorator(login_required, name='dispatch')
class SimilarProductsView(TemplateView):
    """Vue des produits similaires"""
    template_name = 'recommendations/similar_products.html'

@method_decorator(login_required, name='dispatch')
class FrequentlyBoughtTogetherView(TemplateView):
    """Vue des produits fréquemment achetés ensemble"""
    template_name = 'recommendations/frequently_bought_together.html'

def api_user_recommendations(request):
    """API pour les recommandations utilisateur"""
    return JsonResponse({'recommendations': []})

def api_similar_products(request):
    """API pour les produits similaires"""
    return JsonResponse({'products': []})

def api_recommendation_feedback(request):
    """API pour le feedback des recommandations"""
    return JsonResponse({'status': 'success'})

