import math
from collections import defaultdict
from django.db.models import Q, Count, Avg, Sum
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from datetime import datetime, timedelta
from apps.products.models import Product, Category, Brand
from apps.orders.models import Order, OrderItem
from apps.cart.models import Cart, CartItem
from apps.accounts.models import User
from .models import UserBehavior, ProductSimilarity, UserProfile, Recommendation, RecommendationRule, RecommendationFeedback


class RecommendationService:
    """Service principal pour les recommandations"""
    
    @staticmethod
    def get_recommendations(user, limit=10, recommendation_types=None):
        """Retourne les recommandations pour un utilisateur"""
        if not user or not user.is_authenticated:
            return RecommendationService._get_popular_products(limit)
        
        # Récupérer les recommandations existantes
        recommendations = Recommendation.objects.filter(
            user=user,
            is_shown=False,
            expires_at__isnull=True
        ).select_related('product')
        
        if recommendation_types:
            recommendations = recommendations.filter(recommendation_type__in=recommendation_types)
        
        recommendations = recommendations.order_by('-score')[:limit]
        
        # Si pas assez de recommandations, en générer de nouvelles
        if len(recommendations) < limit:
            new_recommendations = RecommendationService._generate_recommendations(user, limit - len(recommendations))
            recommendations = list(recommendations) + new_recommendations
        
        return recommendations[:limit]
    
    @staticmethod
    def _get_popular_products(limit=10):
        """Retourne les produits populaires"""
        return Product.objects.filter(
            status='published',
            is_featured=True
        ).order_by('-created_at')[:limit]
    
    @staticmethod
    def _generate_recommendations(user, limit=10):
        """Génère de nouvelles recommandations pour un utilisateur"""
        recommendations = []
        
        # 1. Recommandations basées sur le contenu (produits similaires)
        content_based = RecommendationService._get_content_based_recommendations(user, limit//3)
        recommendations.extend(content_based)
        
        # 2. Recommandations collaboratives
        collaborative = RecommendationService._get_collaborative_recommendations(user, limit//3)
        recommendations.extend(collaborative)
        
        # 3. Recommandations basées sur la popularité
        popularity = RecommendationService._get_popularity_recommendations(user, limit//3)
        recommendations.extend(popularity)
        
        # 4. Recommandations "frequently bought together"
        fbt = RecommendationService._get_frequently_bought_together(user, limit//3)
        recommendations.extend(fbt)
        
        return recommendations[:limit]
    
    @staticmethod
    def _get_content_based_recommendations(user, limit=5):
        """Recommandations basées sur le contenu"""
        # Récupérer les produits que l'utilisateur a vus/achetés
        user_products = UserBehavior.objects.filter(
            user=user,
            behavior_type__in=['view', 'purchase', 'add_to_cart']
        ).values_list('object_id', flat=True)
        
        if not user_products:
            return []
        
        # Trouver des produits similaires
        similar_products = ProductSimilarity.objects.filter(
            product1_id__in=user_products,
            similarity_score__gte=0.3
        ).exclude(
            product2_id__in=user_products
        ).order_by('-similarity_score')[:limit]
        
        recommendations = []
        for similarity in similar_products:
            recommendation = Recommendation.objects.create(
                user=user,
                product=similarity.product2,
                recommendation_type='content_based',
                score=similarity.similarity_score,
                reason=f"Produit similaire à {similarity.product1.name}"
            )
            recommendations.append(recommendation)
        
        return recommendations
    
    @staticmethod
    def _get_collaborative_recommendations(user, limit=5):
        """Recommandations collaboratives"""
        # Trouver des utilisateurs similaires
        similar_users = RecommendationService._find_similar_users(user, limit=10)
        
        if not similar_users:
            return []
        
        # Récupérer les produits que ces utilisateurs ont achetés
        similar_user_ids = [u['user_id'] for u in similar_users]
        
        # Produits achetés par les utilisateurs similaires
        purchased_products = UserBehavior.objects.filter(
            user_id__in=similar_user_ids,
            behavior_type='purchase'
        ).values_list('object_id', flat=True)
        
        # Produits que l'utilisateur actuel n'a pas encore achetés
        user_purchased = UserBehavior.objects.filter(
            user=user,
            behavior_type='purchase'
        ).values_list('object_id', flat=True)
        
        recommended_product_ids = set(purchased_products) - set(user_purchased)
        
        recommendations = []
        for product_id in list(recommended_product_ids)[:limit]:
            try:
                product = Product.objects.get(id=product_id, status='published')
                recommendation = Recommendation.objects.create(
                    user=user,
                    product=product,
                    recommendation_type='collaborative',
                    score=0.7,  # Score par défaut
                    reason="Recommandé par des utilisateurs similaires"
                )
                recommendations.append(recommendation)
            except Product.DoesNotExist:
                continue
        
        return recommendations
    
    @staticmethod
    def _get_popularity_recommendations(user, limit=5):
        """Recommandations basées sur la popularité"""
        # Produits populaires que l'utilisateur n'a pas encore vus
        user_viewed = UserBehavior.objects.filter(
            user=user,
            behavior_type='view'
        ).values_list('object_id', flat=True)
        
        popular_products = Product.objects.filter(
            status='published'
        ).exclude(
            id__in=user_viewed
        ).annotate(
            popularity=Count('userbehavior')
        ).order_by('-popularity')[:limit]
        
        recommendations = []
        for product in popular_products:
            recommendation = Recommendation.objects.create(
                user=user,
                product=product,
                recommendation_type='popularity',
                score=0.6,
                reason="Produit populaire"
            )
            recommendations.append(recommendation)
        
        return recommendations
    
    @staticmethod
    def _get_frequently_bought_together(user, limit=5):
        """Produits fréquemment achetés ensemble"""
        # Récupérer les commandes de l'utilisateur
        user_orders = Order.objects.filter(user=user, status__in=['completed', 'delivered'])
        
        if not user_orders.exists():
            return []
        
        # Produits achetés par l'utilisateur
        user_products = OrderItem.objects.filter(
            order__in=user_orders
        ).values_list('product_id', flat=True)
        
        # Trouver des produits fréquemment achetés avec ces produits
        fbt_products = OrderItem.objects.filter(
            order__in=Order.objects.filter(
                orderitem__product_id__in=user_products
            ).exclude(user=user)
        ).exclude(
            product_id__in=user_products
        ).values('product_id').annotate(
            frequency=Count('product_id')
        ).order_by('-frequency')[:limit]
        
        recommendations = []
        for item in fbt_products:
            try:
                product = Product.objects.get(id=item['product_id'], status='published')
                recommendation = Recommendation.objects.create(
                    user=user,
                    product=product,
                    recommendation_type='frequently_bought_together',
                    score=0.8,
                    reason="Fréquemment acheté ensemble"
                )
                recommendations.append(recommendation)
            except Product.DoesNotExist:
                continue
        
        return recommendations
    
    @staticmethod
    def _find_similar_users(user, limit=10):
        """Trouve des utilisateurs similaires"""
        # Récupérer les produits que l'utilisateur a achetés
        user_products = UserBehavior.objects.filter(
            user=user,
            behavior_type='purchase'
        ).values_list('object_id', flat=True)
        
        if not user_products:
            return []
        
        # Trouver d'autres utilisateurs qui ont acheté les mêmes produits
        similar_users = UserBehavior.objects.filter(
            behavior_type='purchase',
            object_id__in=user_products
        ).exclude(
            user=user
        ).values('user_id').annotate(
            common_products=Count('object_id')
        ).order_by('-common_products')[:limit]
        
        return list(similar_users)


class BehaviorTrackingService:
    """Service pour le tracking du comportement utilisateur"""
    
    @staticmethod
    def track_behavior(user, session_key, content_object, behavior_type, weight=1.0, metadata=None):
        """Enregistre un comportement utilisateur"""
        content_type = ContentType.objects.get_for_model(content_object)
        
        behavior = UserBehavior.objects.create(
            user=user,
            session_key=session_key,
            content_type=content_type,
            object_id=content_object.id,
            behavior_type=behavior_type,
            weight=weight,
            metadata=metadata or {}
        )
        
        # Mettre à jour le profil utilisateur
        if user and user.is_authenticated:
            RecommendationService._update_user_profile(user, behavior_type, content_object)
        
        return behavior
    
    @staticmethod
    def track_product_view(user, session_key, product):
        """Enregistre une vue de produit"""
        return BehaviorTrackingService.track_behavior(
            user, session_key, product, 'view', weight=1.0
        )
    
    @staticmethod
    def track_add_to_cart(user, session_key, product):
        """Enregistre un ajout au panier"""
        return BehaviorTrackingService.track_behavior(
            user, session_key, product, 'add_to_cart', weight=2.0
        )
    
    @staticmethod
    def track_purchase(user, session_key, product, order_value=None):
        """Enregistre un achat"""
        metadata = {'order_value': order_value} if order_value else {}
        return BehaviorTrackingService.track_behavior(
            user, session_key, product, 'purchase', weight=5.0, metadata=metadata
        )


class SimilarityService:
    """Service pour calculer la similarité entre produits"""
    
    @staticmethod
    def calculate_product_similarity(product1, product2):
        """Calcule la similarité entre deux produits"""
        similarity_score = 0.0
        
        # Similarité basée sur la catégorie
        if product1.category == product2.category:
            similarity_score += 0.3
        
        # Similarité basée sur la marque
        if product1.brand == product2.brand:
            similarity_score += 0.2
        
        # Similarité basée sur le prix (plus le prix est proche, plus la similarité est élevée)
        if product1.price and product2.price:
            price_diff = abs(float(product1.price) - float(product2.price))
            max_price = max(float(product1.price), float(product2.price))
            if max_price > 0:
                price_similarity = 1 - (price_diff / max_price)
                similarity_score += price_similarity * 0.2
        
        # Similarité basée sur les tags/mots-clés
        if hasattr(product1, 'tags') and hasattr(product2, 'tags'):
            tags1 = set(product1.tags.all()) if product1.tags.exists() else set()
            tags2 = set(product2.tags.all()) if product2.tags.exists() else set()
            
            if tags1 or tags2:
                common_tags = tags1.intersection(tags2)
                total_tags = tags1.union(tags2)
                tag_similarity = len(common_tags) / len(total_tags) if total_tags else 0
                similarity_score += tag_similarity * 0.3
        
        return min(similarity_score, 1.0)
    
    @staticmethod
    def update_product_similarities(product):
        """Met à jour les similarités pour un produit"""
        # Récupérer tous les autres produits
        other_products = Product.objects.filter(
            status='published'
        ).exclude(id=product.id)
        
        for other_product in other_products:
            similarity_score = SimilarityService.calculate_product_similarity(product, other_product)
            
            if similarity_score > 0.1:  # Seuil minimum
                ProductSimilarity.objects.update_or_create(
                    product1=product,
                    product2=other_product,
                    defaults={
                        'similarity_score': similarity_score,
                        'similarity_type': 'content_based'
                    }
                )
                
                # Créer aussi la relation inverse
                ProductSimilarity.objects.update_or_create(
                    product1=other_product,
                    product2=product,
                    defaults={
                        'similarity_score': similarity_score,
                        'similarity_type': 'content_based'
                    }
                )
    
    @staticmethod
    def get_similar_products(product, limit=5):
        """Retourne les produits similaires à un produit donné"""
        similarities = ProductSimilarity.objects.filter(
            product1=product,
            similarity_score__gte=0.3
        ).order_by('-similarity_score')[:limit]
        
        return [similarity.product2 for similarity in similarities]


class RecommendationFeedbackService:
    """Service pour gérer le feedback sur les recommandations"""
    
    @staticmethod
    def record_feedback(user, recommendation, feedback_type, comment=None):
        """Enregistre un feedback sur une recommandation"""
        feedback, created = RecommendationFeedback.objects.get_or_create(
            user=user,
            recommendation=recommendation,
            defaults={
                'feedback_type': feedback_type,
                'comment': comment or ''
            }
        )
        
        if not created:
            feedback.feedback_type = feedback_type
            feedback.comment = comment or ''
            feedback.save()
        
        # Mettre à jour la précision des recommandations
        RecommendationService._update_recommendation_accuracy(user)
        
        return feedback
    
    @staticmethod
    def get_recommendation_accuracy(user):
        """Retourne la précision des recommandations pour un utilisateur"""
        try:
            profile = UserProfile.objects.get(user=user)
            return profile.recommendation_accuracy
        except UserProfile.DoesNotExist:
            return 0.0

