#!/usr/bin/env python
"""
Script pour initialiser les informations du site
"""
import os
import sys
import django

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'silence_dor.settings_simple')
django.setup()

from apps.core.models import SiteInformation

def init_site_information():
    """Initialise les informations du site avec des valeurs par défaut"""
    print("🏢 Initialisation des informations du site...")
    
    # Données par défaut
    default_data = {
        'site_name': 'Silence d\'Or',
        'site_tagline': 'Votre boutique de luxe en ligne',
        'site_description': 'Découvrez notre sélection exclusive de produits de qualité pour tous vos besoins. Chez Silence d\'Or, nous vous proposons une expérience shopping unique avec des articles soigneusement sélectionnés.',
        'contact_email': 'contact@silence-dor.com',
        'contact_phone': '+33 1 23 45 67 89',
        'contact_address': '123 Rue de la Paix\n75001 Paris, France',
        'company_name': 'Silence d\'Or SARL',
        'siret_number': '12345678901234',
        'vat_number': 'FR12345678901',
        'currency': 'EUR',
        'currency_symbol': '€',
        'facebook_url': 'https://facebook.com/silence-dor',
        'instagram_url': 'https://instagram.com/silence_dor',
        'twitter_url': 'https://twitter.com/silence_dor',
        'linkedin_url': 'https://linkedin.com/company/silence-dor',
        'meta_keywords': 'e-commerce, boutique en ligne, produits de qualité, shopping, luxe, Silence d\'Or',
        'google_analytics_id': 'GA-XXXXXXXXX',
        'hero_image': None  # L'utilisateur pourra ajouter son image via l'admin
    }
    
    try:
        # Vérifier si les informations existent déjà
        site_info = SiteInformation.objects.first()
        
        if site_info:
            print(f"✅ Informations du site trouvées: {site_info.site_name}")
            
            # Mettre à jour avec les nouvelles données
            for key, value in default_data.items():
                setattr(site_info, key, value)
            
            site_info.save()
            print("🔄 Informations du site mises à jour")
        else:
            # Créer de nouvelles informations
            site_info = SiteInformation.objects.create(**default_data)
            print(f"✅ Nouvelles informations du site créées: {site_info.site_name}")
        
        print("\n" + "="*60)
        print("🏢 INFORMATIONS DU SITE CONFIGURÉES")
        print("="*60)
        print(f"📝 Nom du site: {site_info.site_name}")
        print(f"💬 Slogan: {site_info.site_tagline}")
        print(f"📧 Email: {site_info.contact_email}")
        print(f"📞 Téléphone: {site_info.contact_phone}")
        print(f"🏛️ Entreprise: {site_info.company_name}")
        print(f"💰 Devise: {site_info.currency_symbol} ({site_info.currency})")
        print("="*60)
        
        print("\n🌐 Réseaux sociaux configurés:")
        if site_info.facebook_url:
            print(f"   📘 Facebook: {site_info.facebook_url}")
        if site_info.instagram_url:
            print(f"   📷 Instagram: {site_info.instagram_url}")
        if site_info.twitter_url:
            print(f"   🐦 Twitter: {site_info.twitter_url}")
        if site_info.linkedin_url:
            print(f"   💼 LinkedIn: {site_info.linkedin_url}")
        
        print(f"\n🔗 Accès à l'administration: http://localhost:8000/admin/core/siteinformation/")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de l'initialisation: {e}")
        return False

if __name__ == "__main__":
    success = init_site_information()
    if success:
        print("\n🎉 Initialisation des informations du site terminée !")
        print("Vous pouvez maintenant personnaliser ces informations via l'interface d'administration.")
    else:
        print("\n❌ Échec de l'initialisation.")
        sys.exit(1)
