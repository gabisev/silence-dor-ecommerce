from django.shortcuts import render
from django.views.generic import TemplateView
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

@method_decorator(login_required, name='dispatch')
class LanguageListView(TemplateView):
    """Vue de la liste des langues"""
    template_name = 'i18n/language_list.html'

@method_decorator(login_required, name='dispatch')
class CurrencyListView(TemplateView):
    """Vue de la liste des devises"""
    template_name = 'i18n/currency_list.html'

@method_decorator(login_required, name='dispatch')
class CountryListView(TemplateView):
    """Vue de la liste des pays"""
    template_name = 'i18n/country_list.html'

@method_decorator(login_required, name='dispatch')
class ShippingZoneListView(TemplateView):
    """Vue de la liste des zones de livraison"""
    template_name = 'i18n/shipping_zone_list.html'

@method_decorator(login_required, name='dispatch')
class ShippingMethodListView(TemplateView):
    """Vue de la liste des méthodes de livraison"""
    template_name = 'i18n/shipping_method_list.html'

@method_decorator(login_required, name='dispatch')
class TaxRuleListView(TemplateView):
    """Vue de la liste des règles de taxation"""
    template_name = 'i18n/tax_rule_list.html'

def api_change_language(request):
    """API pour changer de langue"""
    return JsonResponse({'status': 'success'})

def api_change_currency(request):
    """API pour changer de devise"""
    return JsonResponse({'status': 'success'})

def api_countries(request):
    """API pour les pays"""
    return JsonResponse({'countries': []})

