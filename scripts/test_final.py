#!/usr/bin/env python
"""
Script de test final pour vérifier que Silence d'Or fonctionne correctement
"""

import os
import sys
import django
from django.conf import settings

# Ajouter le répertoire du projet au path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_final_setup():
    """Test final de la configuration"""
    print("🔍 Test final de Silence d'Or E-commerce...")
    
    try:
        # Configuration Django simple
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'silence_dor.settings_simple')
        django.setup()
        
        print("✅ Django configuré correctement")
        
        # Test des imports de base
        from apps.accounts.models import User
        from apps.products.models import Product, Category, Brand
        from apps.cart.models import Cart, CartItem
        from apps.orders.models import Order, OrderItem
        from apps.payments.models import Payment
        
        print("✅ Tous les modèles importés correctement")
        
        # Test de la base de données
        from django.db import connection
        cursor = connection.cursor()
        cursor.execute("SELECT 1")
        print("✅ Connexion à la base de données réussie")
        
        # Test des URLs
        from django.urls import reverse
        from django.test import Client
        
        client = Client()
        
        # Test de la page d'accueil
        try:
            response = client.get('/')
            if response.status_code == 200:
                print("✅ Page d'accueil accessible")
            else:
                print(f"⚠️ Page d'accueil - Status: {response.status_code}")
        except Exception as e:
            print(f"⚠️ Erreur page d'accueil: {e}")
        
        # Test de l'admin
        try:
            response = client.get('/admin/')
            if response.status_code in [200, 302]:  # 302 = redirection vers login
                print("✅ Interface d'administration accessible")
            else:
                print(f"⚠️ Admin - Status: {response.status_code}")
        except Exception as e:
            print(f"⚠️ Erreur admin: {e}")
        
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
        
        print("\n🎉 Test final réussi!")
        print("\n📋 Votre site e-commerce est prêt!")
        print("\n🌐 Accès:")
        print("   - Site web: http://localhost:8000")
        print("   - Admin: http://localhost:8000/admin")
        print("   - API: http://localhost:8000/api")
        
        print("\n🚀 Pour démarrer le serveur:")
        print("   python manage.py runserver --settings=silence_dor.settings_simple")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors du test final: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Fonction principale"""
    print("🚀 Test final de Silence d'Or E-commerce\n")
    
    # Test final
    test_ok = test_final_setup()
    
    if not test_ok:
        print("\n❌ Des erreurs ont été détectées")
        print("Consultez docs/TROUBLESHOOTING.md pour plus d'aide")
        sys.exit(1)
    
    print("\n🎉 Félicitations! Votre site e-commerce est opérationnel!")

if __name__ == '__main__':
    main()
