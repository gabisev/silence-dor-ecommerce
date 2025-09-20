# 🚀 Guide de Déploiement sur Render - Silence d'Or

## 🎯 **Vue d'Ensemble**

Ce guide vous accompagne dans le déploiement de votre e-commerce "Silence d'Or" sur la plateforme Render. Render est une plateforme cloud moderne qui simplifie le déploiement d'applications Django.

---

## 📋 **Prérequis**

### **Comptes Requis**
- ✅ **Compte GitHub** - Pour héberger le code
- ✅ **Compte Render** - Pour déployer l'application
- ✅ **Compte Stripe** - Pour les paiements (optionnel)
- ✅ **Compte Gmail** - Pour l'envoi d'emails (optionnel)

### **Outils Requis**
- ✅ **Git** - Pour la gestion de version
- ✅ **Python 3.11+** - Pour le développement local
- ✅ **Navigateur web** - Pour accéder aux interfaces

---

## 🔧 **Préparation du Code**

### **1. Vérifier les Fichiers de Déploiement**

Assurez-vous que tous les fichiers suivants sont présents :

```
silence-dor-ecommerce/
├── requirements.txt              # Dépendances Python
├── render.yaml                  # Configuration Render
├── env.example                  # Variables d'environnement
├── silence_dor/
│   ├── settings_production.py   # Settings de production
│   └── urls.py                  # URLs avec health check
├── scripts/
│   └── deploy.py                # Script de déploiement
└── .gitignore                   # Fichiers à ignorer
```

### **2. Exécuter le Script de Préparation**

```bash
# Exécuter le script de déploiement
python scripts/deploy.py
```

Ce script va :
- ✅ Vérifier tous les fichiers requis
- ✅ Créer le health check
- ✅ Tester la configuration
- ✅ Préparer les fichiers statiques

---

## 📤 **Déploiement sur GitHub**

### **1. Initialiser Git (si pas déjà fait)**

```bash
# Initialiser le repository
git init

# Ajouter tous les fichiers
git add .

# Premier commit
git commit -m "Initial commit - Silence d'Or E-commerce"
```

### **2. Créer un Repository GitHub**

1. **Aller sur GitHub.com**
2. **Cliquer sur "New repository"**
3. **Nommer le repository** : `silence-dor-ecommerce`
4. **Choisir "Public" ou "Private"**
5. **Ne pas initialiser** avec README (déjà présent)

### **3. Connecter le Repository Local**

```bash
# Ajouter l'origine GitHub
git remote add origin https://github.com/VOTRE_USERNAME/silence-dor-ecommerce.git

# Pousser le code
git push -u origin main
```

---

## 🌐 **Configuration sur Render**

### **1. Créer un Compte Render**

1. **Aller sur render.com**
2. **S'inscrire** avec votre compte GitHub
3. **Autoriser l'accès** à vos repositories

### **2. Créer un Nouveau Service**

1. **Cliquer sur "New +"**
2. **Choisir "Web Service"**
3. **Connecter votre repository GitHub**
4. **Sélectionner** `silence-dor-ecommerce`

### **3. Configuration du Service Web**

**Informations de base :**
- **Name** : `silence-dor-web`
- **Environment** : `Python 3`
- **Region** : `Oregon (US West)`
- **Branch** : `main`
- **Root Directory** : `/` (laisser vide)

**Build & Deploy :**
- **Build Command** :
  ```bash
  pip install -r requirements.txt && python manage.py collectstatic --noinput --settings=silence_dor.settings_production && python manage.py migrate --settings=silence_dor.settings_production
  ```
- **Start Command** :
  ```bash
  gunicorn silence_dor.wsgi:application --bind 0.0.0.0:$PORT --settings=silence_dor.settings_production
  ```

### **4. Variables d'Environnement**

Ajouter les variables suivantes dans l'onglet "Environment" :

#### **Configuration Django**
```
DJANGO_SETTINGS_MODULE=silence_dor.settings_production
DEBUG=false
SECRET_KEY=[Généré automatiquement par Render]
ALLOWED_HOSTS=silence-dor.onrender.com,www.silence-dor.com
```

#### **Base de Données (automatique)**
```
DATABASE_URL=[Fourni automatiquement par Render]
```

#### **Cache Redis (automatique)**
```
REDIS_URL=[Fourni automatiquement par Render]
CELERY_BROKER_URL=[Fourni automatiquement par Render]
CELERY_RESULT_BACKEND=[Fourni automatiquement par Render]
```

#### **Email (optionnel)**
```
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=true
EMAIL_HOST_USER=votre-email@gmail.com
EMAIL_HOST_PASSWORD=votre-mot-de-passe-app
DEFAULT_FROM_EMAIL=noreply@silence-dor.com
```

#### **Stripe (optionnel)**
```
STRIPE_PUBLISHABLE_KEY=pk_test_votre_cle_publique
STRIPE_SECRET_KEY=sk_test_votre_cle_secrete
STRIPE_WEBHOOK_SECRET=whsec_votre_secret_webhook
```

---

## 🗄️ **Configuration de la Base de Données**

### **1. Créer une Base de Données PostgreSQL**

1. **Dans Render, cliquer sur "New +"**
2. **Choisir "PostgreSQL"**
3. **Configuration :**
   - **Name** : `silence-dor-db`
   - **Database** : `silence_dor`
   - **User** : `silence_dor_user`
   - **Region** : `Oregon (US West)`
   - **Plan** : `Starter` (gratuit)

### **2. Connecter la Base de Données**

1. **Aller dans votre service web**
2. **Onglet "Environment"**
3. **La variable `DATABASE_URL` est automatiquement ajoutée**

---

## 🔄 **Configuration de Redis**

### **1. Créer un Service Redis**

1. **Dans Render, cliquer sur "New +"**
2. **Choisir "Redis"**
3. **Configuration :**
   - **Name** : `silence-dor-redis`
   - **Region** : `Oregon (US West)`
   - **Plan** : `Starter` (gratuit)

### **2. Connecter Redis**

1. **Aller dans votre service web**
2. **Onglet "Environment"**
3. **Les variables Redis sont automatiquement ajoutées**

---

## ⚙️ **Services Supplémentaires**

### **1. Celery Worker (optionnel)**

Pour les tâches asynchrones :

1. **Créer un nouveau service "Background Worker"**
2. **Configuration :**
   - **Name** : `silence-dor-worker`
   - **Environment** : `Python 3`
   - **Build Command** : `pip install -r requirements.txt`
   - **Start Command** : `celery -A silence_dor worker --loglevel=info`

### **2. Celery Beat (optionnel)**

Pour les tâches programmées :

1. **Créer un nouveau service "Background Worker"**
2. **Configuration :**
   - **Name** : `silence-dor-beat`
   - **Environment** : `Python 3`
   - **Build Command** : `pip install -r requirements.txt`
   - **Start Command** : `celery -A silence_dor beat --loglevel=info`

---

## 🚀 **Déploiement**

### **1. Déployer l'Application**

1. **Cliquer sur "Create Web Service"**
2. **Attendre la construction** (5-10 minutes)
3. **Vérifier les logs** pour détecter les erreurs

### **2. Vérifier le Déploiement**

1. **Aller sur l'URL fournie** : `https://silence-dor.onrender.com`
2. **Tester le health check** : `https://silence-dor.onrender.com/health/`
3. **Vérifier l'admin** : `https://silence-dor.onrender.com/admin/`

### **3. Créer un Superutilisateur**

```bash
# Via le terminal Render ou en local
python manage.py createsuperuser --settings=silence_dor.settings_production
```

---

## 🔧 **Configuration Post-Déploiement**

### **1. Initialiser les Données**

1. **Se connecter à l'admin** : `/admin/`
2. **Configurer les informations du site** : `Core > Site Information`
3. **Ajouter des catégories** : `Products > Categories`
4. **Ajouter des produits** : `Products > Products`

### **2. Configuration des Emails**

1. **Aller dans l'admin**
2. **Configurer les templates d'emails**
3. **Tester l'envoi d'emails**

### **3. Configuration Stripe**

1. **Ajouter les clés Stripe** dans les variables d'environnement
2. **Configurer les webhooks** dans le dashboard Stripe
3. **Tester les paiements**

---

## 📊 **Monitoring et Maintenance**

### **1. Logs**

- **Accéder aux logs** : Onglet "Logs" dans Render
- **Surveiller les erreurs** : Rechercher "ERROR" ou "CRITICAL"
- **Vérifier les performances** : Temps de réponse

### **2. Métriques**

- **CPU et RAM** : Surveillance automatique
- **Requêtes** : Nombre de requêtes par minute
- **Erreurs** : Taux d'erreur HTTP

### **3. Sauvegardes**

- **Base de données** : Sauvegardes automatiques quotidiennes
- **Fichiers** : Stockage persistant sur Render
- **Code** : Sauvegardé sur GitHub

---

## 🔒 **Sécurité**

### **1. HTTPS**

- **Automatique** : Render fournit HTTPS automatiquement
- **Certificats** : Gérés automatiquement
- **Redirection** : HTTP vers HTTPS automatique

### **2. Variables d'Environnement**

- **Secrets** : Stockés de manière sécurisée
- **Rotation** : Changer régulièrement les clés
- **Accès** : Limité aux administrateurs

### **3. Firewall**

- **DDoS Protection** : Incluse dans Render
- **Rate Limiting** : Configurable
- **IP Whitelisting** : Pour l'admin (optionnel)

---

## 🆘 **Dépannage**

### **1. Problèmes Courants**

#### **Erreur de Build**
```bash
# Vérifier les logs de build
# Vérifier requirements.txt
# Vérifier la version Python
```

#### **Erreur de Base de Données**
```bash
# Vérifier DATABASE_URL
# Vérifier les migrations
# Vérifier les permissions
```

#### **Erreur de Fichiers Statiques**
```bash
# Vérifier collectstatic
# Vérifier STATIC_ROOT
# Vérifier WhiteNoise
```

### **2. Commandes de Diagnostic**

```bash
# Vérifier la configuration
python manage.py check --settings=silence_dor.settings_production

# Vérifier les migrations
python manage.py showmigrations --settings=silence_dor.settings_production

# Tester la base de données
python manage.py dbshell --settings=silence_dor.settings_production
```

### **3. Support**

- **Documentation Render** : https://render.com/docs
- **Community** : https://community.render.com
- **Support** : Via le dashboard Render

---

## 📈 **Optimisation**

### **1. Performance**

- **Cache** : Utiliser Redis pour le cache
- **CDN** : Activer le CDN Render
- **Compression** : Gzip automatique
- **Images** : Optimiser les images

### **2. Coûts**

- **Plan Starter** : Gratuit (limité)
- **Plan Standard** : $7/mois (recommandé)
- **Plan Pro** : $25/mois (haute disponibilité)

### **3. Scaling**

- **Horizontal** : Ajouter des instances
- **Vertical** : Augmenter les ressources
- **Auto-scaling** : Basé sur la charge

---

## 🎉 **Félicitations !**

Votre e-commerce "Silence d'Or" est maintenant déployé sur Render ! 

### **Prochaines Étapes :**

1. **🔧 Configurer** les fonctionnalités avancées
2. **📊 Monitorer** les performances
3. **🚀 Optimiser** selon les besoins
4. **📈 Analyser** les métriques
5. **🔄 Maintenir** et mettre à jour

### **URLs Importantes :**

- **Site principal** : `https://silence-dor.onrender.com`
- **Administration** : `https://silence-dor.onrender.com/admin/`
- **Health check** : `https://silence-dor.onrender.com/health/`
- **Analytics** : `https://silence-dor.onrender.com/analytics/`

**Bon succès avec votre e-commerce en ligne ! 🎊**

---

*Guide de déploiement Render - Silence d'Or E-commerce*  
*Version 1.0 - Septembre 2025*
