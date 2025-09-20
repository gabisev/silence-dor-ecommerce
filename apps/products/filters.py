import django_filters
from django.db.models import Q
from .models import Product, Category, Brand


class ProductFilter(django_filters.FilterSet):
    """Filtres pour les produits"""
    
    # Filtres de prix
    price_min = django_filters.NumberFilter(field_name='price', lookup_expr='gte')
    price_max = django_filters.NumberFilter(field_name='price', lookup_expr='lte')
    
    # Filtres de catégorie
    category = django_filters.ModelChoiceFilter(
        queryset=Category.objects.filter(is_active=True),
        field_name='category'
    )
    category_slug = django_filters.CharFilter(
        field_name='category__slug',
        lookup_expr='exact'
    )
    
    # Filtres de marque
    brand = django_filters.ModelChoiceFilter(
        queryset=Brand.objects.filter(is_active=True),
        field_name='brand'
    )
    brand_slug = django_filters.CharFilter(
        field_name='brand__slug',
        lookup_expr='exact'
    )
    
    # Filtres de disponibilité
    in_stock = django_filters.BooleanFilter(method='filter_in_stock')
    low_stock = django_filters.BooleanFilter(method='filter_low_stock')
    
    # Filtres de statut
    is_featured = django_filters.BooleanFilter(field_name='is_featured')
    is_digital = django_filters.BooleanFilter(field_name='is_digital')
    
    # Filtres de vendeur
    vendor = django_filters.NumberFilter(field_name='vendor')
    
    # Filtres de recherche
    search = django_filters.CharFilter(method='filter_search')
    
    class Meta:
        model = Product
        fields = {
            'price': ['gte', 'lte'],
            'quantity': ['gte', 'lte'],
            'created_at': ['gte', 'lte'],
            'updated_at': ['gte', 'lte'],
        }
    
    def filter_in_stock(self, queryset, name, value):
        """Filtrer les produits en stock"""
        if value:
            return queryset.filter(
                Q(track_inventory=False) | Q(quantity__gt=0)
            )
        else:
            return queryset.filter(
                track_inventory=True,
                quantity=0
            )
    
    def filter_low_stock(self, queryset, name, value):
        """Filtrer les produits en stock faible"""
        if value:
            from django.db import models
            return queryset.filter(
                track_inventory=True,
                quantity__lte=models.F('low_stock_threshold')
            )
        return queryset
    
    def filter_search(self, queryset, name, value):
        """Recherche dans les produits"""
        if value:
            return queryset.filter(
                Q(name__icontains=value) |
                Q(description__icontains=value) |
                Q(short_description__icontains=value) |
                Q(sku__icontains=value) |
                Q(category__name__icontains=value) |
                Q(brand__name__icontains=value)
            )
        return queryset


class CategoryFilter(django_filters.FilterSet):
    """Filtres pour les catégories"""
    
    parent = django_filters.ModelChoiceFilter(
        queryset=Category.objects.filter(is_active=True),
        field_name='parent'
    )
    has_products = django_filters.BooleanFilter(method='filter_has_products')
    
    class Meta:
        model = Category
        fields = ['is_active', 'parent']
    
    def filter_has_products(self, queryset, name, value):
        """Filtrer les catégories qui ont des produits"""
        if value:
            return queryset.filter(products__status='published').distinct()
        return queryset


class BrandFilter(django_filters.FilterSet):
    """Filtres pour les marques"""
    
    has_products = django_filters.BooleanFilter(method='filter_has_products')
    
    class Meta:
        model = Brand
        fields = ['is_active']
    
    def filter_has_products(self, queryset, name, value):
        """Filtrer les marques qui ont des produits"""
        if value:
            return queryset.filter(products__status='published').distinct()
        return queryset
