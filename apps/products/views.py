from rest_framework import generics, filters, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Avg, Count
from django.utils.translation import gettext_lazy as _
from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from .models import (
    Category, Brand, Product, ProductImage, 
    ProductAttribute, ProductAttributeValue, ProductReview
)
from .serializers import (
    CategorySerializer, BrandSerializer, ProductListSerializer,
    ProductDetailSerializer, ProductCreateUpdateSerializer,
    ProductAttributeSerializer, ProductReviewSerializer
)
from .filters import ProductFilter


class CategoryListView(generics.ListAPIView):
    """Vue pour lister les catégories"""
    
    queryset = Category.objects.filter(is_active=True, parent__isnull=True)
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class CategoryDetailView(generics.RetrieveAPIView):
    """Vue pour les détails d'une catégorie"""
    
    queryset = Category.objects.filter(is_active=True)
    serializer_class = CategorySerializer
    lookup_field = 'slug'
    permission_classes = [IsAuthenticatedOrReadOnly]


class BrandListView(generics.ListAPIView):
    """Vue pour lister les marques"""
    
    queryset = Brand.objects.filter(is_active=True)
    serializer_class = BrandSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class BrandDetailView(generics.RetrieveAPIView):
    """Vue pour les détails d'une marque"""
    
    queryset = Brand.objects.filter(is_active=True)
    serializer_class = BrandSerializer
    lookup_field = 'slug'
    permission_classes = [IsAuthenticatedOrReadOnly]


class ProductListView(generics.ListAPIView):
    """Vue pour lister les produits"""
    
    queryset = Product.objects.filter(status='published').select_related('category', 'brand')
    serializer_class = ProductListSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ProductFilter
    search_fields = ['name', 'description', 'short_description', 'sku']
    ordering_fields = ['price', 'created_at', 'name']
    ordering = ['-created_at']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtrer par catégorie (incluant les sous-catégories)
        category_slug = self.request.query_params.get('category')
        if category_slug:
            try:
                category = Category.objects.get(slug=category_slug, is_active=True)
                # Inclure les produits de cette catégorie et de ses sous-catégories
                category_ids = [category.id]
                category_ids.extend(category.children.filter(is_active=True).values_list('id', flat=True))
                queryset = queryset.filter(category_id__in=category_ids)
            except Category.DoesNotExist:
                pass
        
        # Filtrer par marque
        brand_slug = self.request.query_params.get('brand')
        if brand_slug:
            queryset = queryset.filter(brand__slug=brand_slug, brand__is_active=True)
        
        # Filtrer par prix
        min_price = self.request.query_params.get('min_price')
        max_price = self.request.query_params.get('max_price')
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)
        
        # Filtrer par disponibilité
        in_stock = self.request.query_params.get('in_stock')
        if in_stock and in_stock.lower() == 'true':
            queryset = queryset.filter(
                Q(track_inventory=False) | Q(quantity__gt=0)
            )
        
        # Filtrer les produits en vedette
        featured = self.request.query_params.get('featured')
        if featured and featured.lower() == 'true':
            queryset = queryset.filter(is_featured=True)
        
        return queryset.prefetch_related('images')


class ProductDetailView(generics.RetrieveAPIView):
    """Vue pour les détails d'un produit"""
    
    queryset = Product.objects.filter(status='published')
    serializer_class = ProductDetailSerializer
    lookup_field = 'slug'
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        return super().get_queryset().select_related(
            'category', 'brand', 'vendor'
        ).prefetch_related(
            'images', 'attribute_values__attribute', 'reviews__user__profile'
        )


class ProductCreateView(generics.CreateAPIView):
    """Vue pour créer un produit (vendeurs uniquement)"""
    
    serializer_class = ProductCreateUpdateSerializer
    permission_classes = [IsAuthenticated]
    
    def perform_create(self, serializer):
        # Seuls les vendeurs peuvent créer des produits
        if not self.request.user.is_vendor:
            raise PermissionError(_("Seuls les vendeurs peuvent créer des produits."))
        serializer.save(vendor=self.request.user)


class ProductUpdateView(generics.UpdateAPIView):
    """Vue pour mettre à jour un produit"""
    
    serializer_class = ProductCreateUpdateSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # Les utilisateurs ne peuvent modifier que leurs propres produits
        if self.request.user.is_staff:
            return Product.objects.all()
        return Product.objects.filter(vendor=self.request.user)


class ProductDeleteView(generics.DestroyAPIView):
    """Vue pour supprimer un produit"""
    
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # Les utilisateurs ne peuvent supprimer que leurs propres produits
        if self.request.user.is_staff:
            return Product.objects.all()
        return Product.objects.filter(vendor=self.request.user)


class ProductReviewCreateView(generics.CreateAPIView):
    """Vue pour créer un avis sur un produit"""
    
    serializer_class = ProductReviewSerializer
    permission_classes = [IsAuthenticated]
    
    def perform_create(self, serializer):
        product_slug = self.kwargs.get('product_slug')
        try:
            product = Product.objects.get(slug=product_slug, status='published')
        except Product.DoesNotExist:
            raise ValueError(_("Produit non trouvé."))
        
        # Vérifier si l'utilisateur a déjà laissé un avis
        if ProductReview.objects.filter(product=product, user=self.request.user).exists():
            raise ValueError(_("Vous avez déjà laissé un avis pour ce produit."))
        
        serializer.save(product=product, user=self.request.user)


class ProductReviewListView(generics.ListAPIView):
    """Vue pour lister les avis d'un produit"""
    
    serializer_class = ProductReviewSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        product_slug = self.kwargs.get('product_slug')
        return ProductReview.objects.filter(
            product__slug=product_slug,
            product__status='published',
            is_approved=True
        ).select_related('user__profile').order_by('-created_at')


@api_view(['GET'])
@permission_classes([IsAuthenticatedOrReadOnly])
def product_search_view(request):
    """Vue pour la recherche avancée de produits"""
    
    query = request.GET.get('q', '')
    if not query:
        return Response({'products': [], 'message': _('Veuillez fournir un terme de recherche.')})
    
    # Recherche dans le nom, description et SKU
    products = Product.objects.filter(
        Q(name__icontains=query) |
        Q(description__icontains=query) |
        Q(short_description__icontains=query) |
        Q(sku__icontains=query),
        status='published'
    ).select_related('category', 'brand').prefetch_related('images')
    
    serializer = ProductListSerializer(products, many=True)
    
    return Response({
        'products': serializer.data,
        'count': products.count(),
        'query': query
    })


@api_view(['GET'])
@permission_classes([IsAuthenticatedOrReadOnly])
def featured_products_view(request):
    """Vue pour les produits en vedette"""
    
    products = Product.objects.filter(
        status='published',
        is_featured=True
    ).select_related('category', 'brand').prefetch_related('images')
    
    serializer = ProductListSerializer(products, many=True)
    
    return Response({
        'products': serializer.data,
        'count': products.count()
    })


@api_view(['GET'])
@permission_classes([IsAuthenticatedOrReadOnly])
def related_products_view(request, product_slug):
    """Vue pour les produits similaires"""
    
    try:
        product = Product.objects.get(slug=product_slug, status='published')
    except Product.DoesNotExist:
        return Response({'error': _('Produit non trouvé.')}, status=status.HTTP_404_NOT_FOUND)
    
    # Produits de la même catégorie, excluant le produit actuel
    related_products = Product.objects.filter(
        category=product.category,
        status='published'
    ).exclude(id=product.id).select_related('category', 'brand').prefetch_related('images')[:8]
    
    serializer = ProductListSerializer(related_products, many=True)
    
    return Response({
        'products': serializer.data,
        'count': related_products.count()
    })


@api_view(['GET'])
@permission_classes([IsAuthenticatedOrReadOnly])
def product_stats_view(request, product_slug):
    """Vue pour les statistiques d'un produit"""
    
    try:
        product = Product.objects.get(slug=product_slug, status='published')
    except Product.DoesNotExist:
        return Response({'error': _('Produit non trouvé.')}, status=status.HTTP_404_NOT_FOUND)
    
    reviews = product.reviews.filter(is_approved=True)
    
    stats = {
        'total_reviews': reviews.count(),
        'average_rating': reviews.aggregate(avg_rating=Avg('rating'))['avg_rating'] or 0,
        'rating_distribution': reviews.values('rating').annotate(count=Count('rating')).order_by('rating'),
        'total_sold': 0,  # À implémenter avec le modèle Order
        'in_stock': product.is_in_stock,
        'low_stock': product.is_low_stock,
    }
    
    return Response(stats)


# Vues de base pour les produits
class ProductListView(ListView):
    """Vue pour lister les produits"""
    model = Product
    template_name = 'products/product_list.html'
    context_object_name = 'products'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = Product.objects.filter(status='published').select_related('category', 'brand').prefetch_related('images')
        
        # Filtrage par catégorie
        category_slug = self.kwargs.get('category_slug')
        if category_slug:
            category = get_object_or_404(Category, slug=category_slug, is_active=True)
            queryset = queryset.filter(category=category)
        
        # Filtrage par marque
        brand_slug = self.kwargs.get('brand_slug')
        if brand_slug:
            brand = get_object_or_404(Brand, slug=brand_slug, is_active=True)
            queryset = queryset.filter(brand=brand)
        
        # Recherche
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(sku__icontains=search_query)
            )
        
        # Tri
        sort_by = self.request.GET.get('sort')
        if sort_by == 'price_asc':
            queryset = queryset.order_by('price')
        elif sort_by == 'price_desc':
            queryset = queryset.order_by('-price')
        elif sort_by == 'name':
            queryset = queryset.order_by('name')
        elif sort_by == 'newest':
            queryset = queryset.order_by('-created_at')
        else:
            queryset = queryset.order_by('-created_at')
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.filter(is_active=True, parent__isnull=True)
        context['brands'] = Brand.objects.filter(is_active=True)
        context['search_query'] = self.request.GET.get('search', '')
        context['sort_by'] = self.request.GET.get('sort', '')
        return context


class ProductDetailView(DetailView):
    """Vue pour afficher un produit"""
    model = Product
    template_name = 'products/product_detail.html'
    context_object_name = 'product'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    
    def get_queryset(self):
        return Product.objects.filter(status='published').select_related('category', 'brand').prefetch_related('images', 'reviews__user')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.get_object()
        
        # Produits similaires
        context['related_products'] = Product.objects.filter(
            category=product.category,
            status='published'
        ).exclude(id=product.id)[:4]
        
        # Avis du produit
        context['reviews'] = product.reviews.filter(is_approved=True).order_by('-created_at')[:10]
        
        # Statistiques des avis
        reviews = product.reviews.filter(is_approved=True)
        if reviews.exists():
            context['avg_rating'] = reviews.aggregate(avg=Avg('rating'))['avg']
            context['total_reviews'] = reviews.count()
        else:
            context['avg_rating'] = 0
            context['total_reviews'] = 0
        
        return context


class CategoryListView(ListView):
    """Vue pour lister les catégories"""
    model = Category
    template_name = 'products/category_list.html'
    context_object_name = 'categories'
    
    def get_queryset(self):
        return Category.objects.filter(is_active=True, parent__isnull=True).prefetch_related('children')


class CategoryDetailView(DetailView):
    """Vue pour afficher une catégorie"""
    model = Category
    template_name = 'products/category_detail.html'
    context_object_name = 'category'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    
    def get_queryset(self):
        return Category.objects.filter(is_active=True)


class BrandListView(ListView):
    """Vue pour lister les marques"""
    model = Brand
    template_name = 'products/brand_list.html'
    context_object_name = 'brands'
    
    def get_queryset(self):
        return Brand.objects.filter(is_active=True)


class BrandDetailView(DetailView):
    """Vue pour afficher une marque"""
    model = Brand
    template_name = 'products/brand_detail.html'
    context_object_name = 'brand'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    
    def get_queryset(self):
        return Brand.objects.filter(is_active=True)


def product_search_view(request):
    """Vue de recherche de produits"""
    query = request.GET.get('q', '')
    products = []
    
    if query:
        products = Product.objects.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(sku__icontains=query),
            status='published'
        ).select_related('category', 'brand').prefetch_related('images')[:20]
    
    context = {
        'query': query,
        'products': products,
        'results_count': len(products)
    }
    
    return render(request, 'products/search_results.html', context)
