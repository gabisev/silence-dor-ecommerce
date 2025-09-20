from django.urls import path
from . import views

app_name = 'recommendations'

urlpatterns = [
    # Recommandations pour l'utilisateur
    path('for-me/', views.UserRecommendationsView.as_view(), name='user-recommendations'),
    path('similar/<int:product_id>/', views.SimilarProductsView.as_view(), name='similar-products'),
    path('frequently-bought-together/<int:product_id>/', views.FrequentlyBoughtTogetherView.as_view(), name='frequently-bought-together'),
    
    # API
    path('api/recommendations/', views.api_user_recommendations, name='api-recommendations'),
    path('api/similar/', views.api_similar_products, name='api-similar'),
    path('api/feedback/', views.api_recommendation_feedback, name='api-feedback'),
]

