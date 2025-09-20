import re
from django.db.models import Q, F, Count, Avg
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from datetime import datetime, timedelta
from apps.products.models import Product, Category, Brand
from apps.search.models import SearchIndex, SearchSuggestion, SearchHistory, SearchAnalytics
from apps.analytics.services import TrackingService


class SearchService:
    """Service pour la recherche avancée"""
    
    @staticmethod
    def build_search_query(query, filters=None, user=None, session_key=None):
        """Construit une requête de recherche complexe"""
        if not query.strip():
            return Product.objects.none()
        
        # Nettoyer la requête
        clean_query = SearchService._clean_query(query)
        
        # Recherche dans l'index
        search_terms = clean_query.split()
        q_objects = Q()
        
        for term in search_terms:
            # Recherche dans le titre (poids élevé)
            q_objects |= Q(title__icontains=term)
            # Recherche dans la description
            q_objects |= Q(description__icontains=term)
            # Recherche dans les mots-clés
            q_objects |= Q(keywords__icontains=term)
            # Recherche dans les tags
            q_objects |= Q(tags__icontains=term)
            # Recherche dans la catégorie
            q_objects |= Q(category__icontains=term)
            # Recherche dans la marque
            q_objects |= Q(brand__icontains=term)
        
        # Filtrer par index actif
        search_results = SearchIndex.objects.filter(
            q_objects,
            is_active=True
        ).select_related('content_object')
        
        # Appliquer les filtres
        if filters:
            search_results = SearchService._apply_filters(search_results, filters)
        
        # Trier par pertinence et popularité
        search_results = search_results.order_by('-popularity_score', 'title')
        
        # Enregistrer la recherche
        SearchService._log_search(query, filters, user, session_key, search_results.count())
        
        # Mettre à jour les suggestions
        SearchService._update_suggestions(query)
        
        return search_results
    
    @staticmethod
    def _clean_query(query):
        """Nettoie la requête de recherche"""
        # Supprimer les caractères spéciaux
        clean_query = re.sub(r'[^\w\s]', ' ', query)
        # Supprimer les espaces multiples
        clean_query = re.sub(r'\s+', ' ', clean_query)
        return clean_query.strip()
    
    @staticmethod
    def _apply_filters(search_results, filters):
        """Applique les filtres à la recherche"""
        if 'category' in filters:
            search_results = search_results.filter(category__in=filters['category'])
        
        if 'brand' in filters:
            search_results = search_results.filter(brand__in=filters['brand'])
        
        if 'price_min' in filters:
            search_results = search_results.filter(price__gte=filters['price_min'])
        
        if 'price_max' in filters:
            search_results = search_results.filter(price__lte=filters['price_max'])
        
        if 'availability' in filters:
            if filters['availability'] == 'in_stock':
                # Logique pour vérifier le stock
                pass
        
        return search_results
    
    @staticmethod
    def _log_search(query, filters, user, session_key, results_count):
        """Enregistre la recherche dans l'historique"""
        SearchHistory.objects.create(
            user=user,
            session_key=session_key,
            query=query,
            filters=filters or {},
            results_count=results_count
        )
        
        # Tracking analytics
        TrackingService.track_search(None, query, results_count)
    
    @staticmethod
    def _update_suggestions(query):
        """Met à jour les suggestions de recherche"""
        suggestion, created = SearchSuggestion.objects.get_or_create(
            query=query.lower(),
            defaults={'count': 1}
        )
        
        if not created:
            suggestion.count += 1
            suggestion.save()
    
    @staticmethod
    def get_suggestions(query, limit=10):
        """Retourne des suggestions de recherche"""
        if len(query) < 2:
            return []
        
        suggestions = SearchSuggestion.objects.filter(
            query__icontains=query,
            is_active=True
        ).order_by('-count', '-last_used')[:limit]
        
        return [suggestion.query for suggestion in suggestions]
    
    @staticmethod
    def get_popular_searches(limit=10):
        """Retourne les recherches populaires"""
        return SearchSuggestion.objects.filter(
            is_active=True
        ).order_by('-count', '-last_used')[:limit]
    
    @staticmethod
    def get_search_history(user=None, session_key=None, limit=10):
        """Retourne l'historique de recherche"""
        queryset = SearchHistory.objects.all()
        
        if user:
            queryset = queryset.filter(user=user)
        elif session_key:
            queryset = queryset.filter(session_key=session_key)
        else:
            return []
        
        return queryset.order_by('-timestamp')[:limit]
    
    @staticmethod
    def index_product(product):
        """Indexe un produit pour la recherche"""
        content_type = ContentType.objects.get_for_model(Product)
        
        # Créer ou mettre à jour l'index
        search_index, created = SearchIndex.objects.get_or_create(
            content_type=content_type,
            object_id=product.id,
            defaults={
                'title': product.name,
                'description': product.description,
                'keywords': f"{product.name} {product.description} {product.sku}",
                'category': product.category.name if product.category else '',
                'brand': product.brand.name if product.brand else '',
                'tags': ', '.join([tag.name for tag in getattr(product, 'tags', [])]),
                'price': product.price,
                'is_active': product.status == 'published',
            }
        )
        
        if not created:
            # Mettre à jour l'index existant
            search_index.title = product.name
            search_index.description = product.description
            search_index.keywords = f"{product.name} {product.description} {product.sku}"
            search_index.category = product.category.name if product.category else ''
            search_index.brand = product.brand.name if product.brand else ''
            search_index.price = product.price
            search_index.is_active = product.status == 'published'
            search_index.save()
        
        return search_index
    
    @staticmethod
    def update_popularity_score(product_id, increment=1):
        """Met à jour le score de popularité d'un produit"""
        try:
            content_type = ContentType.objects.get_for_model(Product)
            search_index = SearchIndex.objects.get(
                content_type=content_type,
                object_id=product_id
            )
            search_index.popularity_score += increment
            search_index.save()
        except SearchIndex.DoesNotExist:
            pass
    
    @staticmethod
    def get_search_analytics(days=30):
        """Retourne les analytics de recherche"""
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=days)
        
        # Recherches populaires
        popular_searches = SearchSuggestion.objects.filter(
            is_active=True
        ).order_by('-count')[:10]
        
        # Recherches récentes
        recent_searches = SearchHistory.objects.filter(
            timestamp__date__gte=start_date
        ).values('query').annotate(
            count=Count('query')
        ).order_by('-count')[:10]
        
        # Recherches sans résultats
        no_results_searches = SearchHistory.objects.filter(
            results_count=0,
            timestamp__date__gte=start_date
        ).values('query').annotate(
            count=Count('query')
        ).order_by('-count')[:10]
        
        return {
            'popular_searches': list(popular_searches.values('query', 'count')),
            'recent_searches': list(recent_searches),
            'no_results_searches': list(no_results_searches),
        }


class AutocompleteService:
    """Service pour l'autocomplétion"""
    
    @staticmethod
    def get_autocomplete_suggestions(query, limit=5):
        """Retourne des suggestions d'autocomplétion"""
        if len(query) < 2:
            return []
        
        suggestions = []
        
        # Suggestions basées sur les recherches populaires
        popular_suggestions = SearchSuggestion.objects.filter(
            query__icontains=query,
            is_active=True
        ).order_by('-count')[:limit//2]
        
        for suggestion in popular_suggestions:
            suggestions.append({
                'text': suggestion.query,
                'type': 'popular',
                'count': suggestion.count
            })
        
        # Suggestions basées sur les noms de produits
        product_suggestions = SearchIndex.objects.filter(
            title__icontains=query,
            is_active=True
        ).order_by('-popularity_score')[:limit//2]
        
        for product in product_suggestions:
            suggestions.append({
                'text': product.title,
                'type': 'product',
                'category': product.category,
                'price': float(product.price) if product.price else None
            })
        
        # Suggestions basées sur les catégories
        category_suggestions = SearchIndex.objects.filter(
            category__icontains=query,
            is_active=True
        ).values('category').distinct()[:3]
        
        for category in category_suggestions:
            if category['category']:
                suggestions.append({
                    'text': category['category'],
                    'type': 'category'
                })
        
        return suggestions[:limit]
    
    @staticmethod
    def get_quick_filters():
        """Retourne les filtres rapides disponibles"""
        return {
            'categories': list(Category.objects.filter(is_active=True).values('name', 'slug')),
            'brands': list(Brand.objects.filter(is_active=True).values('name', 'slug')),
            'price_ranges': [
                {'label': 'Moins de 50€', 'min': 0, 'max': 50},
                {'label': '50€ - 100€', 'min': 50, 'max': 100},
                {'label': '100€ - 200€', 'min': 100, 'max': 200},
                {'label': 'Plus de 200€', 'min': 200, 'max': None},
            ]
        }

