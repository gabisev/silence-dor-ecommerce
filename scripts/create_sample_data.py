#!/usr/bin/env python
"""
Script pour créer des données de test pour Silence d'Or
"""

import os
import sys
import django

# Ajouter le répertoire du projet au path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'silence_dor.settings_simple')
django.setup()

from apps.products.models import Category, Brand, Product, ProductImage
from apps.accounts.models import User
from django.core.files.base import ContentFile
from PIL import Image
import io

def create_sample_data():
    """Créer des données de test"""
    print("🚀 Création des données de test pour Silence d'Or...")
    
    # Créer des catégories
    categories_data = [
        {'name': 'Électronique', 'description': 'Appareils électroniques et gadgets'},
        {'name': 'Mode', 'description': 'Vêtements et accessoires de mode'},
        {'name': 'Maison & Jardin', 'description': 'Articles pour la maison et le jardin'},
        {'name': 'Sport & Loisirs', 'description': 'Équipements sportifs et de loisirs'},
        {'name': 'Beauté & Santé', 'description': 'Produits de beauté et de santé'},
        {'name': 'Livres & Médias', 'description': 'Livres, films et musique'},
    ]
    
    categories = []
    for cat_data in categories_data:
        category, created = Category.objects.get_or_create(
            name=cat_data['name'],
            defaults={'description': cat_data['description'], 'is_active': True}
        )
        categories.append(category)
        if created:
            print(f"✅ Catégorie créée: {category.name}")
    
    # Créer des marques
    brands_data = [
        {'name': 'TechCorp', 'description': 'Innovation technologique'},
        {'name': 'StyleBrand', 'description': 'Mode et style'},
        {'name': 'HomeLife', 'description': 'Maison et décoration'},
        {'name': 'SportMax', 'description': 'Équipements sportifs'},
        {'name': 'BeautyPlus', 'description': 'Produits de beauté'},
        {'name': 'BookWorld', 'description': 'Livres et médias'},
    ]
    
    brands = []
    for brand_data in brands_data:
        brand, created = Brand.objects.get_or_create(
            name=brand_data['name'],
            defaults={'description': brand_data['description'], 'is_active': True}
        )
        brands.append(brand)
        if created:
            print(f"✅ Marque créée: {brand.name}")
    
    # Créer des produits
    products_data = [
        {
            'name': 'Smartphone Premium',
            'description': 'Smartphone haut de gamme avec caméra professionnelle',
            'price': 899.99,
            'category': categories[0],
            'brand': brands[0],
            'sku': 'TECH-SM001'
        },
        {
            'name': 'T-shirt Coton Bio',
            'description': 'T-shirt en coton biologique, confortable et durable',
            'price': 29.99,
            'category': categories[1],
            'brand': brands[1],
            'sku': 'MODE-TS001'
        },
        {
            'name': 'Lampadaire Design',
            'description': 'Lampadaire moderne pour salon et bureau',
            'price': 149.99,
            'category': categories[2],
            'brand': brands[2],
            'sku': 'HOME-LP001'
        },
        {
            'name': 'Raquette de Tennis',
            'description': 'Raquette de tennis professionnelle',
            'price': 199.99,
            'category': categories[3],
            'brand': brands[3],
            'sku': 'SPORT-RT001'
        },
        {
            'name': 'Crème Hydratante',
            'description': 'Crème hydratante pour tous types de peau',
            'price': 39.99,
            'category': categories[4],
            'brand': brands[4],
            'sku': 'BEAU-CH001'
        },
        {
            'name': 'Roman Bestseller',
            'description': 'Roman à succès de l\'année',
            'price': 19.99,
            'category': categories[5],
            'brand': brands[5],
            'sku': 'BOOK-RB001'
        },
        {
            'name': 'Casque Audio Sans Fil',
            'description': 'Casque audio sans fil avec réduction de bruit',
            'price': 299.99,
            'category': categories[0],
            'brand': brands[0],
            'sku': 'TECH-CA001'
        },
        {
            'name': 'Robe Élégante',
            'description': 'Robe élégante pour occasions spéciales',
            'price': 89.99,
            'category': categories[1],
            'brand': brands[1],
            'sku': 'MODE-RE001'
        },
        {
            'name': 'Coussin Décoratif',
            'description': 'Coussin décoratif pour salon',
            'price': 24.99,
            'category': categories[2],
            'brand': brands[2],
            'sku': 'HOME-CD001'
        },
        {
            'name': 'Ballon de Football',
            'description': 'Ballon de football officiel',
            'price': 49.99,
            'category': categories[3],
            'brand': brands[3],
            'sku': 'SPORT-BF001'
        },
        {
            'name': 'Sérum Anti-Âge',
            'description': 'Sérum anti-âge pour une peau plus jeune',
            'price': 79.99,
            'category': categories[4],
            'brand': brands[4],
            'sku': 'BEAU-SA001'
        },
        {
            'name': 'Guide de Cuisine',
            'description': 'Guide complet de cuisine française',
            'price': 34.99,
            'category': categories[5],
            'brand': brands[5],
            'sku': 'BOOK-GC001'
        }
    ]
    
    products = []
    for product_data in products_data:
        product, created = Product.objects.get_or_create(
            sku=product_data['sku'],
            defaults={
                'name': product_data['name'],
                'description': product_data['description'],
                'price': product_data['price'],
                'category': product_data['category'],
                'brand': product_data['brand'],
                'status': 'published',
                'is_featured': len(products) < 4,  # Les 4 premiers sont en vedette
                'quantity': 100,
                'weight': 500
            }
        )
        products.append(product)
        if created:
            print(f"✅ Produit créé: {product.name}")
    
    # Créer des utilisateurs de test
    test_users = [
        {
            'email': 'client1@test.com',
            'first_name': 'Marie',
            'last_name': 'Dupont',
            'password': 'testpass123'
        },
        {
            'email': 'client2@test.com',
            'first_name': 'Pierre',
            'last_name': 'Martin',
            'password': 'testpass123'
        }
    ]
    
    for user_data in test_users:
        try:
            user = User.objects.get(email=user_data['email'])
            print(f"ℹ️ Utilisateur existant: {user.get_full_name()}")
        except User.DoesNotExist:
            user = User.objects.create_user(
                email=user_data['email'],
                username=user_data['email'],  # Utiliser l'email comme username
                first_name=user_data['first_name'],
                last_name=user_data['last_name'],
                password=user_data['password']
            )
            print(f"✅ Utilisateur créé: {user.get_full_name()}")
    
    print("\n🎉 Données de test créées avec succès!")
    print("\n📋 Résumé:")
    print(f"   - {len(categories)} catégories")
    print(f"   - {len(brands)} marques")
    print(f"   - {len(products)} produits")
    print(f"   - {len(test_users)} utilisateurs de test")
    
    print("\n🔑 Comptes de test:")
    print("   - admin / (mot de passe à définir)")
    print("   - client1@test.com / testpass123")
    print("   - client2@test.com / testpass123")
    
    print("\n🌐 Accès au site:")
    print("   - Site web: http://localhost:8000")
    print("   - Admin: http://localhost:8000/admin")

if __name__ == '__main__':
    create_sample_data()
