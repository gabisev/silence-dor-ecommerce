#!/usr/bin/env python
"""
Script d'initialisation des fonctionnalités avancées
Initialise les données de base pour toutes les nouvelles apps
"""

import os
import sys
import django

# Ajouter le répertoire parent au path Python
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'silence_dor.settings_simple')
django.setup()

from django.contrib.auth import get_user_model
from apps.i18n.models import Language, Currency, Country, Region, ShippingZone, ShippingMethod
from apps.security.models import SecuritySettings
from apps.marketing.models import LoyaltyProgram, AffiliateProgram
from apps.inventory.models import Warehouse
from apps.notifications.models import EmailTemplate

User = get_user_model()


def init_languages():
    """Initialise les langues supportées"""
    print("🌍 Initialisation des langues...")
    
    languages = [
        {'code': 'fr', 'name': 'Français', 'native_name': 'Français', 'is_default': True, 'flag_emoji': '🇫🇷'},
        {'code': 'en', 'name': 'English', 'native_name': 'English', 'flag_emoji': '🇺🇸'},
        {'code': 'es', 'name': 'Español', 'native_name': 'Español', 'flag_emoji': '🇪🇸'},
        {'code': 'de', 'name': 'Deutsch', 'native_name': 'Deutsch', 'flag_emoji': '🇩🇪'},
    ]
    
    for lang_data in languages:
        language, created = Language.objects.get_or_create(
            code=lang_data['code'],
            defaults=lang_data
        )
        if created:
            print(f"  ✅ Langue créée: {language.name}")
        else:
            print(f"  ℹ️  Langue existante: {language.name}")


def init_currencies():
    """Initialise les devises supportées"""
    print("💰 Initialisation des devises...")
    
    currencies = [
        {'code': 'EUR', 'name': 'Euro', 'symbol': '€', 'is_default': True, 'symbol_position': 'after'},
        {'code': 'USD', 'name': 'US Dollar', 'symbol': '$', 'symbol_position': 'before'},
        {'code': 'GBP', 'name': 'British Pound', 'symbol': '£', 'symbol_position': 'before'},
        {'code': 'CAD', 'name': 'Canadian Dollar', 'symbol': 'C$', 'symbol_position': 'before'},
    ]
    
    for curr_data in currencies:
        currency, created = Currency.objects.get_or_create(
            code=curr_data['code'],
            defaults=curr_data
        )
        if created:
            print(f"  ✅ Devise créée: {currency.name}")
        else:
            print(f"  ℹ️  Devise existante: {currency.name}")


def init_countries():
    """Initialise les pays supportés"""
    print("🌍 Initialisation des pays...")
    
    countries = [
        {
            'code': 'FR', 'name': 'France', 'native_name': 'France', 
            'is_default': True, 'flag_emoji': '🇫🇷', 'phone_code': '+33',
            'continent': 'Europe', 'region': 'Western Europe'
        },
        {
            'code': 'US', 'name': 'United States', 'native_name': 'United States',
            'flag_emoji': '🇺🇸', 'phone_code': '+1',
            'continent': 'North America', 'region': 'North America'
        },
        {
            'code': 'CA', 'name': 'Canada', 'native_name': 'Canada',
            'flag_emoji': '🇨🇦', 'phone_code': '+1',
            'continent': 'North America', 'region': 'North America'
        },
        {
            'code': 'GB', 'name': 'United Kingdom', 'native_name': 'United Kingdom',
            'flag_emoji': '🇬🇧', 'phone_code': '+44',
            'continent': 'Europe', 'region': 'Western Europe'
        },
    ]
    
    for country_data in countries:
        country, created = Country.objects.get_or_create(
            code=country_data['code'],
            defaults=country_data
        )
        if created:
            print(f"  ✅ Pays créé: {country.name}")
        else:
            print(f"  ℹ️  Pays existant: {country.name}")


def init_shipping():
    """Initialise les zones et méthodes de livraison"""
    print("🚚 Initialisation des zones de livraison...")
    
    # Zone France
    france = Country.objects.get(code='FR')
    france_zone, created = ShippingZone.objects.get_or_create(
        name='France',
        defaults={'description': 'Livraison en France métropolitaine', 'is_default': True}
    )
    if created:
        france_zone.countries.add(france)
        print(f"  ✅ Zone créée: {france_zone.name}")
    
    # Zone Europe
    europe_zone, created = ShippingZone.objects.get_or_create(
        name='Europe',
        defaults={'description': 'Livraison en Europe'}
    )
    if created:
        europe_countries = Country.objects.filter(continent='Europe')
        europe_zone.countries.set(europe_countries)
        print(f"  ✅ Zone créée: {europe_zone.name}")
    
    # Zone International
    international_zone, created = ShippingZone.objects.get_or_create(
        name='International',
        defaults={'description': 'Livraison internationale'}
    )
    if created:
        all_countries = Country.objects.all()
        international_zone.countries.set(all_countries)
        print(f"  ✅ Zone créée: {international_zone.name}")
    
    # Méthodes de livraison
    shipping_methods = [
        {
            'name': 'Livraison Standard',
            'description': 'Livraison standard en 3-5 jours ouvrés',
            'method_type': 'standard',
            'base_cost': 5.99,
            'min_delivery_days': 3,
            'max_delivery_days': 5,
            'is_default': True
        },
        {
            'name': 'Livraison Express',
            'description': 'Livraison express en 1-2 jours ouvrés',
            'method_type': 'express',
            'base_cost': 12.99,
            'min_delivery_days': 1,
            'max_delivery_days': 2,
        },
        {
            'name': 'Livraison Gratuite',
            'description': 'Livraison gratuite pour commandes > 50€',
            'method_type': 'standard',
            'base_cost': 0,
            'free_shipping_threshold': 50,
            'min_delivery_days': 3,
            'max_delivery_days': 5,
        }
    ]
    
    for method_data in shipping_methods:
        method, created = ShippingMethod.objects.get_or_create(
            name=method_data['name'],
            shipping_zone=france_zone,
            defaults=method_data
        )
        if created:
            print(f"  ✅ Méthode créée: {method.name}")
        else:
            print(f"  ℹ️  Méthode existante: {method.name}")


def init_security():
    """Initialise les paramètres de sécurité"""
    print("🛡️ Initialisation des paramètres de sécurité...")
    
    settings, created = SecuritySettings.objects.get_or_create(
        pk=1,
        defaults={
            'password_min_length': 8,
            'password_require_uppercase': True,
            'password_require_lowercase': True,
            'password_require_numbers': True,
            'password_require_symbols': False,
            'max_login_attempts': 5,
            'lockout_duration_minutes': 30,
            'require_2fa_for_admins': True,
            'require_2fa_for_staff': False,
            'session_timeout_minutes': 120,
            'max_concurrent_sessions': 3,
            'audit_log_retention_days': 365,
            'log_failed_attempts': True,
            'notify_on_suspicious_activity': True,
            'notify_on_admin_actions': True,
        }
    )
    
    if created:
        print("  ✅ Paramètres de sécurité créés")
    else:
        print("  ℹ️  Paramètres de sécurité existants")


def init_marketing():
    """Initialise les programmes marketing"""
    print("📢 Initialisation des programmes marketing...")
    
    # Programme de fidélité
    loyalty_program, created = LoyaltyProgram.objects.get_or_create(
        name='Programme de Fidélité Silence d\'Or',
        defaults={
            'description': 'Gagnez des points à chaque achat et profitez d\'avantages exclusifs',
            'points_per_euro': 1.0,
            'points_per_signup': 100,
            'points_per_review': 50,
            'points_per_referral': 200,
            'bronze_threshold': 0,
            'silver_threshold': 1000,
            'gold_threshold': 5000,
            'platinum_threshold': 10000,
            'bronze_discount': 0,
            'silver_discount': 5,
            'gold_discount': 10,
            'platinum_discount': 15,
        }
    )
    
    if created:
        print("  ✅ Programme de fidélité créé")
    else:
        print("  ℹ️  Programme de fidélité existant")
    
    # Programme d'affiliation
    affiliate_program, created = AffiliateProgram.objects.get_or_create(
        name='Programme d\'Affiliation Silence d\'Or',
        defaults={
            'description': 'Gagnez des commissions en recommandant nos produits',
            'commission_type': 'percentage',
            'commission_value': 5.0,
            'minimum_payout': 50,
            'cookie_duration_days': 30,
        }
    )
    
    if created:
        print("  ✅ Programme d'affiliation créé")
    else:
        print("  ℹ️  Programme d'affiliation existant")


def init_inventory():
    """Initialise l'inventaire"""
    print("📦 Initialisation de l'inventaire...")
    
    # Entrepôt principal
    warehouse, created = Warehouse.objects.get_or_create(
        code='MAIN',
        defaults={
            'name': 'Entrepôt Principal',
            'address': '123 Rue de la Paix',
            'city': 'Paris',
            'postal_code': '75001',
            'country': 'France',
            'contact_person': 'Responsable Entrepôt',
            'phone': '+33 1 23 45 67 89',
            'email': 'warehouse@silence-dor.com',
            'is_default': True,
            'max_capacity': 10000,
        }
    )
    
    if created:
        print("  ✅ Entrepôt principal créé")
    else:
        print("  ℹ️  Entrepôt principal existant")


def init_email_templates():
    """Initialise les templates d'emails"""
    print("📧 Initialisation des templates d'emails...")
    
    templates = [
        {
            'name': 'Email de bienvenue',
            'template_type': 'welcome',
            'subject': 'Bienvenue chez {{ site_name }} !',
            'html_content': '''
            <h1>Bienvenue {{ user_name }} !</h1>
            <p>Merci de vous être inscrit sur {{ site_name }}.</p>
            <p>Vous pouvez maintenant profiter de tous nos services.</p>
            <a href="{{ login_url }}">Se connecter</a>
            ''',
            'text_content': 'Bienvenue {{ user_name }} ! Merci de vous être inscrit sur {{ site_name }}.'
        },
        {
            'name': 'Confirmation de commande',
            'template_type': 'order_confirmation',
            'subject': 'Confirmation de votre commande #{{ order_id }}',
            'html_content': '''
            <h1>Commande confirmée</h1>
            <p>Bonjour {{ user_name }},</p>
            <p>Votre commande #{{ order_id }} a été confirmée.</p>
            <p>Total: {{ order_total }}€</p>
            <a href="{{ order_url }}">Voir ma commande</a>
            ''',
            'text_content': 'Commande #{{ order_id }} confirmée. Total: {{ order_total }}€'
        },
        {
            'name': 'Commande expédiée',
            'template_type': 'order_shipped',
            'subject': 'Votre commande #{{ order_id }} a été expédiée',
            'html_content': '''
            <h1>Commande expédiée</h1>
            <p>Bonjour {{ user_name }},</p>
            <p>Votre commande #{{ order_id }} a été expédiée.</p>
            <p>Numéro de suivi: {{ tracking_number }}</p>
            ''',
            'text_content': 'Commande #{{ order_id }} expédiée. Suivi: {{ tracking_number }}'
        },
    ]
    
    for template_data in templates:
        template, created = EmailTemplate.objects.get_or_create(
            template_type=template_data['template_type'],
            defaults=template_data
        )
        if created:
            print(f"  ✅ Template créé: {template.name}")
        else:
            print(f"  ℹ️  Template existant: {template.name}")


def main():
    """Fonction principale"""
    print("🚀 Initialisation des fonctionnalités avancées de Silence d'Or")
    print("=" * 60)
    
    try:
        init_languages()
        init_currencies()
        init_countries()
        init_shipping()
        init_security()
        init_marketing()
        init_inventory()
        init_email_templates()
        
        print("\n" + "=" * 60)
        print("✅ Initialisation terminée avec succès !")
        print("\n📋 Résumé des fonctionnalités disponibles:")
        print("  🌍 Multi-langues et devises")
        print("  🛡️ Sécurité renforcée (2FA, audit trail)")
        print("  📊 Analytics et tableau de bord")
        print("  🔍 Recherche avancée")
        print("  🎯 Système de recommandations")
        print("  📦 Gestion d'inventaire avancée")
        print("  📢 Marketing et fidélité")
        print("  📱 PWA et notifications")
        print("  🤖 Automatisation avec Celery")
        print("  📧 Système d'emails complet")
        
    except Exception as e:
        print(f"\n❌ Erreur lors de l'initialisation: {e}")
        return False
    
    return True


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)

