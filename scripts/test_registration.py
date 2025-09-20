#!/usr/bin/env python
"""
Script pour tester l'inscription d'utilisateurs
"""

import os
import sys
import django

# Ajouter le répertoire du projet au path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'silence_dor.settings_simple')
django.setup()

from apps.accounts.models import User

def test_user_creation():
    """Tester la création d'un utilisateur"""
    print("🧪 Test de création d'utilisateur...")
    
    try:
        # Créer un utilisateur de test
        user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        
        print(f"✅ Utilisateur créé avec succès: {user.get_full_name()}")
        print(f"   - Email: {user.email}")
        print(f"   - Username: {user.username}")
        print(f"   - Date de création: {user.date_joined}")
        
        # Tester l'authentification
        from django.contrib.auth import authenticate
        auth_user = authenticate(username='test@example.com', password='testpass123')
        
        if auth_user:
            print("✅ Authentification réussie")
        else:
            print("❌ Échec de l'authentification")
        
        # Nettoyer
        user.delete()
        print("✅ Utilisateur de test supprimé")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == '__main__':
    test_user_creation()

