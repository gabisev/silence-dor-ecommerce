# Silence d'Or - E-commerce

Site e-commerce moderne pour la vente de tous types de produits, développé avec Django.

## 🚀 Fonctionnalités

- **Catalogue produits** : Gestion complète des produits avec catégories et marques
- **Authentification** : Inscription/Connexion utilisateurs avec Django Allauth
- **Panier d'achat** : Gestion des commandes et liste de souhaits
- **Paiements** : Intégration sécurisée avec Stripe
- **Administration** : Interface d'administration Django personnalisée
- **API REST** : API complète avec Django REST Framework
- **Interface moderne** : Design responsive avec Bootstrap 5

## 🛠️ Technologies

### Backend
- **Django 4.2** - Framework web Python
- **Django REST Framework** - API REST
- **PostgreSQL/SQLite** - Base de données
- **Stripe** - Paiements en ligne
- **Redis** - Cache et sessions
- **Celery** - Tâches asynchrones

### Frontend
- **Bootstrap 5** - Framework CSS
- **JavaScript ES6+** - Interactivité
- **Font Awesome** - Icônes
- **Responsive Design** - Mobile-first

## 📦 Installation

### Prérequis
- Python 3.11+
- pip
- PostgreSQL (optionnel, SQLite par défaut)

### Installation rapide

1. **Cloner le projet**
```bash
git clone <repository-url>
cd silence-dor-ecommerce
```

2. **Configuration automatique (recommandé)**
```bash
python scripts/quick_start.py
```

3. **Configuration manuelle alternative**
```bash
chmod +x scripts/setup.sh
./scripts/setup.sh
```

4. **Configuration manuelle détaillée**
```bash
# Créer un environnement virtuel
python3 -m venv venv
source venv/bin/activate  # Sur Windows: venv\Scripts\activate

# Installer les dépendances
pip install -r requirements.txt

# Configuration de l'environnement
cp env.example .env
# Éditer .env avec vos paramètres

# Migrations de base de données
python manage.py makemigrations
python manage.py migrate

# Créer un superutilisateur
python manage.py createsuperuser

# Collecter les fichiers statiques
python manage.py collectstatic --noinput
```

5. **Démarrer le serveur**
```bash
python manage.py runserver
```

## 🔧 Résolution des erreurs

Si vous rencontrez des erreurs lors de l'installation :

### 🚀 Démarrage rapide (sans erreurs)
```bash
# Configuration minimale pour éviter les erreurs
python scripts/start_simple.py
```

### 🔍 Tests de diagnostic
```bash
# Test de configuration complète
python scripts/test_setup.py

# Test de configuration simple
python scripts/test_simple.py
```

### 📚 Guide de dépannage complet
Consultez [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) pour les erreurs courantes et leurs solutions.

### ⚡ Solutions rapides

1. **Erreurs de dépendances**
```bash
pip install --upgrade pip
pip install Django
# Ou pour la configuration complète:
pip install -r requirements.txt
```

2. **Erreurs de base de données**
```bash
# Configuration simple
python manage.py makemigrations --settings=silence_dor.settings_simple
python manage.py migrate --settings=silence_dor.settings_simple

# Configuration complète
python manage.py makemigrations
python manage.py migrate
```

3. **Erreurs de configuration**
```bash
# Utiliser la configuration simple
python manage.py runserver --settings=silence_dor.settings_simple
```

## 🌐 Accès

- **Site web** : http://localhost:8000
- **Interface d'administration** : http://localhost:8000/admin
- **API REST** : http://localhost:8000/api

## 📁 Structure du projet

```
silence-dor-ecommerce/
├── apps/                    # Applications Django
│   ├── accounts/           # Gestion des utilisateurs
│   ├── products/           # Catalogue produits
│   ├── cart/              # Panier et liste de souhaits
│   ├── orders/            # Commandes
│   ├── payments/          # Paiements Stripe
│   └── core/              # Vues principales
├── silence_dor/           # Configuration Django
├── templates/             # Templates HTML
├── static/               # Fichiers statiques (CSS, JS, images)
├── media/                # Fichiers uploadés
├── scripts/              # Scripts de déploiement
└── requirements.txt      # Dépendances Python
```

## 🔧 Configuration

### Variables d'environnement (.env)
```bash
# Configuration Django
SECRET_KEY=your-super-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Base de données
DATABASE_URL=sqlite:///db.sqlite3
# Pour PostgreSQL: postgres://user:password@localhost:5432/silence_dor

# Configuration Stripe
STRIPE_PUBLISHABLE_KEY=pk_test_your_stripe_publishable_key
STRIPE_SECRET_KEY=sk_test_your_stripe_secret_key
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret

# Configuration Email
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=noreply@silence-dor.com
```

## 🚀 Déploiement

### Déploiement automatique
```bash
chmod +x scripts/deploy.sh
./scripts/deploy.sh
```

### Déploiement sur Heroku
```bash
# Installer Heroku CLI
# Créer une application Heroku
heroku create silence-dor-ecommerce

# Configurer les variables d'environnement
heroku config:set SECRET_KEY=your-secret-key
heroku config:set DEBUG=False
heroku config:set ALLOWED_HOSTS=your-app.herokuapp.com

# Déployer
git push heroku main
heroku run python manage.py migrate
heroku run python manage.py createsuperuser
```

## 📚 API Documentation

### Endpoints principaux

#### Produits
- `GET /api/products/` - Liste des produits
- `GET /api/products/{slug}/` - Détails d'un produit
- `POST /api/products/` - Créer un produit (vendeurs)

#### Panier
- `GET /api/cart/` - Récupérer le panier
- `POST /api/cart/add/{product_id}/` - Ajouter au panier
- `DELETE /api/cart/remove/{product_id}/` - Retirer du panier

#### Commandes
- `GET /api/orders/` - Liste des commandes
- `POST /api/orders/create-from-cart/` - Créer une commande

#### Paiements
- `POST /api/payments/create-intent/` - Créer un PaymentIntent Stripe
- `POST /api/payments/{payment_id}/confirm/` - Confirmer un paiement

## 🧪 Tests

```bash
# Lancer tous les tests
python manage.py test

# Tests avec couverture
pip install coverage
coverage run --source='.' manage.py test
coverage report
coverage html
```

## 📝 Licence

MIT License - Silence d'Or © 2024

## 🤝 Contribution

1. Fork le projet
2. Créer une branche feature (`git checkout -b feature/AmazingFeature`)
3. Commit les changements (`git commit -m 'Add some AmazingFeature'`)
4. Push vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrir une Pull Request

## 📞 Support

Pour toute question ou support, contactez-nous :
- Email : contact@silence-dor.com
- Site web : https://silence-dor.com
