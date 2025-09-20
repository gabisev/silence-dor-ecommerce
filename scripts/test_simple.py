#!/usr/bin/env python
"""
Script de test simple pour vérifier la configuration de base
"""

import os
import sys
import django
from django.conf import settings

def test_basic_setup():
    """Test de configuration de base"""
    print("🔍 Test de configuration de base...")
    
    try:
        # Configuration Django simple
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'silence_dor.settings_simple')
        django.setup()
        
        print("✅ Django configuré correctement")
        
        # Test des imports de base
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
        
        print("\n🎉 Configuration de base fonctionnelle!")
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_requirements_basic():
    """Test des dépendances de base"""
    print("\n🔍 Test des dépendances de base...")
    
    required_packages = [
        'django',
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package} installé")
        except ImportError:
            print(f"❌ {package} manquant")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n❌ Packages manquants: {', '.join(missing_packages)}")
        print("Installez Django avec: pip install Django")
        return False
    
    print("✅ Django installé")
    return True

def main():
    """Fonction principale"""
    print("🚀 Test de configuration simple de Silence d'Or E-commerce\n")
    
    # Test des dépendances de base
    deps_ok = test_requirements_basic()
    
    if not deps_ok:
        print("\n❌ Veuillez installer Django avant de continuer")
        sys.exit(1)
    
    # Test de Django
    django_ok = test_basic_setup()
    
    if not django_ok:
        print("\n❌ Configuration Django incorrecte")
        sys.exit(1)
    
    print("\n🎉 Configuration de base complète et fonctionnelle!")
    print("\nProchaines étapes:")
    print("1. python manage.py makemigrations --settings=silence_dor.settings_simple")
    print("2. python manage.py migrate --settings=silence_dor.settings_simple")
    print("3. python manage.py createsuperuser --settings=silence_dor.settings_simple")
    print("4. python manage.py runserver --settings=silence_dor.settings_simple")

if __name__ == '__main__':
    main()

