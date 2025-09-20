from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator
from decimal import Decimal

User = get_user_model()


class Warehouse(models.Model):
    """Entrepôts pour la gestion multi-entrepôts"""
    
    name = models.CharField(_('nom'), max_length=100)
    code = models.CharField(_('code'), max_length=10, unique=True)
    address = models.TextField(_('adresse'))
    city = models.CharField(_('ville'), max_length=100)
    postal_code = models.CharField(_('code postal'), max_length=10)
    country = models.CharField(_('pays'), max_length=100, default='France')
    
    # Contact
    contact_person = models.CharField(_('personne de contact'), max_length=100, blank=True)
    phone = models.CharField(_('téléphone'), max_length=20, blank=True)
    email = models.EmailField(_('email'), blank=True)
    
    # Configuration
    is_active = models.BooleanField(_('actif'), default=True)
    is_default = models.BooleanField(_('entrepôt par défaut'), default=False)
    
    # Capacité
    max_capacity = models.PositiveIntegerField(_('capacité maximale'), null=True, blank=True)
    current_capacity = models.PositiveIntegerField(_('capacité actuelle'), default=0)
    
    created_at = models.DateTimeField(_('créé le'), auto_now_add=True)
    updated_at = models.DateTimeField(_('modifié le'), auto_now=True)
    
    class Meta:
        verbose_name = _('Entrepôt')
        verbose_name_plural = _('Entrepôts')
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.code})"
    
    def save(self, *args, **kwargs):
        # S'assurer qu'il n'y a qu'un seul entrepôt par défaut
        if self.is_default:
            Warehouse.objects.filter(is_default=True).update(is_default=False)
        super().save(*args, **kwargs)


class StockMovement(models.Model):
    """Mouvements de stock"""
    
    MOVEMENT_TYPES = [
        ('in', _('Entrée')),
        ('out', _('Sortie')),
        ('transfer', _('Transfert')),
        ('adjustment', _('Ajustement')),
        ('return', _('Retour')),
        ('damage', _('Dommage')),
        ('expired', _('Expiré')),
    ]
    
    REASONS = [
        ('purchase', _('Achat')),
        ('sale', _('Vente')),
        ('transfer', _('Transfert entre entrepôts')),
        ('adjustment', _('Ajustement manuel')),
        ('return', _('Retour client')),
        ('damage', _('Produit endommagé')),
        ('expired', _('Produit expiré')),
        ('theft', _('Vol')),
        ('other', _('Autre')),
    ]
    
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE, related_name='stock_movements')
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name='stock_movements')
    
    movement_type = models.CharField(_('type de mouvement'), max_length=20, choices=MOVEMENT_TYPES)
    reason = models.CharField(_('raison'), max_length=20, choices=REASONS)
    
    quantity = models.IntegerField(_('quantité'), validators=[MinValueValidator(1)])
    unit_cost = models.DecimalField(_('coût unitaire'), max_digits=10, decimal_places=2, null=True, blank=True)
    total_cost = models.DecimalField(_('coût total'), max_digits=12, decimal_places=2, null=True, blank=True)
    
    # Références
    reference_number = models.CharField(_('numéro de référence'), max_length=100, blank=True)
    order = models.ForeignKey('orders.Order', on_delete=models.SET_NULL, null=True, blank=True, related_name='stock_movements')
    
    # Métadonnées
    notes = models.TextField(_('notes'), blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='stock_movements')
    
    timestamp = models.DateTimeField(_('horodatage'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('Mouvement de stock')
        verbose_name_plural = _('Mouvements de stock')
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['product', 'warehouse']),
            models.Index(fields=['movement_type', 'timestamp']),
            models.Index(fields=['reference_number']),
        ]
    
    def __str__(self):
        return f"{self.product.name} - {self.get_movement_type_display()} ({self.quantity})"
    
    def save(self, *args, **kwargs):
        # Calculer le coût total
        if self.unit_cost and self.quantity:
            self.total_cost = self.unit_cost * self.quantity
        super().save(*args, **kwargs)


class StockLevel(models.Model):
    """Niveaux de stock par produit et entrepôt"""
    
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE, related_name='stock_levels')
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name='stock_levels')
    
    # Stock actuel
    current_stock = models.PositiveIntegerField(_('stock actuel'), default=0)
    reserved_stock = models.PositiveIntegerField(_('stock réservé'), default=0)
    available_stock = models.PositiveIntegerField(_('stock disponible'), default=0)
    
    # Seuils
    min_stock_level = models.PositiveIntegerField(_('stock minimum'), default=0)
    max_stock_level = models.PositiveIntegerField(_('stock maximum'), null=True, blank=True)
    reorder_point = models.PositiveIntegerField(_('point de réapprovisionnement'), default=0)
    reorder_quantity = models.PositiveIntegerField(_('quantité de réapprovisionnement'), default=0)
    
    # Coûts
    average_cost = models.DecimalField(_('coût moyen'), max_digits=10, decimal_places=2, default=0)
    last_cost = models.DecimalField(_('dernier coût'), max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Dates
    last_movement = models.DateTimeField(_('dernier mouvement'), null=True, blank=True)
    last_count = models.DateTimeField(_('dernier inventaire'), null=True, blank=True)
    
    created_at = models.DateTimeField(_('créé le'), auto_now_add=True)
    updated_at = models.DateTimeField(_('modifié le'), auto_now=True)
    
    class Meta:
        verbose_name = _('Niveau de stock')
        verbose_name_plural = _('Niveaux de stock')
        unique_together = ['product', 'warehouse']
        ordering = ['product__name', 'warehouse__name']
    
    def __str__(self):
        return f"{self.product.name} - {self.warehouse.name} ({self.current_stock})"
    
    def save(self, *args, **kwargs):
        # Calculer le stock disponible
        self.available_stock = max(0, self.current_stock - self.reserved_stock)
        super().save(*args, **kwargs)
    
    @property
    def is_low_stock(self):
        """Vérifie si le stock est bas"""
        return self.available_stock <= self.min_stock_level
    
    @property
    def needs_reorder(self):
        """Vérifie si un réapprovisionnement est nécessaire"""
        return self.available_stock <= self.reorder_point


class StockAlert(models.Model):
    """Alertes de stock"""
    
    ALERT_TYPES = [
        ('low_stock', _('Stock bas')),
        ('out_of_stock', _('Rupture de stock')),
        ('overstock', _('Surstock')),
        ('expiring', _('Expiration proche')),
        ('reorder', _('Réapprovisionnement nécessaire')),
    ]
    
    ALERT_LEVELS = [
        ('info', _('Information')),
        ('warning', _('Avertissement')),
        ('critical', _('Critique')),
    ]
    
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE, related_name='stock_alerts')
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name='stock_alerts')
    stock_level = models.ForeignKey(StockLevel, on_delete=models.CASCADE, related_name='alerts')
    
    alert_type = models.CharField(_('type d\'alerte'), max_length=20, choices=ALERT_TYPES)
    alert_level = models.CharField(_('niveau d\'alerte'), max_length=10, choices=ALERT_LEVELS, default='warning')
    
    message = models.TextField(_('message'))
    current_stock = models.PositiveIntegerField(_('stock actuel'))
    threshold = models.PositiveIntegerField(_('seuil'))
    
    # Statut
    is_active = models.BooleanField(_('actif'), default=True)
    is_resolved = models.BooleanField(_('résolu'), default=False)
    resolved_at = models.DateTimeField(_('résolu le'), null=True, blank=True)
    resolved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='resolved_alerts')
    
    created_at = models.DateTimeField(_('créé le'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('Alerte de stock')
        verbose_name_plural = _('Alertes de stock')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['alert_type', 'is_active']),
            models.Index(fields=['alert_level', 'is_resolved']),
        ]
    
    def __str__(self):
        return f"{self.product.name} - {self.get_alert_type_display()}"


class InventoryCount(models.Model):
    """Inventaires physiques"""
    
    STATUS_CHOICES = [
        ('planned', _('Planifié')),
        ('in_progress', _('En cours')),
        ('completed', _('Terminé')),
        ('cancelled', _('Annulé')),
    ]
    
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name='inventory_counts')
    name = models.CharField(_('nom'), max_length=200)
    description = models.TextField(_('description'), blank=True)
    
    status = models.CharField(_('statut'), max_length=20, choices=STATUS_CHOICES, default='planned')
    
    # Dates
    planned_date = models.DateTimeField(_('date planifiée'))
    started_at = models.DateTimeField(_('commencé le'), null=True, blank=True)
    completed_at = models.DateTimeField(_('terminé le'), null=True, blank=True)
    
    # Responsables
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_inventory_counts')
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_inventory_counts')
    
    # Résultats
    total_products = models.PositiveIntegerField(_('total produits'), default=0)
    counted_products = models.PositiveIntegerField(_('produits comptés'), default=0)
    discrepancies = models.PositiveIntegerField(_('écarts'), default=0)
    
    created_at = models.DateTimeField(_('créé le'), auto_now_add=True)
    updated_at = models.DateTimeField(_('modifié le'), auto_now=True)
    
    class Meta:
        verbose_name = _('Inventaire')
        verbose_name_plural = _('Inventaires')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.warehouse.name}"


class InventoryCountItem(models.Model):
    """Éléments d'un inventaire"""
    
    inventory_count = models.ForeignKey(InventoryCount, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE, related_name='inventory_count_items')
    
    # Quantités
    expected_quantity = models.PositiveIntegerField(_('quantité attendue'))
    counted_quantity = models.PositiveIntegerField(_('quantité comptée'), null=True, blank=True)
    difference = models.IntegerField(_('différence'), default=0)
    
    # Statut
    is_counted = models.BooleanField(_('compté'), default=False)
    has_discrepancy = models.BooleanField(_('a un écart'), default=False)
    
    # Notes
    notes = models.TextField(_('notes'), blank=True)
    counted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='counted_items')
    counted_at = models.DateTimeField(_('compté le'), null=True, blank=True)
    
    class Meta:
        verbose_name = _('Élément d\'inventaire')
        verbose_name_plural = _('Éléments d\'inventaire')
        unique_together = ['inventory_count', 'product']
    
    def __str__(self):
        return f"{self.product.name} - {self.expected_quantity} (compté: {self.counted_quantity})"
    
    def save(self, *args, **kwargs):
        if self.counted_quantity is not None:
            self.difference = self.counted_quantity - self.expected_quantity
            self.has_discrepancy = self.difference != 0
            self.is_counted = True
        super().save(*args, **kwargs)


class Supplier(models.Model):
    """Fournisseurs"""
    
    name = models.CharField(_('nom'), max_length=200)
    code = models.CharField(_('code'), max_length=20, unique=True)
    
    # Contact
    contact_person = models.CharField(_('personne de contact'), max_length=100, blank=True)
    email = models.EmailField(_('email'), blank=True)
    phone = models.CharField(_('téléphone'), max_length=20, blank=True)
    
    # Adresse
    address = models.TextField(_('adresse'), blank=True)
    city = models.CharField(_('ville'), max_length=100, blank=True)
    postal_code = models.CharField(_('code postal'), max_length=10, blank=True)
    country = models.CharField(_('pays'), max_length=100, default='France')
    
    # Informations commerciales
    payment_terms = models.CharField(_('conditions de paiement'), max_length=100, blank=True)
    delivery_time_days = models.PositiveIntegerField(_('délai de livraison (jours)'), default=7)
    minimum_order_value = models.DecimalField(_('valeur minimum de commande'), max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Statut
    is_active = models.BooleanField(_('actif'), default=True)
    is_preferred = models.BooleanField(_('fournisseur préféré'), default=False)
    
    # Notes
    notes = models.TextField(_('notes'), blank=True)
    
    created_at = models.DateTimeField(_('créé le'), auto_now_add=True)
    updated_at = models.DateTimeField(_('modifié le'), auto_now=True)
    
    class Meta:
        verbose_name = _('Fournisseur')
        verbose_name_plural = _('Fournisseurs')
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.code})"


class PurchaseOrder(models.Model):
    """Commandes d'achat"""
    
    STATUS_CHOICES = [
        ('draft', _('Brouillon')),
        ('sent', _('Envoyée')),
        ('confirmed', _('Confirmée')),
        ('partial', _('Partiellement reçue')),
        ('received', _('Reçue')),
        ('cancelled', _('Annulée')),
    ]
    
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name='purchase_orders')
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name='purchase_orders')
    
    order_number = models.CharField(_('numéro de commande'), max_length=50, unique=True)
    status = models.CharField(_('statut'), max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # Dates
    order_date = models.DateTimeField(_('date de commande'), auto_now_add=True)
    expected_delivery = models.DateTimeField(_('livraison prévue'), null=True, blank=True)
    actual_delivery = models.DateTimeField(_('livraison effective'), null=True, blank=True)
    
    # Montants
    subtotal = models.DecimalField(_('sous-total'), max_digits=12, decimal_places=2, default=0)
    tax_amount = models.DecimalField(_('montant des taxes'), max_digits=12, decimal_places=2, default=0)
    total_amount = models.DecimalField(_('montant total'), max_digits=12, decimal_places=2, default=0)
    
    # Métadonnées
    notes = models.TextField(_('notes'), blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_purchase_orders')
    
    created_at = models.DateTimeField(_('créé le'), auto_now_add=True)
    updated_at = models.DateTimeField(_('modifié le'), auto_now=True)
    
    class Meta:
        verbose_name = _('Commande d\'achat')
        verbose_name_plural = _('Commandes d\'achat')
        ordering = ['-order_date']
    
    def __str__(self):
        return f"{self.order_number} - {self.supplier.name}"
    
    def save(self, *args, **kwargs):
        if not self.order_number:
            # Générer un numéro de commande
            from django.utils import timezone
            date_str = timezone.now().strftime('%Y%m%d')
            last_order = PurchaseOrder.objects.filter(order_number__startswith=date_str).order_by('-order_number').first()
            if last_order:
                last_num = int(last_order.order_number[-4:])
                new_num = last_num + 1
            else:
                new_num = 1
            self.order_number = f"PO{date_str}{new_num:04d}"
        
        super().save(*args, **kwargs)


class PurchaseOrderItem(models.Model):
    """Éléments d'une commande d'achat"""
    
    purchase_order = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE, related_name='purchase_order_items')
    
    quantity_ordered = models.PositiveIntegerField(_('quantité commandée'))
    quantity_received = models.PositiveIntegerField(_('quantité reçue'), default=0)
    unit_cost = models.DecimalField(_('coût unitaire'), max_digits=10, decimal_places=2)
    total_cost = models.DecimalField(_('coût total'), max_digits=12, decimal_places=2)
    
    # Dates
    expected_delivery = models.DateTimeField(_('livraison prévue'), null=True, blank=True)
    actual_delivery = models.DateTimeField(_('livraison effective'), null=True, blank=True)
    
    notes = models.TextField(_('notes'), blank=True)
    
    class Meta:
        verbose_name = _('Élément de commande d\'achat')
        verbose_name_plural = _('Éléments de commande d\'achat')
        unique_together = ['purchase_order', 'product']
    
    def __str__(self):
        return f"{self.product.name} - {self.quantity_ordered} @ {self.unit_cost}"
    
    def save(self, *args, **kwargs):
        self.total_cost = self.quantity_ordered * self.unit_cost
        super().save(*args, **kwargs)
    
    @property
    def is_fully_received(self):
        return self.quantity_received >= self.quantity_ordered
    
    @property
    def remaining_quantity(self):
        return self.quantity_ordered - self.quantity_received

