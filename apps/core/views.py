from django.shortcuts import render
from django.http import JsonResponse
from django.views.generic import TemplateView
from django.utils.translation import gettext_lazy as _
from apps.products.models import Product, Category, Brand
from apps.orders.models import Order


class HomeView(TemplateView):
    """Vue d'accueil"""
    
    template_name = 'core/home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Produits en vedette
        context['featured_products'] = Product.objects.filter(
            status='published',
            is_featured=True
        ).select_related('category', 'brand').prefetch_related('images')[:8]
        
        # Nouvelles catégories
        context['categories'] = Category.objects.filter(
            is_active=True,
            parent__isnull=True
        )[:6]
        
        # Marques populaires
        context['brands'] = Brand.objects.filter(is_active=True)[:8]
        
        return context


class AboutView(TemplateView):
    """Vue à propos"""
    
    template_name = 'core/about.html'


class ContactView(TemplateView):
    """Vue contact"""
    
    template_name = 'core/contact.html'
    
    def post(self, request, *args, **kwargs):
        """Traiter le formulaire de contact"""
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        
        # Ici vous pouvez ajouter la logique d'envoi d'email
        # Pour l'instant, on simule un envoi réussi
        
        context = {
            'success_message': 'Votre message a été envoyé avec succès !',
            'name': name,
            'email': email,
            'subject': subject,
            'message': message
        }
        
        return render(request, self.template_name, context)


def api_stats_view(request):
    """Vue pour les statistiques de l'API"""
    
    stats = {
        'total_products': Product.objects.filter(status='published').count(),
        'total_categories': Category.objects.filter(is_active=True).count(),
        'total_brands': Brand.objects.filter(is_active=True).count(),
        'total_orders': Order.objects.count(),
    }
    
    return JsonResponse(stats)
