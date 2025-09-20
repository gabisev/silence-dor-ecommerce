#!/bin/bash

# Script de configuration pour Silence d'Or E-commerce

echo "🚀 Configuration de Silence d'Or E-commerce..."

# Vérifier Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 n'est pas installé. Veuillez l'installer d'abord."
    exit 1
fi

# Créer un environnement virtuel
echo "📦 Création de l'environnement virtuel..."
python3 -m venv venv

# Activer l'environnement virtuel
echo "🔧 Activation de l'environnement virtuel..."
source venv/bin/activate

# Installer les dépendances
echo "📚 Installation des dépendances..."
pip install --upgrade pip
pip install -r requirements.txt

# Copier le fichier d'environnement
echo "⚙️ Configuration de l'environnement..."
if [ ! -f .env ]; then
    cp env.example .env
    echo "📝 Fichier .env créé. Veuillez le configurer avec vos paramètres."
fi

# Créer les dossiers nécessaires
echo "📁 Création des dossiers..."
mkdir -p media
mkdir -p staticfiles
mkdir -p logs

# Migrations de base de données
echo "🗄️ Configuration de la base de données..."
python manage.py makemigrations
python manage.py migrate

# Créer un superutilisateur
echo "👤 Création du superutilisateur..."
python manage.py createsuperuser

# Collecter les fichiers statiques
echo "🎨 Collecte des fichiers statiques..."
python manage.py collectstatic --noinput

echo "✅ Configuration terminée!"
echo ""
echo "Pour démarrer le serveur de développement:"
echo "1. Activez l'environnement virtuel: source venv/bin/activate"
echo "2. Démarrez le serveur: python manage.py runserver"
echo ""
echo "Pour accéder à l'interface d'administration:"
echo "http://localhost:8000/admin/"

