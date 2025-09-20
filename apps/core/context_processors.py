from .models import SiteInformation

def site_info(request):
    """Context processor pour ajouter les informations du site à tous les templates"""
    try:
        site_info = SiteInformation.get_site_info()
        return {
            'site_info': site_info,
            'site_name': site_info.site_name,
            'site_tagline': site_info.site_tagline,
            'site_description': site_info.site_description,
            'hero_image': site_info.hero_image,
            'contact_email': site_info.contact_email,
            'contact_phone': site_info.contact_phone,
            'contact_address': site_info.contact_address,
            'company_name': site_info.company_name,
            'currency': site_info.currency,
            'currency_symbol': site_info.currency_symbol,
            'social_media': {
                'facebook': site_info.facebook_url,
                'instagram': site_info.instagram_url,
                'twitter': site_info.twitter_url,
                'linkedin': site_info.linkedin_url,
            },
            'seo': {
                'meta_keywords': site_info.meta_keywords,
                'google_analytics_id': site_info.google_analytics_id,
            }
        }
    except Exception:
        # Fallback en cas d'erreur
        return {
            'site_info': None,
            'site_name': 'Silence d\'Or',
            'site_tagline': 'Votre boutique de luxe en ligne',
            'site_description': 'Découvrez notre sélection exclusive de produits de qualité.',
            'hero_image': None,
            'contact_email': 'contact@silence-dor.com',
            'contact_phone': '+33 1 23 45 67 89',
            'contact_address': '123 Rue de la Paix, 75001 Paris, France',
            'company_name': 'Silence d\'Or SARL',
            'currency': 'EUR',
            'currency_symbol': '€',
            'social_media': {
                'facebook': '',
                'instagram': '',
                'twitter': '',
                'linkedin': '',
            },
            'seo': {
                'meta_keywords': '',
                'google_analytics_id': '',
            }
        }
