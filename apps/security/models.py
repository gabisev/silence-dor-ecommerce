from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
import pyotp
import qrcode
from io import BytesIO
import base64

User = get_user_model()


class TwoFactorAuth(models.Model):
    """Authentification à deux facteurs"""
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='two_factor_auth')
    secret_key = models.CharField(_('clé secrète'), max_length=32, unique=True)
    is_enabled = models.BooleanField(_('activé'), default=False)
    backup_codes = models.JSONField(_('codes de sauvegarde'), default=list, blank=True)
    created_at = models.DateTimeField(_('créé le'), auto_now_add=True)
    last_used = models.DateTimeField(_('dernière utilisation'), null=True, blank=True)
    
    class Meta:
        verbose_name = _('Authentification à deux facteurs')
        verbose_name_plural = _('Authentifications à deux facteurs')
    
    def __str__(self):
        return f"2FA pour {self.user.email}"
    
    def generate_secret_key(self):
        """Génère une nouvelle clé secrète"""
        self.secret_key = pyotp.random_base32()
        self.save()
        return self.secret_key
    
    def generate_backup_codes(self, count=10):
        """Génère des codes de sauvegarde"""
        import secrets
        codes = [secrets.token_hex(4).upper() for _ in range(count)]
        self.backup_codes = codes
        self.save()
        return codes
    
    def verify_token(self, token):
        """Vérifie un token TOTP"""
        totp = pyotp.TOTP(self.secret_key)
        return totp.verify(token, valid_window=1)
    
    def verify_backup_code(self, code):
        """Vérifie un code de sauvegarde"""
        if code in self.backup_codes:
            self.backup_codes.remove(code)
            self.save()
            return True
        return False
    
    def get_qr_code_url(self):
        """Retourne l'URL du QR code pour l'application d'authentification"""
        totp = pyotp.TOTP(self.secret_key)
        provisioning_uri = totp.provisioning_uri(
            name=self.user.email,
            issuer_name="Silence d'Or"
        )
        return provisioning_uri


class SecurityEvent(models.Model):
    """Événements de sécurité"""
    
    EVENT_TYPES = [
        ('login', _('Connexion')),
        ('logout', _('Déconnexion')),
        ('login_failed', _('Échec de connexion')),
        ('password_change', _('Changement de mot de passe')),
        ('password_reset', _('Réinitialisation de mot de passe')),
        ('2fa_enabled', _('2FA activé')),
        ('2fa_disabled', _('2FA désactivé')),
        ('2fa_used', _('2FA utilisé')),
        ('suspicious_activity', _('Activité suspecte')),
        ('account_locked', _('Compte verrouillé')),
        ('account_unlocked', _('Compte déverrouillé')),
        ('permission_denied', _('Accès refusé')),
        ('data_export', _('Export de données')),
        ('data_import', _('Import de données')),
    ]
    
    SEVERITY_LEVELS = [
        ('low', _('Faible')),
        ('medium', _('Moyen')),
        ('high', _('Élevé')),
        ('critical', _('Critique')),
    ]
    
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='security_events')
    event_type = models.CharField(_('type d\'événement'), max_length=30, choices=EVENT_TYPES)
    severity = models.CharField(_('gravité'), max_length=10, choices=SEVERITY_LEVELS, default='medium')
    
    # Détails de l'événement
    description = models.TextField(_('description'))
    ip_address = models.GenericIPAddressField(_('adresse IP'), null=True, blank=True)
    user_agent = models.TextField(_('user agent'), blank=True)
    location = models.CharField(_('localisation'), max_length=200, blank=True)
    
    # Métadonnées
    metadata = models.JSONField(_('métadonnées'), default=dict, blank=True)
    is_resolved = models.BooleanField(_('résolu'), default=False)
    resolved_at = models.DateTimeField(_('résolu le'), null=True, blank=True)
    resolved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='resolved_events')
    
    timestamp = models.DateTimeField(_('horodatage'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('Événement de sécurité')
        verbose_name_plural = _('Événements de sécurité')
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', 'event_type']),
            models.Index(fields=['severity', 'timestamp']),
            models.Index(fields=['is_resolved', 'timestamp']),
        ]
    
    def __str__(self):
        return f"{self.get_event_type_display()} - {self.user.email if self.user else 'Système'}"


class AuditLog(models.Model):
    """Journal d'audit pour toutes les actions"""
    
    ACTION_TYPES = [
        ('create', _('Création')),
        ('read', _('Lecture')),
        ('update', _('Modification')),
        ('delete', _('Suppression')),
        ('login', _('Connexion')),
        ('logout', _('Déconnexion')),
        ('export', _('Export')),
        ('import', _('Import')),
        ('permission_change', _('Changement de permission')),
    ]
    
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='audit_logs')
    action_type = models.CharField(_('type d\'action'), max_length=20, choices=ACTION_TYPES)
    
    # Objet concerné
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    
    # Détails
    description = models.TextField(_('description'))
    old_values = models.JSONField(_('anciennes valeurs'), default=dict, blank=True)
    new_values = models.JSONField(_('nouvelles valeurs'), default=dict, blank=True)
    
    # Contexte
    ip_address = models.GenericIPAddressField(_('adresse IP'), null=True, blank=True)
    user_agent = models.TextField(_('user agent'), blank=True)
    session_key = models.CharField(_('clé de session'), max_length=40, blank=True)
    
    timestamp = models.DateTimeField(_('horodatage'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('Journal d\'audit')
        verbose_name_plural = _('Journaux d\'audit')
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', 'action_type']),
            models.Index(fields=['content_type', 'object_id']),
            models.Index(fields=['timestamp']),
        ]
    
    def __str__(self):
        return f"{self.get_action_type_display()} - {self.description}"


class SecuritySettings(models.Model):
    """Paramètres de sécurité globaux"""
    
    # Authentification
    password_min_length = models.PositiveIntegerField(_('longueur minimale du mot de passe'), default=8)
    password_require_uppercase = models.BooleanField(_('exiger majuscules'), default=True)
    password_require_lowercase = models.BooleanField(_('exiger minuscules'), default=True)
    password_require_numbers = models.BooleanField(_('exiger chiffres'), default=True)
    password_require_symbols = models.BooleanField(_('exiger symboles'), default=False)
    password_expiry_days = models.PositiveIntegerField(_('expiration du mot de passe (jours)'), null=True, blank=True)
    
    # Verrouillage de compte
    max_login_attempts = models.PositiveIntegerField(_('tentatives de connexion max'), default=5)
    lockout_duration_minutes = models.PositiveIntegerField(_('durée de verrouillage (minutes)'), default=30)
    
    # 2FA
    require_2fa_for_admins = models.BooleanField(_('exiger 2FA pour les admins'), default=True)
    require_2fa_for_staff = models.BooleanField(_('exiger 2FA pour le personnel'), default=False)
    
    # Sessions
    session_timeout_minutes = models.PositiveIntegerField(_('timeout de session (minutes)'), default=120)
    max_concurrent_sessions = models.PositiveIntegerField(_('sessions simultanées max'), default=3)
    
    # Audit
    audit_log_retention_days = models.PositiveIntegerField(_('rétention des logs d\'audit (jours)'), default=365)
    log_failed_attempts = models.BooleanField(_('logger les tentatives échouées'), default=True)
    
    # Notifications
    notify_on_suspicious_activity = models.BooleanField(_('notifier activité suspecte'), default=True)
    notify_on_admin_actions = models.BooleanField(_('notifier actions admin'), default=True)
    
    created_at = models.DateTimeField(_('créé le'), auto_now_add=True)
    updated_at = models.DateTimeField(_('modifié le'), auto_now=True)
    
    class Meta:
        verbose_name = _('Paramètres de sécurité')
        verbose_name_plural = _('Paramètres de sécurité')
    
    def __str__(self):
        return "Paramètres de sécurité"
    
    @classmethod
    def get_settings(cls):
        """Retourne les paramètres de sécurité (singleton)"""
        settings, created = cls.objects.get_or_create(pk=1)
        return settings


class FailedLoginAttempt(models.Model):
    """Tentatives de connexion échouées"""
    
    email = models.EmailField(_('email'))
    ip_address = models.GenericIPAddressField(_('adresse IP'))
    user_agent = models.TextField(_('user agent'), blank=True)
    timestamp = models.DateTimeField(_('horodatage'), auto_now_add=True)
    is_blocked = models.BooleanField(_('bloqué'), default=False)
    
    class Meta:
        verbose_name = _('Tentative de connexion échouée')
        verbose_name_plural = _('Tentatives de connexion échouées')
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['email', 'timestamp']),
            models.Index(fields=['ip_address', 'timestamp']),
        ]
    
    def __str__(self):
        return f"Échec de connexion - {self.email}"


class SecurityNotification(models.Model):
    """Notifications de sécurité"""
    
    NOTIFICATION_TYPES = [
        ('suspicious_login', _('Connexion suspecte')),
        ('new_device', _('Nouvel appareil')),
        ('password_changed', _('Mot de passe changé')),
        ('2fa_enabled', _('2FA activé')),
        ('account_locked', _('Compte verrouillé')),
        ('data_breach', _('Violation de données')),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='security_notifications')
    notification_type = models.CharField(_('type de notification'), max_length=30, choices=NOTIFICATION_TYPES)
    title = models.CharField(_('titre'), max_length=200)
    message = models.TextField(_('message'))
    
    # Métadonnées
    metadata = models.JSONField(_('métadonnées'), default=dict, blank=True)
    is_read = models.BooleanField(_('lu'), default=False)
    is_sent = models.BooleanField(_('envoyé'), default=False)
    
    created_at = models.DateTimeField(_('créé le'), auto_now_add=True)
    read_at = models.DateTimeField(_('lu le'), null=True, blank=True)
    
    class Meta:
        verbose_name = _('Notification de sécurité')
        verbose_name_plural = _('Notifications de sécurité')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.user.email}"

