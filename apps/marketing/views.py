from django.shortcuts import render
from django.views.generic import TemplateView
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

@method_decorator(login_required, name='dispatch')
class CampaignListView(TemplateView):
    """Vue de la liste des campagnes"""
    template_name = 'marketing/campaign_list.html'

@method_decorator(login_required, name='dispatch')
class CampaignDetailView(TemplateView):
    """Vue de détail d'une campagne"""
    template_name = 'marketing/campaign_detail.html'

@method_decorator(login_required, name='dispatch')
class CampaignCreateView(TemplateView):
    """Vue de création de campagne"""
    template_name = 'marketing/campaign_create.html'

@method_decorator(login_required, name='dispatch')
class CouponListView(TemplateView):
    """Vue de la liste des coupons"""
    template_name = 'marketing/coupon_list.html'

@method_decorator(login_required, name='dispatch')
class CouponDetailView(TemplateView):
    """Vue de détail d'un coupon"""
    template_name = 'marketing/coupon_detail.html'

@method_decorator(login_required, name='dispatch')
class CouponCreateView(TemplateView):
    """Vue de création de coupon"""
    template_name = 'marketing/coupon_create.html'

@method_decorator(login_required, name='dispatch')
class LoyaltyProgramView(TemplateView):
    """Vue du programme de fidélité"""
    template_name = 'marketing/loyalty_program.html'

@method_decorator(login_required, name='dispatch')
class LoyaltyAccountView(TemplateView):
    """Vue du compte de fidélité"""
    template_name = 'marketing/loyalty_account.html'

@method_decorator(login_required, name='dispatch')
class AffiliateProgramView(TemplateView):
    """Vue du programme d'affiliation"""
    template_name = 'marketing/affiliate_program.html'

@method_decorator(login_required, name='dispatch')
class AffiliateAccountView(TemplateView):
    """Vue du compte d'affiliation"""
    template_name = 'marketing/affiliate_account.html'

def api_validate_coupon(request):
    """API pour valider un coupon"""
    return JsonResponse({'valid': False})

def api_loyalty_points(request):
    """API pour les points de fidélité"""
    return JsonResponse({'points': 0})

