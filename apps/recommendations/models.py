from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

User = get_user_model()


class UserBehavior(models.Model):
    """Comportement utilisateur pour les recommandations"""
    
    BEHAVIOR_TYPES = [
        ('view', _('Vue')),
        ('add_to_cart', _('Ajout au panier')),
        ('remove_from_cart', _('Retrait du panier')),
        ('add_to_wishlist', _('Ajout aux favoris')),
        ('remove_from_wishlist', _('Retrait des favoris')),
        ('purchase', _('Achat')),
        ('review', _('Avis')),
        ('share', _('Partage')),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    session_key = models.CharField(_('clé de session'), max_length=40, blank=True)
    
    # Objet concerné (produit, catégorie, etc.)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    
    behavior_type = models.CharField(_('type de comportement'), max_length=20, choices=BEHAVIOR_TYPES)
    weight = models.FloatField(_('poids'), default=1.0)  # Poids de l'action
    metadata = models.JSONField(_('métadonnées'), default=dict, blank=True)
    timestamp = models.DateTimeField(_('horodatage'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('Comportement utilisateur')
        verbose_name_plural = _('Comportements utilisateur')
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', 'behavior_type']),
            models.Index(fields=['session_key', 'behavior_type']),
            models.Index(fields=['content_type', 'object_id']),
            models.Index(fields=['timestamp']),
        ]
    
    def __str__(self):
        return f"{self.get_behavior_type_display()} - {self.content_object}"


class ProductSimilarity(models.Model):
    """Similarité entre produits"""
    
    product1 = models.ForeignKey('products.Product', on_delete=models.CASCADE, related_name='similarities_as_product1')
    product2 = models.ForeignKey('products.Product', on_delete=models.CASCADE, related_name='similarities_as_product2')
    similarity_score = models.FloatField(_('score de similarité'), default=0.0)
    similarity_type = models.CharField(_('type de similarité'), max_length=50, default='content_based')
    created_at = models.DateTimeField(_('créé le'), auto_now_add=True)
    updated_at = models.DateTimeField(_('modifié le'), auto_now=True)
    
    class Meta:
        verbose_name = _('Similarité produit')
        verbose_name_plural = _('Similarités produit')
        unique_together = ['product1', 'product2']
        ordering = ['-similarity_score']
    
    def __str__(self):
        return f"{self.product1.name} ~ {self.product2.name} ({self.similarity_score:.2f})"


class UserProfile(models.Model):
    """Profil utilisateur pour les recommandations"""
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='recommendation_profile')
    
    # Préférences
    preferred_categories = models.JSONField(_('catégories préférées'), default=list, blank=True)
    preferred_brands = models.JSONField(_('marques préférées'), default=list, blank=True)
    price_range_min = models.DecimalField(_('prix minimum'), max_digits=10, decimal_places=2, null=True, blank=True)
    price_range_max = models.DecimalField(_('prix maximum'), max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Comportement
    total_views = models.PositiveIntegerField(_('total vues'), default=0)
    total_purchases = models.PositiveIntegerField(_('total achats'), default=0)
    total_spent = models.DecimalField(_('total dépensé'), max_digits=12, decimal_places=2, default=0)
    average_order_value = models.DecimalField(_('panier moyen'), max_digits=10, decimal_places=2, default=0)
    
    # Métriques de recommandation
    last_recommendation_update = models.DateTimeField(_('dernière mise à jour recommandations'), null=True, blank=True)
    recommendation_accuracy = models.FloatField(_('précision des recommandations'), default=0.0)
    
    created_at = models.DateTimeField(_('créé le'), auto_now_add=True)
    updated_at = models.DateTimeField(_('modifié le'), auto_now=True)
    
    class Meta:
        verbose_name = _('Profil de recommandation')
        verbose_name_plural = _('Profils de recommandation')
    
    def __str__(self):
        return f"Profil de {self.user.email}"


class Recommendation(models.Model):
    """Recommandations générées pour les utilisateurs"""
    
    RECOMMENDATION_TYPES = [
        ('collaborative', _('Collaborative Filtering')),
        ('content_based', _('Content-Based')),
        ('hybrid', _('Hybride')),
        ('popularity', _('Popularité')),
        ('trending', _('Tendance')),
        ('frequently_bought_together', _('Achetés ensemble')),
        ('similar_users', _('Utilisateurs similaires')),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recommendations')
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE, related_name='recommendations')
    
    recommendation_type = models.CharField(_('type de recommandation'), max_length=30, choices=RECOMMENDATION_TYPES)
    score = models.FloatField(_('score de recommandation'), default=0.0)
    reason = models.TextField(_('raison'), blank=True)
    
    # Métadonnées
    is_shown = models.BooleanField(_('affiché'), default=False)
    is_clicked = models.BooleanField(_('cliqué'), default=False)
    is_purchased = models.BooleanField(_('acheté'), default=False)
    
    created_at = models.DateTimeField(_('créé le'), auto_now_add=True)
    expires_at = models.DateTimeField(_('expire le'), null=True, blank=True)
    
    class Meta:
        verbose_name = _('Recommandation')
        verbose_name_plural = _('Recommandations')
        unique_together = ['user', 'product', 'recommendation_type']
        ordering = ['-score', '-created_at']
        indexes = [
            models.Index(fields=['user', 'recommendation_type']),
            models.Index(fields=['product', 'recommendation_type']),
            models.Index(fields=['score']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.email} - {self.product.name} ({self.get_recommendation_type_display()})"


class RecommendationRule(models.Model):
    """Règles de recommandation"""
    
    RULE_TYPES = [
        ('category_based', _('Basée sur la catégorie')),
        ('brand_based', _('Basée sur la marque')),
        ('price_based', _('Basée sur le prix')),
        ('seasonal', _('Saisonnière')),
        ('cross_sell', _('Vente croisée')),
        ('upsell', _('Vente incitative')),
    ]
    
    name = models.CharField(_('nom'), max_length=100)
    rule_type = models.CharField(_('type de règle'), max_length=20, choices=RULE_TYPES)
    description = models.TextField(_('description'), blank=True)
    
    # Conditions
    conditions = models.JSONField(_('conditions'), default=dict, blank=True)
    
    # Actions
    actions = models.JSONField(_('actions'), default=dict, blank=True)
    
    # Configuration
    is_active = models.BooleanField(_('actif'), default=True)
    priority = models.PositiveIntegerField(_('priorité'), default=0)
    weight = models.FloatField(_('poids'), default=1.0)
    
    # Métriques
    usage_count = models.PositiveIntegerField(_('nombre d\'utilisations'), default=0)
    success_rate = models.FloatField(_('taux de succès'), default=0.0)
    
    created_at = models.DateTimeField(_('créé le'), auto_now_add=True)
    updated_at = models.DateTimeField(_('modifié le'), auto_now=True)
    
    class Meta:
        verbose_name = _('Règle de recommandation')
        verbose_name_plural = _('Règles de recommandation')
        ordering = ['-priority', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.get_rule_type_display()})"


class RecommendationFeedback(models.Model):
    """Feedback sur les recommandations"""
    
    FEEDBACK_TYPES = [
        ('positive', _('Positif')),
        ('negative', _('Négatif')),
        ('neutral', _('Neutre')),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recommendation_feedback')
    recommendation = models.ForeignKey(Recommendation, on_delete=models.CASCADE, related_name='feedback')
    
    feedback_type = models.CharField(_('type de feedback'), max_length=10, choices=FEEDBACK_TYPES)
    comment = models.TextField(_('commentaire'), blank=True)
    
    timestamp = models.DateTimeField(_('horodatage'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('Feedback de recommandation')
        verbose_name_plural = _('Feedbacks de recommandation')
        unique_together = ['user', 'recommendation']
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.user.email} - {self.get_feedback_type_display()}"

