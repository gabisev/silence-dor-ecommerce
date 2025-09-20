from rest_framework import serializers
from django.db.models import Avg
from .models import (
    Category, Brand, Product, ProductImage, 
    ProductAttribute, ProductAttributeValue, ProductReview
)


class CategorySerializer(serializers.ModelSerializer):
    """Sérialiseur pour les catégories"""
    
    children = serializers.SerializerMethodField()
    product_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = (
            'id', 'name', 'slug', 'description', 'image', 
            'parent', 'is_active', 'sort_order', 'children', 'product_count'
        )
        read_only_fields = ('id', 'slug')
    
    def get_children(self, obj):
        if obj.children.exists():
            return CategorySerializer(obj.children.filter(is_active=True), many=True).data
        return []
    
    def get_product_count(self, obj):
        return obj.products.filter(status='published').count()


class BrandSerializer(serializers.ModelSerializer):
    """Sérialiseur pour les marques"""
    
    product_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Brand
        fields = (
            'id', 'name', 'slug', 'description', 'logo', 
            'website', 'is_active', 'product_count'
        )
        read_only_fields = ('id', 'slug')
    
    def get_product_count(self, obj):
        return obj.products.filter(status='published').count()


class ProductImageSerializer(serializers.ModelSerializer):
    """Sérialiseur pour les images de produits"""
    
    class Meta:
        model = ProductImage
        fields = ('id', 'image', 'alt_text', 'is_primary', 'sort_order')
        read_only_fields = ('id',)


class ProductAttributeValueSerializer(serializers.ModelSerializer):
    """Sérialiseur pour les valeurs d'attributs de produits"""
    
    attribute_name = serializers.CharField(source='attribute.name', read_only=True)
    attribute_type = serializers.CharField(source='attribute.type', read_only=True)
    
    class Meta:
        model = ProductAttributeValue
        fields = ('id', 'attribute', 'attribute_name', 'attribute_type', 'value')
        read_only_fields = ('id',)


class ProductReviewSerializer(serializers.ModelSerializer):
    """Sérialiseur pour les avis sur les produits"""
    
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    user_avatar = serializers.SerializerMethodField()
    
    class Meta:
        model = ProductReview
        fields = (
            'id', 'user', 'user_name', 'user_avatar', 'rating', 
            'title', 'comment', 'is_verified_purchase', 'is_approved', 'created_at'
        )
        read_only_fields = ('id', 'user', 'is_verified_purchase', 'is_approved', 'created_at')
    
    def get_user_avatar(self, obj):
        if hasattr(obj.user, 'profile') and obj.user.profile.avatar:
            return obj.user.profile.avatar.url
        return None


class ProductListSerializer(serializers.ModelSerializer):
    """Sérialiseur pour la liste des produits"""
    
    category_name = serializers.CharField(source='category.name', read_only=True)
    brand_name = serializers.CharField(source='brand.name', read_only=True)
    primary_image = serializers.SerializerMethodField()
    average_rating = serializers.SerializerMethodField()
    review_count = serializers.SerializerMethodField()
    discount_percentage = serializers.ReadOnlyField()
    
    class Meta:
        model = Product
        fields = (
            'id', 'name', 'slug', 'short_description', 'sku',
            'price', 'compare_price', 'discount_percentage',
            'category', 'category_name', 'brand', 'brand_name',
            'primary_image', 'is_featured', 'is_in_stock',
            'average_rating', 'review_count', 'created_at'
        )
        read_only_fields = ('id', 'slug')
    
    def get_primary_image(self, obj):
        primary_image = obj.images.filter(is_primary=True).first()
        if primary_image:
            return ProductImageSerializer(primary_image).data
        # Retourner la première image si aucune image primaire
        first_image = obj.images.first()
        if first_image:
            return ProductImageSerializer(first_image).data
        return None
    
    def get_average_rating(self, obj):
        avg_rating = obj.reviews.filter(is_approved=True).aggregate(
            avg_rating=Avg('rating')
        )['avg_rating']
        return round(avg_rating, 1) if avg_rating else 0
    
    def get_review_count(self, obj):
        return obj.reviews.filter(is_approved=True).count()


class ProductDetailSerializer(serializers.ModelSerializer):
    """Sérialiseur pour les détails d'un produit"""
    
    category = CategorySerializer(read_only=True)
    brand = BrandSerializer(read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    attribute_values = ProductAttributeValueSerializer(many=True, read_only=True)
    reviews = ProductReviewSerializer(many=True, read_only=True)
    average_rating = serializers.SerializerMethodField()
    review_count = serializers.SerializerMethodField()
    discount_percentage = serializers.ReadOnlyField()
    
    class Meta:
        model = Product
        fields = (
            'id', 'name', 'slug', 'description', 'short_description', 'sku',
            'price', 'compare_price', 'cost_price', 'discount_percentage',
            'category', 'brand', 'vendor', 'track_inventory', 'quantity',
            'low_stock_threshold', 'status', 'is_featured', 'is_digital',
            'weight', 'length', 'width', 'height', 'meta_title', 'meta_description',
            'images', 'attribute_values', 'reviews', 'average_rating', 'review_count',
            'is_in_stock', 'is_low_stock', 'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'slug', 'created_at', 'updated_at')
    
    def get_average_rating(self, obj):
        avg_rating = obj.reviews.filter(is_approved=True).aggregate(
            avg_rating=Avg('rating')
        )['avg_rating']
        return round(avg_rating, 1) if avg_rating else 0
    
    def get_review_count(self, obj):
        return obj.reviews.filter(is_approved=True).count()


class ProductCreateUpdateSerializer(serializers.ModelSerializer):
    """Sérialiseur pour la création et mise à jour des produits"""
    
    images = ProductImageSerializer(many=True, required=False)
    attribute_values = ProductAttributeValueSerializer(many=True, required=False)
    
    class Meta:
        model = Product
        fields = (
            'name', 'description', 'short_description', 'sku',
            'price', 'compare_price', 'cost_price', 'category', 'brand',
            'track_inventory', 'quantity', 'low_stock_threshold',
            'status', 'is_featured', 'is_digital', 'weight', 'length',
            'width', 'height', 'meta_title', 'meta_description',
            'images', 'attribute_values'
        )
    
    def create(self, validated_data):
        images_data = validated_data.pop('images', [])
        attribute_values_data = validated_data.pop('attribute_values', [])
        
        product = Product.objects.create(**validated_data)
        
        # Créer les images
        for image_data in images_data:
            ProductImage.objects.create(product=product, **image_data)
        
        # Créer les valeurs d'attributs
        for attr_value_data in attribute_values_data:
            ProductAttributeValue.objects.create(product=product, **attr_value_data)
        
        return product
    
    def update(self, instance, validated_data):
        images_data = validated_data.pop('images', [])
        attribute_values_data = validated_data.pop('attribute_values', [])
        
        # Mettre à jour le produit
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Mettre à jour les images si fournies
        if images_data:
            instance.images.all().delete()
            for image_data in images_data:
                ProductImage.objects.create(product=instance, **image_data)
        
        # Mettre à jour les valeurs d'attributs si fournies
        if attribute_values_data:
            instance.attribute_values.all().delete()
            for attr_value_data in attribute_values_data:
                ProductAttributeValue.objects.create(product=instance, **attr_value_data)
        
        return instance


class ProductAttributeSerializer(serializers.ModelSerializer):
    """Sérialiseur pour les attributs de produits"""
    
    class Meta:
        model = ProductAttribute
        fields = ('id', 'name', 'slug', 'type', 'is_required', 'is_filterable')
        read_only_fields = ('id', 'slug')

