from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal

User = get_user_model()


class Campaign(models.Model):
    """Campagnes marketing"""
    
    CAMPAIGN_TYPES = [
        ('email', _('Email')),
        ('sms', _('SMS')),
        ('push', _('Notification push')),
        ('banner', _('Bannière')),
        ('popup', _('Popup')),
        ('social', _('Réseaux sociaux')),
        ('affiliate', _('Affiliation')),
    ]
    
    STATUS_CHOICES = [
        ('draft', _('Brouillon')),
        ('scheduled', _('Programmée')),
        ('active', _('Active')),
        ('paused', _('En pause')),
        ('completed', _('Terminée')),
        ('cancelled', _('Annulée')),
    ]
    
    name = models.CharField(_('nom'), max_length=200)
    description = models.TextField(_('description'), blank=True)
    campaign_type = models.CharField(_('type de campagne'), max_length=20, choices=CAMPAIGN_TYPES)
    status = models.CharField(_('statut'), max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # Dates
    start_date = models.DateTimeField(_('date de début'))
    end_date = models.DateTimeField(_('date de fin'), null=True, blank=True)
    
    # Budget
    budget = models.DecimalField(_('budget'), max_digits=12, decimal_places=2, null=True, blank=True)
    spent_amount = models.DecimalField(_('montant dépensé'), max_digits=12, decimal_places=2, default=0)
    
    # Ciblage
    target_audience = models.JSONField(_('audience cible'), default=dict, blank=True)
    
    # Métriques
    impressions = models.PositiveIntegerField(_('impressions'), default=0)
    clicks = models.PositiveIntegerField(_('clics'), default=0)
    conversions = models.PositiveIntegerField(_('conversions'), default=0)
    revenue = models.DecimalField(_('revenus générés'), max_digits=12, decimal_places=2, default=0)
    
    # Configuration
    is_active = models.BooleanField(_('actif'), default=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_campaigns')
    
    created_at = models.DateTimeField(_('créé le'), auto_now_add=True)
    updated_at = models.DateTimeField(_('modifié le'), auto_now=True)
    
    class Meta:
        verbose_name = _('Campagne')
        verbose_name_plural = _('Campagnes')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} ({self.get_campaign_type_display()})"
    
    @property
    def click_through_rate(self):
        """Taux de clic"""
        if self.impressions > 0:
            return (self.clicks / self.impressions) * 100
        return 0
    
    @property
    def conversion_rate(self):
        """Taux de conversion"""
        if self.clicks > 0:
            return (self.conversions / self.clicks) * 100
        return 0
    
    @property
    def roi(self):
        """Retour sur investissement"""
        if self.spent_amount > 0:
            return ((self.revenue - self.spent_amount) / self.spent_amount) * 100
        return 0


class Coupon(models.Model):
    """Codes de réduction"""
    
    COUPON_TYPES = [
        ('percentage', _('Pourcentage')),
        ('fixed_amount', _('Montant fixe')),
        ('free_shipping', _('Livraison gratuite')),
        ('buy_x_get_y', _('Achetez X obtenez Y')),
    ]
    
    STATUS_CHOICES = [
        ('active', _('Actif')),
        ('inactive', _('Inactif')),
        ('expired', _('Expiré')),
        ('exhausted', _('Épuisé')),
    ]
    
    code = models.CharField(_('code'), max_length=50, unique=True)
    name = models.CharField(_('nom'), max_length=200)
    description = models.TextField(_('description'), blank=True)
    
    coupon_type = models.CharField(_('type de coupon'), max_length=20, choices=COUPON_TYPES)
    value = models.DecimalField(_('valeur'), max_digits=10, decimal_places=2)
    
    # Conditions
    minimum_order_amount = models.DecimalField(_('montant minimum de commande'), max_digits=10, decimal_places=2, null=True, blank=True)
    maximum_discount_amount = models.DecimalField(_('montant maximum de réduction'), max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Limites
    usage_limit = models.PositiveIntegerField(_('limite d\'utilisation'), null=True, blank=True)
    usage_limit_per_user = models.PositiveIntegerField(_('limite d\'utilisation par utilisateur'), default=1)
    used_count = models.PositiveIntegerField(_('nombre d\'utilisations'), default=0)
    
    # Dates
    valid_from = models.DateTimeField(_('valide à partir du'))
    valid_until = models.DateTimeField(_('valide jusqu\'au'), null=True, blank=True)
    
    # Ciblage
    applicable_products = models.ManyToManyField('products.Product', blank=True, related_name='applicable_coupons', verbose_name=_('produits applicables'))
    applicable_categories = models.ManyToManyField('products.Category', blank=True, related_name='applicable_coupons', verbose_name=_('catégories applicables'))
    applicable_users = models.ManyToManyField(User, blank=True, related_name='applicable_coupons', verbose_name=_('utilisateurs applicables'))
    
    # Statut
    status = models.CharField(_('statut'), max_length=20, choices=STATUS_CHOICES, default='active')
    is_active = models.BooleanField(_('actif'), default=True)
    
    created_at = models.DateTimeField(_('créé le'), auto_now_add=True)
    updated_at = models.DateTimeField(_('modifié le'), auto_now=True)
    
    class Meta:
        verbose_name = _('Coupon')
        verbose_name_plural = _('Coupons')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.code} - {self.name}"
    
    def is_valid(self, user=None, order_amount=None):
        """Vérifie si le coupon est valide"""
        from django.utils import timezone
        
        # Vérifier le statut
        if not self.is_active or self.status != 'active':
            return False, "Coupon inactif"
        
        # Vérifier les dates
        now = timezone.now()
        if now < self.valid_from:
            return False, "Coupon pas encore valide"
        
        if self.valid_until and now > self.valid_until:
            return False, "Coupon expiré"
        
        # Vérifier la limite d'utilisation
        if self.usage_limit and self.used_count >= self.usage_limit:
            return False, "Coupon épuisé"
        
        # Vérifier l'utilisateur
        if user and self.applicable_users.exists() and user not in self.applicable_users.all():
            return False, "Coupon non applicable à cet utilisateur"
        
        # Vérifier le montant minimum
        if order_amount and self.minimum_order_amount and order_amount < self.minimum_order_amount:
            return False, f"Montant minimum de commande requis: {self.minimum_order_amount}€"
        
        return True, "Coupon valide"
    
    def calculate_discount(self, order_amount):
        """Calcule le montant de la réduction"""
        if self.coupon_type == 'percentage':
            discount = (order_amount * self.value) / 100
        elif self.coupon_type == 'fixed_amount':
            discount = min(self.value, order_amount)
        elif self.coupon_type == 'free_shipping':
            discount = 0  # Géré séparément
        else:
            discount = 0
        
        # Appliquer le montant maximum de réduction
        if self.maximum_discount_amount:
            discount = min(discount, self.maximum_discount_amount)
        
        return discount


class LoyaltyProgram(models.Model):
    """Programme de fidélité"""
    
    name = models.CharField(_('nom'), max_length=200)
    description = models.TextField(_('description'), blank=True)
    
    # Configuration des points
    points_per_euro = models.DecimalField(_('points par euro'), max_digits=5, decimal_places=2, default=1.0)
    points_per_signup = models.PositiveIntegerField(_('points pour inscription'), default=100)
    points_per_review = models.PositiveIntegerField(_('points pour avis'), default=50)
    points_per_referral = models.PositiveIntegerField(_('points pour parrainage'), default=200)
    
    # Niveaux
    bronze_threshold = models.PositiveIntegerField(_('seuil bronze'), default=0)
    silver_threshold = models.PositiveIntegerField(_('seuil argent'), default=1000)
    gold_threshold = models.PositiveIntegerField(_('seuil or'), default=5000)
    platinum_threshold = models.PositiveIntegerField(_('seuil platine'), default=10000)
    
    # Avantages par niveau
    bronze_discount = models.DecimalField(_('réduction bronze (%)'), max_digits=5, decimal_places=2, default=0)
    silver_discount = models.DecimalField(_('réduction argent (%)'), max_digits=5, decimal_places=2, default=5)
    gold_discount = models.DecimalField(_('réduction or (%)'), max_digits=5, decimal_places=2, default=10)
    platinum_discount = models.DecimalField(_('réduction platine (%)'), max_digits=5, decimal_places=2, default=15)
    
    # Statut
    is_active = models.BooleanField(_('actif'), default=True)
    
    created_at = models.DateTimeField(_('créé le'), auto_now_add=True)
    updated_at = models.DateTimeField(_('modifié le'), auto_now=True)
    
    class Meta:
        verbose_name = _('Programme de fidélité')
        verbose_name_plural = _('Programmes de fidélité')
    
    def __str__(self):
        return self.name


class LoyaltyAccount(models.Model):
    """Compte de fidélité utilisateur"""
    
    MEMBERSHIP_LEVELS = [
        ('bronze', _('Bronze')),
        ('silver', _('Argent')),
        ('gold', _('Or')),
        ('platinum', _('Platine')),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='loyalty_account')
    program = models.ForeignKey(LoyaltyProgram, on_delete=models.CASCADE, related_name='accounts')
    
    # Points
    total_points = models.PositiveIntegerField(_('points totaux'), default=0)
    available_points = models.PositiveIntegerField(_('points disponibles'), default=0)
    used_points = models.PositiveIntegerField(_('points utilisés'), default=0)
    
    # Niveau
    membership_level = models.CharField(_('niveau d\'adhésion'), max_length=20, choices=MEMBERSHIP_LEVELS, default='bronze')
    
    # Statistiques
    total_spent = models.DecimalField(_('total dépensé'), max_digits=12, decimal_places=2, default=0)
    total_orders = models.PositiveIntegerField(_('total commandes'), default=0)
    referrals_count = models.PositiveIntegerField(_('nombre de parrainages'), default=0)
    
    # Dates
    joined_at = models.DateTimeField(_('rejoint le'), auto_now_add=True)
    last_activity = models.DateTimeField(_('dernière activité'), auto_now=True)
    
    class Meta:
        verbose_name = _('Compte de fidélité')
        verbose_name_plural = _('Comptes de fidélité')
    
    def __str__(self):
        return f"{self.user.email} - {self.get_membership_level_display()}"
    
    def add_points(self, points, reason=None):
        """Ajoute des points au compte"""
        self.total_points += points
        self.available_points += points
        self.save()
        
        # Enregistrer l'historique
        LoyaltyTransaction.objects.create(
            account=self,
            transaction_type='earned',
            points=points,
            reason=reason or 'Points ajoutés'
        )
        
        # Vérifier le niveau
        self.update_membership_level()
    
    def use_points(self, points, reason=None):
        """Utilise des points du compte"""
        if self.available_points >= points:
            self.available_points -= points
            self.used_points += points
            self.save()
            
            # Enregistrer l'historique
            LoyaltyTransaction.objects.create(
                account=self,
                transaction_type='used',
                points=points,
                reason=reason or 'Points utilisés'
            )
            
            return True
        return False
    
    def update_membership_level(self):
        """Met à jour le niveau d'adhésion"""
        if self.total_points >= self.program.platinum_threshold:
            new_level = 'platinum'
        elif self.total_points >= self.program.gold_threshold:
            new_level = 'gold'
        elif self.total_points >= self.program.silver_threshold:
            new_level = 'silver'
        else:
            new_level = 'bronze'
        
        if new_level != self.membership_level:
            self.membership_level = new_level
            self.save()
    
    def get_discount_percentage(self):
        """Retourne le pourcentage de réduction selon le niveau"""
        discounts = {
            'bronze': self.program.bronze_discount,
            'silver': self.program.silver_discount,
            'gold': self.program.gold_discount,
            'platinum': self.program.platinum_discount,
        }
        return discounts.get(self.membership_level, 0)


class LoyaltyTransaction(models.Model):
    """Transactions de points de fidélité"""
    
    TRANSACTION_TYPES = [
        ('earned', _('Gagné')),
        ('used', _('Utilisé')),
        ('expired', _('Expiré')),
        ('refunded', _('Remboursé')),
    ]
    
    account = models.ForeignKey(LoyaltyAccount, on_delete=models.CASCADE, related_name='transactions')
    transaction_type = models.CharField(_('type de transaction'), max_length=20, choices=TRANSACTION_TYPES)
    points = models.IntegerField(_('points'))
    reason = models.CharField(_('raison'), max_length=200)
    
    # Références
    order = models.ForeignKey('orders.Order', on_delete=models.SET_NULL, null=True, blank=True, related_name='loyalty_transactions')
    
    timestamp = models.DateTimeField(_('horodatage'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('Transaction de fidélité')
        verbose_name_plural = _('Transactions de fidélité')
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.account.user.email} - {self.get_transaction_type_display()} ({self.points} points)"


class AffiliateProgram(models.Model):
    """Programme d'affiliation"""
    
    name = models.CharField(_('nom'), max_length=200)
    description = models.TextField(_('description'), blank=True)
    
    # Commission
    commission_type = models.CharField(_('type de commission'), max_length=20, choices=[
        ('percentage', _('Pourcentage')),
        ('fixed', _('Montant fixe')),
    ], default='percentage')
    commission_value = models.DecimalField(_('valeur de commission'), max_digits=10, decimal_places=2)
    
    # Conditions
    minimum_payout = models.DecimalField(_('paiement minimum'), max_digits=10, decimal_places=2, default=50)
    cookie_duration_days = models.PositiveIntegerField(_('durée des cookies (jours)'), default=30)
    
    # Statut
    is_active = models.BooleanField(_('actif'), default=True)
    
    created_at = models.DateTimeField(_('créé le'), auto_now_add=True)
    updated_at = models.DateTimeField(_('modifié le'), auto_now=True)
    
    class Meta:
        verbose_name = _('Programme d\'affiliation')
        verbose_name_plural = _('Programmes d\'affiliation')
    
    def __str__(self):
        return self.name


class Affiliate(models.Model):
    """Affiliés"""
    
    STATUS_CHOICES = [
        ('pending', _('En attente')),
        ('approved', _('Approuvé')),
        ('suspended', _('Suspendu')),
        ('rejected', _('Rejeté')),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='affiliate')
    program = models.ForeignKey(AffiliateProgram, on_delete=models.CASCADE, related_name='affiliates')
    
    # Informations
    company_name = models.CharField(_('nom de l\'entreprise'), max_length=200, blank=True)
    website_url = models.URLField(_('URL du site web'), blank=True)
    description = models.TextField(_('description'), blank=True)
    
    # Code d'affiliation
    affiliate_code = models.CharField(_('code d\'affiliation'), max_length=50, unique=True)
    
    # Statut
    status = models.CharField(_('statut'), max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Statistiques
    total_clicks = models.PositiveIntegerField(_('total clics'), default=0)
    total_conversions = models.PositiveIntegerField(_('total conversions'), default=0)
    total_commission = models.DecimalField(_('total commission'), max_digits=12, decimal_places=2, default=0)
    total_paid = models.DecimalField(_('total payé'), max_digits=12, decimal_places=2, default=0)
    
    # Dates
    applied_at = models.DateTimeField(_('candidature le'), auto_now_add=True)
    approved_at = models.DateTimeField(_('approuvé le'), null=True, blank=True)
    
    class Meta:
        verbose_name = _('Affilié')
        verbose_name_plural = _('Affiliés')
    
    def __str__(self):
        return f"{self.user.email} - {self.affiliate_code}"
    
    @property
    def conversion_rate(self):
        """Taux de conversion"""
        if self.total_clicks > 0:
            return (self.total_conversions / self.total_clicks) * 100
        return 0
    
    @property
    def pending_commission(self):
        """Commission en attente"""
        return self.total_commission - self.total_paid


class AffiliateClick(models.Model):
    """Clics d'affiliation"""
    
    affiliate = models.ForeignKey(Affiliate, on_delete=models.CASCADE, related_name='clicks')
    ip_address = models.GenericIPAddressField(_('adresse IP'))
    user_agent = models.TextField(_('user agent'), blank=True)
    referrer = models.URLField(_('référent'), blank=True)
    
    # Produit/Page visitée
    product = models.ForeignKey('products.Product', on_delete=models.SET_NULL, null=True, blank=True, related_name='affiliate_clicks')
    page_url = models.URLField(_('URL de la page'))
    
    # Conversion
    converted = models.BooleanField(_('converti'), default=False)
    order = models.ForeignKey('orders.Order', on_delete=models.SET_NULL, null=True, blank=True, related_name='affiliate_clicks')
    
    timestamp = models.DateTimeField(_('horodatage'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('Clic d\'affiliation')
        verbose_name_plural = _('Clics d\'affiliation')
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.affiliate.affiliate_code} - {self.page_url}"


class EmailTemplate(models.Model):
    """Templates d'emails marketing"""
    
    TEMPLATE_TYPES = [
        ('welcome', _('Email de bienvenue')),
        ('newsletter', _('Newsletter')),
        ('promotional', _('Email promotionnel')),
        ('abandoned_cart', _('Panier abandonné')),
        ('order_confirmation', _('Confirmation de commande')),
        ('order_shipped', _('Commande expédiée')),
        ('birthday', _('Anniversaire')),
        ('reengagement', _('Réengagement')),
    ]
    
    name = models.CharField(_('nom'), max_length=200)
    template_type = models.CharField(_('type de template'), max_length=30, choices=TEMPLATE_TYPES)
    subject = models.CharField(_('sujet'), max_length=200)
    
    # Contenu
    html_content = models.TextField(_('contenu HTML'))
    text_content = models.TextField(_('contenu texte'), blank=True)
    
    # Configuration
    is_active = models.BooleanField(_('actif'), default=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_email_templates')
    
    created_at = models.DateTimeField(_('créé le'), auto_now_add=True)
    updated_at = models.DateTimeField(_('modifié le'), auto_now=True)
    
    class Meta:
        verbose_name = _('Template d\'email')
        verbose_name_plural = _('Templates d\'email')
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.get_template_type_display()})"

