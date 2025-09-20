# 🔐 Guide d'Administration - Silence d'Or

## 🚀 **Accès à l'Interface d'Administration**

### **Informations de Connexion**
- **URL** : http://localhost:8000/admin/
- **Email** : `admin@silence-dor.com`
- **Mot de passe** : `admin123`

## 📊 **Fonctionnalités Administratives**

### **1. Gestion des Utilisateurs**
- **Créer des comptes** utilisateurs
- **Modifier les profils** clients
- **Gérer les permissions** et rôles
- **Voir les statistiques** d'inscription

### **2. Gestion des Produits**
- **Ajouter des produits** avec images
- **Créer des catégories** et sous-catégories
- **Gérer les marques** et fabricants
- **Contrôler les stocks** et prix
- **Mettre en vedette** des produits

### **3. Gestion des Commandes**
- **Voir toutes les commandes** clients
- **Suivre le statut** des livraisons
- **Gérer les remboursements**
- **Exporter les rapports** de ventes

### **4. Gestion du Panier et Favoris**
- **Voir les paniers** actifs
- **Analyser les listes de souhaits**
- **Comprendre le comportement** d'achat

### **5. Gestion des Paiements**
- **Suivre les transactions** Stripe
- **Gérer les remboursements**
- **Voir l'historique** des paiements

## 🛠️ **Actions Administratives Courantes**

### **Ajouter un Nouveau Produit**
1. Aller dans **Products** → **Products**
2. Cliquer sur **"Add Product"**
3. Remplir les informations :
   - Nom du produit
   - Description détaillée
   - Prix et stock
   - Catégorie et marque
   - Images du produit
4. Sauvegarder

### **Créer une Catégorie**
1. Aller dans **Products** → **Categories**
2. Cliquer sur **"Add Category"**
3. Remplir :
   - Nom de la catégorie
   - Description
   - Image de la catégorie
4. Sauvegarder

### **Gérer les Commandes**
1. Aller dans **Orders** → **Orders**
2. Voir la liste des commandes
3. Cliquer sur une commande pour :
   - Voir les détails
   - Changer le statut
   - Gérer la livraison

### **Analyser les Utilisateurs**
1. Aller dans **Accounts** → **Users**
2. Voir tous les utilisateurs inscrits
3. Cliquer sur un utilisateur pour :
   - Voir le profil complet
   - Modifier les informations
   - Voir l'historique des commandes

## 📈 **Tableau de Bord Principal**

L'interface d'administration Django vous donne accès à :

### **Sections Principales**
- **👥 Accounts** - Gestion des utilisateurs
- **🛍️ Products** - Catalogue de produits
- **📦 Orders** - Commandes et livraisons
- **🛒 Cart** - Paniers et favoris
- **💳 Payments** - Transactions et paiements
- **🏠 Core** - Pages du site

### **Statistiques Disponibles**
- Nombre total d'utilisateurs
- Produits en stock
- Commandes en cours
- Revenus générés
- Produits les plus vendus

## 🔧 **Fonctionnalités Avancées**

### **Recherche et Filtres**
- **Recherche rapide** dans toutes les sections
- **Filtres par date** pour les commandes
- **Filtres par statut** pour les produits
- **Tri personnalisé** des listes

### **Actions en Lot**
- **Sélection multiple** d'éléments
- **Actions groupées** (suppression, modification)
- **Export de données** en CSV/Excel

### **Notifications**
- **Alertes de stock** bas
- **Nouvelles commandes** en temps réel
- **Messages d'erreur** système

## 🚨 **Sécurité et Maintenance**

### **Bonnes Pratiques**
- **Changer le mot de passe** admin régulièrement
- **Sauvegarder la base de données** régulièrement
- **Surveiller les logs** d'erreur
- **Mettre à jour** les dépendances

### **Sauvegarde**
```bash
# Sauvegarder la base de données
python manage.py dumpdata > backup.json

# Restaurer la base de données
python manage.py loaddata backup.json
```

## 📱 **Accès Mobile**

L'interface d'administration est **responsive** et fonctionne sur :
- **Ordinateurs** de bureau
- **Tablettes** et iPads
- **Smartphones** (interface adaptée)

## 🎯 **Prochaines Étapes**

Une fois connecté à l'admin, vous pouvez :

1. **📊 Explorer le tableau de bord** - Voir les statistiques générales
2. **🛍️ Ajouter des produits** - Commencer à peupler le catalogue
3. **👥 Gérer les utilisateurs** - Voir les comptes créés
4. **📦 Suivre les commandes** - Analyser les ventes
5. **⚙️ Configurer les paramètres** - Personnaliser le site

## ✨ **Conseils d'Utilisation**

- **Utilisez les filtres** pour naviguer efficacement
- **Sauvegardez régulièrement** vos modifications
- **Testez les fonctionnalités** avant de les publier
- **Surveillez les performances** du site

---

**🎉 Votre interface d'administration est maintenant prête !**

**Connectez-vous à : http://localhost:8000/admin/**

