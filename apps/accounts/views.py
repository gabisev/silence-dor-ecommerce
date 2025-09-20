from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import TemplateView, CreateView, UpdateView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import User, UserProfile, Address
from .serializers import UserSerializer, UserProfileSerializer, AddressSerializer


# Vues de base pour l'authentification
def login_view(request):
    """Vue de connexion"""
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, 'Connexion réussie !')
            next_url = request.GET.get('next', 'core:home')
            return redirect(next_url)
        else:
            messages.error(request, 'Email ou mot de passe incorrect.')
    
    return render(request, 'accounts/login.html')


def register_view(request):
    """Vue d'inscription"""
    if request.method == 'POST':
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        
        if password1 != password2:
            messages.error(request, 'Les mots de passe ne correspondent pas.')
            return render(request, 'accounts/register.html')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Un compte avec cet email existe déjà.')
            return render(request, 'accounts/register.html')
        
        user = User.objects.create_user(
            email=email,
            password=password1,
            first_name=first_name,
            last_name=last_name
        )
        
        login(request, user)
        messages.success(request, 'Compte créé avec succès !')
        return redirect('core:home')
    
    return render(request, 'accounts/register.html')


def logout_view(request):
    """Vue de déconnexion"""
    logout(request)
    messages.success(request, 'Vous avez été déconnecté.')
    return redirect('core:home')


# Vues de profil utilisateur
class ProfileView(LoginRequiredMixin, TemplateView):
    """Vue du profil utilisateur"""
    template_name = 'accounts/profile.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = getattr(self.request.user, 'profile', None)
        context['addresses'] = Address.objects.filter(user=self.request.user)
        return context


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    """Vue de mise à jour du profil"""
    model = UserProfile
    fields = ['phone', 'date_of_birth', 'bio', 'avatar']
    template_name = 'accounts/profile_update.html'
    success_url = reverse_lazy('accounts:profile')
    
    def get_object(self):
        profile, created = UserProfile.objects.get_or_create(user=self.request.user)
        return profile


class AddressCreateView(LoginRequiredMixin, CreateView):
    """Vue de création d'adresse"""
    model = Address
    fields = ['type', 'first_name', 'last_name', 'company', 'address_line_1', 
              'address_line_2', 'city', 'state', 'postal_code', 'country', 'phone']
    template_name = 'accounts/address_form.html'
    success_url = reverse_lazy('accounts:profile')
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class AddressUpdateView(LoginRequiredMixin, UpdateView):
    """Vue de mise à jour d'adresse"""
    model = Address
    fields = ['type', 'first_name', 'last_name', 'company', 'address_line_1', 
              'address_line_2', 'city', 'state', 'postal_code', 'country', 'phone']
    template_name = 'accounts/address_form.html'
    success_url = reverse_lazy('accounts:profile')
    
    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)


# Vues API
class UserProfileAPIView(generics.RetrieveUpdateAPIView):
    """API pour le profil utilisateur"""
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        profile, created = UserProfile.objects.get_or_create(user=self.request.user)
        return profile


class AddressListCreateAPIView(generics.ListCreateAPIView):
    """API pour les adresses"""
    serializer_class = AddressSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class AddressRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    """API pour une adresse spécifique"""
    serializer_class = AddressSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password_view(request):
    """API pour changer le mot de passe"""
    old_password = request.data.get('old_password')
    new_password = request.data.get('new_password')
    
    if not request.user.check_password(old_password):
        return Response({'error': 'Ancien mot de passe incorrect'}, 
                       status=status.HTTP_400_BAD_REQUEST)
    
    request.user.set_password(new_password)
    request.user.save()
    
    return Response({'message': 'Mot de passe modifié avec succès'})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_stats_view(request):
    """API pour les statistiques utilisateur"""
    from apps.orders.models import Order
    from apps.cart.models import Wishlist
    
    stats = {
        'total_orders': Order.objects.filter(user=request.user).count(),
        'pending_orders': Order.objects.filter(user=request.user, status='pending').count(),
        'wishlist_items': Wishlist.objects.filter(user=request.user).count(),
        'profile_completion': 0
    }
    
    # Calculer le pourcentage de completion du profil
    profile = getattr(request.user, 'profile', None)
    if profile:
        fields = ['phone', 'date_of_birth', 'bio']
        completed_fields = sum(1 for field in fields if getattr(profile, field, None))
        stats['profile_completion'] = int((completed_fields / len(fields)) * 100)
    
    return Response(stats)