# 📚 Guide Utilisateur Admin - Silence d'Or E-commerce

---

## 🎯 **TABLE DES MATIÈRES**

1. [Introduction](#introduction)
2. [Accès à l'Administration](#accès-à-ladministration)
3. [Gestion des Produits](#gestion-des-produits)
4. [Gestion des Commandes](#gestion-des-commandes)
5. [Gestion des Utilisateurs](#gestion-des-utilisateurs)
6. [Fonctionnalités Avancées](#fonctionnalités-avancées)
7. [Configuration du Site](#configuration-du-site)
8. [Sécurité et Maintenance](#sécurité-et-maintenance)
9. [Dépannage](#dépannage)
10. [Support](#support)

---

## 📖 **INTRODUCTION**

Bienvenue dans le guide d'administration de votre e-commerce "Silence d'Or" ! Ce guide vous accompagnera dans la gestion quotidienne de votre boutique en ligne.

### **Ce que vous apprendrez :**
- ✅ Comment accéder et naviguer dans l'interface d'administration
- ✅ Comment gérer vos produits, commandes et clients
- ✅ Comment utiliser les fonctionnalités avancées
- ✅ Comment configurer et sécuriser votre site
- ✅ Comment résoudre les problèmes courants

---

## 🔐 **ACCÈS À L'ADMINISTRATION**

### **1. Connexion à l'Administration**

**URL d'accès :** `http://127.0.0.1:8000/admin/`

**Étapes de connexion :**
1. Ouvrez votre navigateur web
2. Tapez l'URL d'administration
3. Entrez vos identifiants administrateur
4. Cliquez sur "Se connecter"

### **2. Création d'un Superutilisateur**

Si vous n'avez pas encore de compte administrateur :

```bash
python manage.py createsuperuser --settings=silence_dor.settings_simple
```

**Informations requises :**
- Nom d'utilisateur
- Adresse email
- Mot de passe (minimum 8 caractères)

### **3. Interface d'Administration**

L'interface d'administration se compose de :

- **📊 Tableau de bord** - Vue d'ensemble des statistiques
- **🛍️ Produits** - Gestion du catalogue
- **📦 Commandes** - Suivi des ventes
- **👥 Utilisateurs** - Gestion des clients
- **⚙️ Configuration** - Paramètres du site
- **🔧 Fonctionnalités avancées** - Outils professionnels

---

## 🛍️ **GESTION DES PRODUITS**

### **1. Ajouter un Nouveau Produit**

**Navigation :** `Produits > Produits > Ajouter`

**Informations obligatoires :**
- **Nom du produit** - Titre visible par les clients
- **Description** - Détails du produit
- **Prix** - Prix de vente (en euros)
- **Catégorie** - Classification du produit
- **Stock** - Quantité disponible
- **Images** - Photos du produit

**Informations optionnelles :**
- **SKU** - Code produit unique
- **Marque** - Fabricant du produit
- **Poids** - Pour le calcul des frais de port
- **Dimensions** - Taille du produit
- **Produit en vedette** - Mise en avant sur la page d'accueil

### **2. Gérer les Catégories**

**Navigation :** `Produits > Catégories`

**Actions disponibles :**
- ✅ **Créer une catégorie** - Nouvelle classification
- ✅ **Modifier une catégorie** - Éditer les informations
- ✅ **Supprimer une catégorie** - Retirer du catalogue
- ✅ **Réorganiser** - Ordre d'affichage

**Conseils :**
- Utilisez des noms clairs et descriptifs
- Organisez en hiérarchie (catégorie > sous-catégorie)
- Ajoutez des descriptions pour le SEO

### **3. Gérer les Marques**

**Navigation :** `Produits > Marques`

**Fonctionnalités :**
- ✅ **Ajouter une marque** - Nouveau fabricant
- ✅ **Logo de marque** - Image représentative
- ✅ **Description** - Informations sur la marque
- ✅ **Site web** - Lien vers le site officiel

### **4. Gestion des Images**

**Bonnes pratiques :**
- **Format recommandé :** JPG, PNG, WebP
- **Taille optimale :** 800x600 pixels minimum
- **Poids maximum :** 2MB par image
- **Images multiples :** Jusqu'à 5 images par produit

**Ordre des images :**
1. **Image principale** - Photo de couverture
2. **Images secondaires** - Vues supplémentaires
3. **Images détail** - Gros plans, détails

---

## 📦 **GESTION DES COMMANDES**

### **1. Vue d'Ensemble des Commandes**

**Navigation :** `Commandes > Commandes`

**Informations affichées :**
- **Numéro de commande** - Identifiant unique
- **Client** - Nom et email du client
- **Date** - Date de la commande
- **Statut** - État actuel de la commande
- **Montant total** - Prix final de la commande

### **2. Statuts des Commandes**

**Statuts disponibles :**
- 🔄 **En attente** - Commande reçue, en cours de traitement
- ⚙️ **En cours de traitement** - Préparation en cours
- 📦 **Expédiée** - Commande envoyée au client
- ✅ **Livrée** - Commande reçue par le client
- ❌ **Annulée** - Commande annulée
- 🔄 **Remboursée** - Remboursement effectué

### **3. Traitement d'une Commande**

**Étapes de traitement :**

1. **Réception de la commande**
   - Vérifier les informations client
   - Contrôler la disponibilité des produits
   - Valider le paiement

2. **Préparation**
   - Changer le statut en "En cours de traitement"
   - Préparer les articles
   - Générer la facture

3. **Expédition**
   - Changer le statut en "Expédiée"
   - Ajouter le numéro de suivi
   - Envoyer l'email de confirmation

4. **Livraison**
   - Changer le statut en "Livrée"
   - Demander un avis client

### **4. Gestion des Remboursements**

**Processus de remboursement :**
1. **Demande client** - Réception de la demande
2. **Validation** - Vérification des conditions
3. **Traitement** - Remboursement via Stripe
4. **Confirmation** - Notification au client

---

## 👥 **GESTION DES UTILISATEURS**

### **1. Vue d'Ensemble des Clients**

**Navigation :** `Utilisateurs > Utilisateurs`

**Informations client :**
- **Nom et prénom** - Identité du client
- **Email** - Adresse de contact
- **Date d'inscription** - Membre depuis
- **Statut** - Actif/Inactif
- **Dernière connexion** - Activité récente

### **2. Profil Client Détaillé**

**Informations disponibles :**
- **Données personnelles** - Nom, email, téléphone
- **Adresses** - Livraison et facturation
- **Historique des commandes** - Toutes les commandes
- **Statistiques** - Montant total, nombre de commandes
- **Préférences** - Newsletter, langue

### **3. Gestion des Adresses**

**Types d'adresses :**
- **Adresse de livraison** - Où envoyer les commandes
- **Adresse de facturation** - Pour les factures
- **Adresses multiples** - Plusieurs adresses par client

**Actions disponibles :**
- ✅ **Ajouter une adresse** - Nouvelle adresse
- ✅ **Modifier** - Éditer les informations
- ✅ **Supprimer** - Retirer une adresse
- ✅ **Définir par défaut** - Adresse principale

---

## 🚀 **FONCTIONNALITÉS AVANCÉES**

### **1. Analytics et Statistiques**

**Accès :** `http://127.0.0.1:8000/analytics/dashboard/`

**Métriques disponibles :**
- 📊 **Ventes** - Chiffre d'affaires, nombre de commandes
- 👥 **Utilisateurs** - Nouveaux clients, clients actifs
- 🛍️ **Produits** - Produits les plus vendus
- 📈 **Évolution** - Tendances et croissance

**Rapports :**
- **Rapport de ventes** - Analyse des ventes
- **Rapport utilisateurs** - Comportement des clients
- **Rapport produits** - Performance du catalogue

### **2. Système de Recherche Avancée**

**Accès :** `http://127.0.0.1:8000/search/`

**Fonctionnalités :**
- 🔍 **Recherche intelligente** - Suggestions automatiques
- 🎯 **Filtres avancés** - Par catégorie, prix, disponibilité
- 📚 **Historique** - Recherches précédentes
- 🔥 **Tendances** - Recherches populaires

### **3. Notifications et Emails**

**Accès :** `http://127.0.0.1:8000/notifications/`

**Types de notifications :**
- 📧 **Emails transactionnels** - Confirmations, expéditions
- 📰 **Newsletter** - Campagnes marketing
- 🔔 **Notifications système** - Alertes importantes
- 📊 **Logs d'emails** - Suivi des envois

### **4. Système de Recommandations**

**Accès :** `http://127.0.0.1:8000/recommendations/for-me/`

**Fonctionnalités IA :**
- 🤖 **Recommandations personnalisées** - Basées sur l'historique
- 🔗 **Produits similaires** - Suggestions intelligentes
- 🛒 **Cross-selling** - "Fréquemment achetés ensemble"
- 📈 **Analyse comportementale** - Compréhension des clients

### **5. Sécurité Renforcée**

**Accès :** `http://127.0.0.1:8000/security/2fa/setup/`

**Fonctionnalités de sécurité :**
- 🔐 **Authentification 2FA** - Double authentification
- 📋 **Journal d'audit** - Traçabilité complète
- 🚨 **Alertes de sécurité** - Détection d'intrusions
- ⚙️ **Paramètres de sécurité** - Configuration avancée

### **6. Gestion des Stocks**

**Accès :** `http://127.0.0.1:8000/inventory/`

**Fonctionnalités :**
- 🏢 **Multi-entrepôts** - Gestion de plusieurs sites
- 📊 **Mouvements de stock** - Entrées, sorties, transferts
- 🚨 **Alertes automatiques** - Stock bas, rupture
- 📋 **Rapports d'inventaire** - Analyses détaillées

### **7. Marketing et Promotions**

**Accès :** `http://127.0.0.1:8000/marketing/campaigns/`

**Outils marketing :**
- 📢 **Campagnes** - Emails, SMS, notifications push
- 🎫 **Coupons** - Codes de réduction
- ⭐ **Programme de fidélité** - Points et niveaux
- 🤝 **Affiliation** - Programme d'affiliation

---

## ⚙️ **CONFIGURATION DU SITE**

### **1. Informations Générales**

**Navigation :** `Core > Site Information`

**Paramètres configurables :**
- **Nom du site** - "Silence d'Or"
- **Slogan** - Phrase d'accroche
- **Description** - Description du site
- **Image hero** - Bannière de la page d'accueil
- **Logo** - Logo de l'entreprise

### **2. Informations de Contact**

**Paramètres :**
- **Adresse** - Adresse physique de l'entreprise
- **Téléphone** - Numéro de contact
- **Email** - Adresse email de contact
- **Horaires** - Heures d'ouverture

### **3. Réseaux Sociaux**

**Plateformes supportées :**
- **Facebook** - Page Facebook
- **Instagram** - Compte Instagram
- **Twitter** - Compte Twitter
- **LinkedIn** - Page LinkedIn
- **YouTube** - Chaîne YouTube

### **4. Paramètres de Livraison**

**Configuration :**
- **Frais de port** - Coûts de livraison
- **Délais de livraison** - Temps d'expédition
- **Zones de livraison** - Pays/régions couverts
- **Méthodes de livraison** - Colissimo, Chronopost, etc.

---

## 🛡️ **SÉCURITÉ ET MAINTENANCE**

### **1. Sauvegardes**

**Sauvegardes automatiques :**
- **Base de données** - Sauvegarde quotidienne
- **Fichiers média** - Images et documents
- **Configuration** - Paramètres du site

**Sauvegardes manuelles :**
```bash
# Sauvegarde de la base de données
python manage.py dumpdata > backup.json

# Sauvegarde des fichiers média
tar -czf media_backup.tar.gz media/
```

### **2. Mise à Jour**

**Vérifications régulières :**
- **Django** - Version du framework
- **Packages Python** - Dépendances
- **Sécurité** - Correctifs de sécurité

**Commandes de mise à jour :**
```bash
# Mettre à jour les packages
pip install --upgrade -r requirements.txt

# Appliquer les migrations
python manage.py migrate --settings=silence_dor.settings_simple
```

### **3. Monitoring**

**Surveillance continue :**
- **Performance** - Temps de réponse
- **Erreurs** - Logs d'erreurs
- **Sécurité** - Tentatives d'intrusion
- **Disque** - Espace de stockage

### **4. Conformité RGPD**

**Obligations légales :**
- **Consentement** - Collecte des données
- **Droit à l'oubli** - Suppression des données
- **Portabilité** - Export des données
- **Transparence** - Politique de confidentialité

---

## 🔧 **DÉPANNAGE**

### **1. Problèmes Courants**

**Site inaccessible :**
1. Vérifier que le serveur est démarré
2. Contrôler les logs d'erreurs
3. Vérifier la configuration

**Erreurs de base de données :**
1. Appliquer les migrations
2. Vérifier les permissions
3. Contrôler l'espace disque

**Problèmes de performance :**
1. Optimiser les images
2. Vider le cache
3. Vérifier les requêtes

### **2. Logs et Diagnostics**

**Fichiers de logs :**
- **Django** - `logs/django.log`
- **Erreurs** - `logs/error.log`
- **Accès** - `logs/access.log`

**Commandes de diagnostic :**
```bash
# Vérifier la configuration
python manage.py check --settings=silence_dor.settings_simple

# Tester la base de données
python manage.py dbshell --settings=silence_dor.settings_simple

# Vérifier les permissions
python manage.py collectstatic --settings=silence_dor.settings_simple
```

### **3. Récupération d'Urgence**

**En cas de problème majeur :**
1. **Arrêter le serveur** - Éviter les dommages
2. **Restaurer la sauvegarde** - Retour à l'état précédent
3. **Analyser les logs** - Identifier la cause
4. **Corriger le problème** - Résolution
5. **Redémarrer** - Remise en service

---

## 📞 **SUPPORT**

### **1. Ressources d'Aide**

**Documentation :**
- **Guide utilisateur** - Ce document
- **Documentation Django** - https://docs.djangoproject.com/
- **Documentation Stripe** - https://stripe.com/docs

**Communauté :**
- **Forum Django** - https://forum.djangoproject.com/
- **Stack Overflow** - https://stackoverflow.com/questions/tagged/django

### **2. Contact Support**

**En cas de problème :**
1. **Consulter ce guide** - Solutions courantes
2. **Vérifier les logs** - Informations d'erreur
3. **Rechercher en ligne** - Solutions communautaires
4. **Contacter le développeur** - Support technique

### **3. Formation Continue**

**Ressources d'apprentissage :**
- **Tutoriels Django** - Apprentissage du framework
- **E-commerce** - Bonnes pratiques
- **Sécurité web** - Protection des données
- **Marketing digital** - Optimisation des ventes

---

## 🎉 **CONCLUSION**

Félicitations ! Vous disposez maintenant de toutes les connaissances nécessaires pour administrer efficacement votre e-commerce "Silence d'Or".

### **Points Clés à Retenir :**
- ✅ **Utilisez l'interface d'administration** pour gérer votre site
- ✅ **Surveillez régulièrement** les commandes et les stocks
- ✅ **Exploitez les fonctionnalités avancées** pour optimiser vos ventes
- ✅ **Maintenez la sécurité** et effectuez des sauvegardes
- ✅ **Consultez ce guide** en cas de besoin

### **Prochaines Étapes :**
1. **Explorez l'interface** - Familiarisez-vous avec les fonctionnalités
2. **Configurez votre site** - Personnalisez selon vos besoins
3. **Testez les fonctionnalités** - Vérifiez que tout fonctionne
4. **Formez votre équipe** - Partagez ce guide avec vos collaborateurs

**Bon succès avec votre e-commerce ! 🚀**

---

*Guide utilisateur admin - Silence d'Or E-commerce*  
*Version 1.0 - Septembre 2025*
