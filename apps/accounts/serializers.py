from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from .models import User, UserProfile, Address


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Sérialiseur pour l'inscription des utilisateurs"""
    
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = (
            'email', 'username', 'first_name', 'last_name', 
            'phone', 'password', 'password_confirm'
        )
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Les mots de passe ne correspondent pas.")
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        # Créer le profil utilisateur
        UserProfile.objects.create(user=user)
        return user


class UserLoginSerializer(serializers.Serializer):
    """Sérialiseur pour la connexion des utilisateurs"""
    
    email = serializers.EmailField()
    password = serializers.CharField()
    
    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        
        if email and password:
            user = authenticate(username=email, password=password)
            if not user:
                raise serializers.ValidationError('Identifiants invalides.')
            if not user.is_active:
                raise serializers.ValidationError('Ce compte est désactivé.')
            attrs['user'] = user
            return attrs
        else:
            raise serializers.ValidationError('Email et mot de passe requis.')


class UserProfileSerializer(serializers.ModelSerializer):
    """Sérialiseur pour le profil utilisateur"""
    
    class Meta:
        model = UserProfile
        fields = ('avatar', 'bio', 'email_notifications', 'sms_notifications')


class UserSerializer(serializers.ModelSerializer):
    """Sérialiseur pour les utilisateurs"""
    
    profile = UserProfileSerializer(read_only=True)
    full_name = serializers.ReadOnlyField()
    
    class Meta:
        model = User
        fields = (
            'id', 'email', 'username', 'first_name', 'last_name', 
            'full_name', 'phone', 'birth_date', 'address', 'city', 
            'postal_code', 'country', 'is_vendor', 'company_name', 
            'newsletter_subscription', 'language', 'date_joined', 'profile'
        )
        read_only_fields = ('id', 'date_joined', 'is_vendor')


class UserUpdateSerializer(serializers.ModelSerializer):
    """Sérialiseur pour la mise à jour des utilisateurs"""
    
    class Meta:
        model = User
        fields = (
            'first_name', 'last_name', 'phone', 'birth_date', 
            'address', 'city', 'postal_code', 'country', 
            'company_name', 'newsletter_subscription', 'language'
        )


class AddressSerializer(serializers.ModelSerializer):
    """Sérialiseur pour les adresses"""
    
    class Meta:
        model = Address
        fields = (
            'id', 'type', 'is_default', 'first_name', 'last_name', 
            'company', 'address_line_1', 'address_line_2', 'city', 
            'state', 'postal_code', 'country', 'phone', 'created_at'
        )
        read_only_fields = ('id', 'created_at')
    
    def validate(self, attrs):
        # Vérifier qu'il n'y a qu'une seule adresse par défaut par type
        if attrs.get('is_default', False):
            user = self.context['request'].user
            address_type = attrs.get('type')
            
            existing_default = Address.objects.filter(
                user=user, 
                type=address_type, 
                is_default=True
            ).exclude(pk=self.instance.pk if self.instance else None)
            
            if existing_default.exists():
                existing_default.update(is_default=False)
        
        return attrs


class ChangePasswordSerializer(serializers.Serializer):
    """Sérialiseur pour le changement de mot de passe"""
    
    old_password = serializers.CharField()
    new_password = serializers.CharField(validators=[validate_password])
    new_password_confirm = serializers.CharField()
    
    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('Ancien mot de passe incorrect.')
        return value
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError("Les nouveaux mots de passe ne correspondent pas.")
        return attrs

