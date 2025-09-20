from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    # Vues de base
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    
    # Profil utilisateur
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('profile/update/', views.ProfileUpdateView.as_view(), name='profile-update'),
    
    # Adresses
    path('addresses/create/', views.AddressCreateView.as_view(), name='address-create'),
    path('addresses/<int:pk>/update/', views.AddressUpdateView.as_view(), name='address-update'),
    
    # API URLs
    path('api/profile/', views.UserProfileAPIView.as_view(), name='user-profile-api'),
    path('api/addresses/', views.AddressListCreateAPIView.as_view(), name='address-list-create-api'),
    path('api/addresses/<int:pk>/', views.AddressRetrieveUpdateDestroyAPIView.as_view(), name='address-detail-api'),
    path('api/change-password/', views.change_password_view, name='change-password-api'),
    path('api/stats/', views.user_stats_view, name='user-stats-api'),
]
