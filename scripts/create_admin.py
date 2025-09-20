#!/usr/bin/env python
"""
Script pour créer ou réinitialiser le superutilisateur admin
"""
import os
import sys
import django

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'silence_dor.settings_simple')
django.setup()

from apps.accounts.models import User

def create_or_reset_admin():
    """Créer ou réinitialiser le superutilisateur admin"""
    print("🔐 Gestion du superutilisateur admin...")
    
    # Informations de connexion
    admin_email = "admin@silence-dor.com"
    admin_password = "admin123"
    
    try:
        # Vérifier si l'admin existe déjà
        admin_user = User.objects.filter(email=admin_email).first()
        
        if admin_user:
            print(f"✅ Utilisateur admin trouvé: {admin_user.email}")
            
            # Réinitialiser le mot de passe
            admin_user.set_password(admin_password)
            admin_user.is_staff = True
            admin_user.is_superuser = True
            admin_user.save()
            
            print(f"🔄 Mot de passe réinitialisé pour l'admin")
        else:
            # Créer un nouvel admin
            admin_user = User.objects.create_superuser(
                email=admin_email,
                username=admin_email,
                password=admin_password,
                first_name="Admin",
                last_name="Silence d'Or"
            )
            print(f"✅ Nouvel admin créé: {admin_user.email}")
        
        print("\n" + "="*50)
        print("🔑 INFORMATIONS DE CONNEXION ADMIN")
        print("="*50)
        print(f"📧 Email: {admin_email}")
        print(f"🔒 Mot de passe: {admin_password}")
        print(f"🌐 URL Admin: http://localhost:8000/admin/")
        print("="*50)
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la création de l'admin: {e}")
        return False

if __name__ == "__main__":
    success = create_or_reset_admin()
    if success:
        print("\n🎉 Superutilisateur admin prêt !")
        print("Vous pouvez maintenant vous connecter à l'interface d'administration.")
    else:
        print("\n❌ Échec de la création de l'admin.")
        sys.exit(1)

