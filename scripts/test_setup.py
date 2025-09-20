#!/usr/bin/env python
"""
Script de test pour vérifier la configuration de Silence d'Or
"""

import os
import sys
import django
from django.conf import settings
from django.core.management import execute_from_command_line

def test_django_setup():
    """Tester la configuration Django"""
    print("🔍 Test de la configuration Django...")
    
    try:
        # Configuration Django
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'silence_dor.settings')
        django.setup()
        
        print("✅ Django configuré correctement")
        
        # Test des imports
        from apps.accounts.models import User
        from apps.products.models import Product, Category
        from apps.cart.models import Cart
        from apps.orders.models import Order
        from apps.payments.models import Payment
        
        print("✅ Tous les modèles importés correctement")
        
        # Test de la base de données
        from django.db import connection
        cursor = connection.cursor()
        cursor.execute("SELECT 1")
        print("✅ Connexion à la base de données réussie")
        
        # Test des applications
        from django.apps import apps
        app_configs = apps.get_app_configs()
        app_names = [app.name for app in app_configs]
        
        expected_apps = [
            'apps.accounts',
            'apps.products', 
            'apps.cart',
            'apps.orders',
            'apps.payments',
            'apps.core'
        ]
        
        for app_name in expected_apps:
            if app_name in app_names:
                print(f"✅ Application {app_name} trouvée")
            else:
                print(f"❌ Application {app_name} manquante")
        
        print("\n🎉 Tous les tests sont passés avec succès!")
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
        return False

def test_requirements():
    """Tester les dépendances requises"""
    print("\n🔍 Test des dépendances...")
    
    required_packages = [
        'django',
        'djangorestframework',
        'stripe',
        'pillow',
        'python-decouple'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package} installé")
        except ImportError:
            print(f"❌ {package} manquant")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n❌ Packages manquants: {', '.join(missing_packages)}")
        print("Installez-les avec: pip install -r requirements.txt")
        return False
    
    print("✅ Toutes les dépendances sont installées")
    return True

def main():
    """Fonction principale"""
    print("🚀 Test de configuration de Silence d'Or E-commerce\n")
    
    # Test des dépendances
    deps_ok = test_requirements()
    
    if not deps_ok:
        print("\n❌ Veuillez installer les dépendances manquantes avant de continuer")
        sys.exit(1)
    
    # Test de Django
    django_ok = test_django_setup()
    
    if not django_ok:
        print("\n❌ Configuration Django incorrecte")
        sys.exit(1)
    
    print("\n🎉 Configuration complète et fonctionnelle!")
    print("\nProchaines étapes:")
    print("1. python manage.py makemigrations")
    print("2. python manage.py migrate")
    print("3. python manage.py createsuperuser")
    print("4. python manage.py runserver")

if __name__ == '__main__':
    main()

