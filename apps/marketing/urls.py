from django.urls import path
from . import views

app_name = 'marketing'

urlpatterns = [
    # Campagnes
    path('campaigns/', views.CampaignListView.as_view(), name='campaign-list'),
    path('campaigns/<int:pk>/', views.CampaignDetailView.as_view(), name='campaign-detail'),
    path('campaigns/create/', views.CampaignCreateView.as_view(), name='campaign-create'),
    
    # Coupons
    path('coupons/', views.CouponListView.as_view(), name='coupon-list'),
    path('coupons/<int:pk>/', views.CouponDetailView.as_view(), name='coupon-detail'),
    path('coupons/create/', views.CouponCreateView.as_view(), name='coupon-create'),
    
    # Programme de fidélité
    path('loyalty/', views.LoyaltyProgramView.as_view(), name='loyalty-program'),
    path('loyalty/my-account/', views.LoyaltyAccountView.as_view(), name='loyalty-account'),
    
    # Affiliation
    path('affiliate/', views.AffiliateProgramView.as_view(), name='affiliate-program'),
    path('affiliate/my-account/', views.AffiliateAccountView.as_view(), name='affiliate-account'),
    
    # API
    path('api/coupons/validate/', views.api_validate_coupon, name='api-validate-coupon'),
    path('api/loyalty/points/', views.api_loyalty_points, name='api-loyalty-points'),
]

