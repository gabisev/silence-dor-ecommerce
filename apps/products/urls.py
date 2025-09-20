from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    # Pages de base
    path('', views.ProductListView.as_view(), name='product-list'),
    path('search/', views.product_search_view, name='product-search'),
    path('<slug:slug>/', views.ProductDetailView.as_view(), name='product-detail'),
    
    # Catégories
    path('categories/', views.CategoryListView.as_view(), name='category-list'),
    path('categories/<slug:slug>/', views.CategoryDetailView.as_view(), name='category-detail'),
    path('category/<slug:category_slug>/', views.ProductListView.as_view(), name='product-list-by-category'),
    
    # Marques
    path('brands/', views.BrandListView.as_view(), name='brand-list'),
    path('brands/<slug:slug>/', views.BrandDetailView.as_view(), name='brand-detail'),
    path('brand/<slug:brand_slug>/', views.ProductListView.as_view(), name='product-list-by-brand'),
    
    # API URLs
    path('api/categories/', views.CategoryListView.as_view(), name='category-list-api'),
    path('api/categories/<slug:slug>/', views.CategoryDetailView.as_view(), name='category-detail-api'),
    path('api/brands/', views.BrandListView.as_view(), name='brand-list-api'),
    path('api/brands/<slug:slug>/', views.BrandDetailView.as_view(), name='brand-detail-api'),
    path('api/', views.ProductListView.as_view(), name='product-list-api'),
    path('api/<slug:slug>/', views.ProductDetailView.as_view(), name='product-detail-api'),
    path('api/create/', views.ProductCreateView.as_view(), name='product-create-api'),
    path('api/<slug:slug>/update/', views.ProductUpdateView.as_view(), name='product-update-api'),
    path('api/<slug:slug>/delete/', views.ProductDeleteView.as_view(), name='product-delete-api'),
    
    # Recherche et produits spéciaux API
    path('api/search/', views.product_search_view, name='product-search-api'),
    path('api/featured/', views.featured_products_view, name='featured-products-api'),
    path('api/<slug:product_slug>/related/', views.related_products_view, name='related-products-api'),
    path('api/<slug:product_slug>/stats/', views.product_stats_view, name='product-stats-api'),
    
    # Avis sur les produits API
    path('api/<slug:product_slug>/reviews/', views.ProductReviewListView.as_view(), name='product-reviews-api'),
    path('api/<slug:product_slug>/reviews/create/', views.ProductReviewCreateView.as_view(), name='product-review-create-api'),
]
