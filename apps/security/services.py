import hashlib
import hmac
import time
from datetime import datetime, timedelta
from django.contrib.auth import get_user_model
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.db.models import Q, Count
from django.utils import timezone
from django.core.cache import cache
from django.conf import settings
from .models import (
    TwoFactorAuth, SecurityEvent, AuditLog, SecuritySettings, 
    FailedLoginAttempt, SecurityNotification
)
from apps.notifications.services import EmailService

User = get_user_model()


class SecurityService:
    """Service principal pour la sécurité"""
    
    @staticmethod
    def log_security_event(user, event_type, description, severity='medium', 
                          ip_address=None, user_agent=None, metadata=None):
        """Enregistre un événement de sécurité"""
        event = SecurityEvent.objects.create(
            user=user,
            event_type=event_type,
            severity=severity,
            description=description,
            ip_address=ip_address,
            user_agent=user_agent,
            metadata=metadata or {}
        )
        
        # Envoyer une notification si nécessaire
        if severity in ['high', 'critical']:
            SecurityService._send_security_alert(event)
        
        return event
    
    @staticmethod
    def log_audit_event(user, action_type, description, content_object=None, 
                       old_values=None, new_values=None, request=None):
        """Enregistre un événement d'audit"""
        audit_log = AuditLog.objects.create(
            user=user,
            action_type=action_type,
            description=description,
            content_object=content_object,
            old_values=old_values or {},
            new_values=new_values or {},
            ip_address=request.META.get('REMOTE_ADDR') if request else None,
            user_agent=request.META.get('HTTP_USER_AGENT', '') if request else '',
            session_key=request.session.session_key if request and hasattr(request, 'session') else ''
        )
        
        return audit_log
    
    @staticmethod
    def _send_security_alert(event):
        """Envoie une alerte de sécurité"""
        # Envoyer un email aux administrateurs
        admins = User.objects.filter(is_staff=True, is_active=True)
        
        for admin in admins:
            context = {
                'event_type': event.get_event_type_display(),
                'severity': event.get_severity_display(),
                'description': event.description,
                'user': event.user.email if event.user else 'Système',
                'timestamp': event.timestamp,
                'ip_address': event.ip_address,
            }
            
            EmailService.send_template_email(
                'security_alert',
                admin.email,
                context,
                admin
            )
    
    @staticmethod
    def check_failed_login_attempts(email, ip_address):
        """Vérifie les tentatives de connexion échouées"""
        security_settings = SecuritySettings.get_settings()
        
        # Compter les tentatives récentes
        recent_attempts = FailedLoginAttempt.objects.filter(
            Q(email=email) | Q(ip_address=ip_address),
            timestamp__gte=timezone.now() - timedelta(minutes=security_settings.lockout_duration_minutes)
        ).count()
        
        return recent_attempts >= security_settings.max_login_attempts
    
    @staticmethod
    def record_failed_login(email, ip_address, user_agent=None):
        """Enregistre une tentative de connexion échouée"""
        FailedLoginAttempt.objects.create(
            email=email,
            ip_address=ip_address,
            user_agent=user_agent or ''
        )
        
        # Vérifier si le compte doit être verrouillé
        if SecurityService.check_failed_login_attempts(email, ip_address):
            SecurityService._lock_account(email, ip_address)
    
    @staticmethod
    def _lock_account(email, ip_address):
        """Verrouille un compte après trop de tentatives échouées"""
        try:
            user = User.objects.get(email=email)
            user.is_active = False
            user.save()
            
            SecurityService.log_security_event(
                user=user,
                event_type='account_locked',
                description=f'Compte verrouillé après échecs de connexion depuis {ip_address}',
                severity='high',
                ip_address=ip_address
            )
            
            # Envoyer une notification
            SecurityNotification.objects.create(
                user=user,
                notification_type='account_locked',
                title='Compte verrouillé',
                message='Votre compte a été temporairement verrouillé pour des raisons de sécurité.'
            )
            
        except User.DoesNotExist:
            pass
    
    @staticmethod
    def unlock_account(user, unlocked_by=None):
        """Déverrouille un compte"""
        user.is_active = True
        user.save()
        
        # Supprimer les tentatives échouées
        FailedLoginAttempt.objects.filter(email=user.email).delete()
        
        SecurityService.log_security_event(
            user=user,
            event_type='account_unlocked',
            description=f'Compte déverrouillé par {unlocked_by.email if unlocked_by else "système"}',
            severity='medium'
        )
    
    @staticmethod
    def validate_password_strength(password):
        """Valide la force d'un mot de passe"""
        security_settings = SecuritySettings.get_settings()
        errors = []
        
        if len(password) < security_settings.password_min_length:
            errors.append(f'Le mot de passe doit contenir au moins {security_settings.password_min_length} caractères')
        
        if security_settings.password_require_uppercase and not any(c.isupper() for c in password):
            errors.append('Le mot de passe doit contenir au moins une majuscule')
        
        if security_settings.password_require_lowercase and not any(c.islower() for c in password):
            errors.append('Le mot de passe doit contenir au moins une minuscule')
        
        if security_settings.password_require_numbers and not any(c.isdigit() for c in password):
            errors.append('Le mot de passe doit contenir au moins un chiffre')
        
        if security_settings.password_require_symbols and not any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?' for c in password):
            errors.append('Le mot de passe doit contenir au moins un symbole')
        
        return errors
    
    @staticmethod
    def check_password_expiry(user):
        """Vérifie si le mot de passe a expiré"""
        security_settings = SecuritySettings.get_settings()
        
        if not security_settings.password_expiry_days:
            return False
        
        if hasattr(user, 'password_changed_at'):
            expiry_date = user.password_changed_at + timedelta(days=security_settings.password_expiry_days)
            return timezone.now() > expiry_date
        
        return False


class TwoFactorService:
    """Service pour l'authentification à deux facteurs"""
    
    @staticmethod
    def setup_2fa(user):
        """Configure la 2FA pour un utilisateur"""
        two_factor, created = TwoFactorAuth.objects.get_or_create(user=user)
        
        if created or not two_factor.secret_key:
            two_factor.generate_secret_key()
            two_factor.generate_backup_codes()
        
        return two_factor
    
    @staticmethod
    def enable_2fa(user, token):
        """Active la 2FA pour un utilisateur"""
        try:
            two_factor = TwoFactorAuth.objects.get(user=user)
            
            if two_factor.verify_token(token):
                two_factor.is_enabled = True
                two_factor.save()
                
                SecurityService.log_security_event(
                    user=user,
                    event_type='2fa_enabled',
                    description='Authentification à deux facteurs activée',
                    severity='medium'
                )
                
                return True, "2FA activé avec succès"
            else:
                return False, "Token invalide"
                
        except TwoFactorAuth.DoesNotExist:
            return False, "2FA non configuré"
    
    @staticmethod
    def disable_2fa(user, token_or_backup_code):
        """Désactive la 2FA pour un utilisateur"""
        try:
            two_factor = TwoFactorAuth.objects.get(user=user)
            
            # Vérifier le token ou le code de sauvegarde
            if two_factor.verify_token(token_or_backup_code) or two_factor.verify_backup_code(token_or_backup_code):
                two_factor.is_enabled = False
                two_factor.save()
                
                SecurityService.log_security_event(
                    user=user,
                    event_type='2fa_disabled',
                    description='Authentification à deux facteurs désactivée',
                    severity='medium'
                )
                
                return True, "2FA désactivé avec succès"
            else:
                return False, "Token ou code de sauvegarde invalide"
                
        except TwoFactorAuth.DoesNotExist:
            return False, "2FA non configuré"
    
    @staticmethod
    def verify_2fa(user, token):
        """Vérifie un token 2FA"""
        try:
            two_factor = TwoFactorAuth.objects.get(user=user, is_enabled=True)
            
            if two_factor.verify_token(token):
                two_factor.last_used = timezone.now()
                two_factor.save()
                
                SecurityService.log_security_event(
                    user=user,
                    event_type='2fa_used',
                    description='Token 2FA utilisé avec succès',
                    severity='low'
                )
                
                return True
            else:
                SecurityService.log_security_event(
                    user=user,
                    event_type='2fa_failed',
                    description='Échec de vérification 2FA',
                    severity='medium'
                )
                
                return False
                
        except TwoFactorAuth.DoesNotExist:
            return False
    
    @staticmethod
    def is_2fa_required(user):
        """Vérifie si la 2FA est requise pour un utilisateur"""
        security_settings = SecuritySettings.get_settings()
        
        if user.is_superuser and security_settings.require_2fa_for_admins:
            return True
        
        if user.is_staff and security_settings.require_2fa_for_staff:
            return True
        
        return False


class SessionSecurityService:
    """Service pour la sécurité des sessions"""
    
    @staticmethod
    def check_concurrent_sessions(user, session_key):
        """Vérifie les sessions simultanées"""
        security_settings = SecuritySettings.get_settings()
        
        # Compter les sessions actives
        active_sessions = cache.get(f'user_sessions_{user.id}', [])
        
        if len(active_sessions) >= security_settings.max_concurrent_sessions:
            # Supprimer la session la plus ancienne
            oldest_session = min(active_sessions, key=lambda x: x['timestamp'])
            cache.delete(f'session_{oldest_session["key"]}')
            active_sessions.remove(oldest_session)
        
        # Ajouter la nouvelle session
        active_sessions.append({
            'key': session_key,
            'timestamp': timezone.now().isoformat()
        })
        
        cache.set(f'user_sessions_{user.id}', active_sessions, timeout=security_settings.session_timeout_minutes * 60)
    
    @staticmethod
    def invalidate_user_sessions(user):
        """Invalide toutes les sessions d'un utilisateur"""
        active_sessions = cache.get(f'user_sessions_{user.id}', [])
        
        for session in active_sessions:
            cache.delete(f'session_{session["key"]}')
        
        cache.delete(f'user_sessions_{user.id}')
        
        SecurityService.log_security_event(
            user=user,
            event_type='sessions_invalidated',
            description='Toutes les sessions ont été invalidées',
            severity='medium'
        )


class DataProtectionService:
    """Service pour la protection des données"""
    
    @staticmethod
    def anonymize_user_data(user):
        """Anonymise les données d'un utilisateur"""
        # Anonymiser les données personnelles
        user.email = f"deleted_{user.id}@example.com"
        user.first_name = "Utilisateur"
        user.last_name = "Supprimé"
        user.save()
        
        # Anonymiser les logs d'audit
        AuditLog.objects.filter(user=user).update(
            description="Données anonymisées"
        )
        
        SecurityService.log_audit_event(
            user=None,
            action_type='update',
            description=f'Données utilisateur {user.id} anonymisées'
        )
    
    @staticmethod
    def export_user_data(user):
        """Exporte les données d'un utilisateur (RGPD)"""
        data = {
            'user_info': {
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'date_joined': user.date_joined.isoformat(),
                'last_login': user.last_login.isoformat() if user.last_login else None,
            },
            'orders': [],
            'audit_logs': [],
            'security_events': [],
        }
        
        # Ajouter les commandes
        from apps.orders.models import Order
        orders = Order.objects.filter(user=user)
        for order in orders:
            data['orders'].append({
                'id': order.id,
                'total_price': float(order.total_price),
                'status': order.status,
                'created_at': order.created_at.isoformat(),
            })
        
        # Ajouter les logs d'audit
        audit_logs = AuditLog.objects.filter(user=user)
        for log in audit_logs:
            data['audit_logs'].append({
                'action_type': log.action_type,
                'description': log.description,
                'timestamp': log.timestamp.isoformat(),
            })
        
        # Ajouter les événements de sécurité
        security_events = SecurityEvent.objects.filter(user=user)
        for event in security_events:
            data['security_events'].append({
                'event_type': event.event_type,
                'description': event.description,
                'severity': event.severity,
                'timestamp': event.timestamp.isoformat(),
            })
        
        SecurityService.log_audit_event(
            user=user,
            action_type='export',
            description='Export des données utilisateur (RGPD)'
        )
        
        return data

