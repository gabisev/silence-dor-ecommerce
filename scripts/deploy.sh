#!/bin/bash

# Script de déploiement pour Silence d'Or E-commerce

echo "🚀 Déploiement de Silence d'Or E-commerce..."

# Vérifier que nous sommes sur la branche main
if [ "$(git branch --show-current)" != "main" ]; then
    echo "❌ Vous devez être sur la branche main pour déployer."
    exit 1
fi

# Vérifier que le répertoire de travail est propre
if [ -n "$(git status --porcelain)" ]; then
    echo "❌ Le répertoire de travail n'est pas propre. Committez vos changements d'abord."
    exit 1
fi

# Activer l'environnement virtuel
echo "🔧 Activation de l'environnement virtuel..."
source venv/bin/activate

# Installer/mettre à jour les dépendances
echo "📚 Mise à jour des dépendances..."
pip install --upgrade pip
pip install -r requirements.txt

# Migrations de base de données
echo "🗄️ Application des migrations..."
python manage.py migrate

# Collecter les fichiers statiques
echo "🎨 Collecte des fichiers statiques..."
python manage.py collectstatic --noinput

# Vérifier la configuration
echo "🔍 Vérification de la configuration..."
python manage.py check --deploy

# Redémarrer les services (si applicable)
echo "🔄 Redémarrage des services..."
# sudo systemctl restart gunicorn
# sudo systemctl restart nginx

echo "✅ Déploiement terminé!"
echo ""
echo "Vérifiez que l'application fonctionne correctement:"
echo "1. Testez l'accès à l'application"
echo "2. Vérifiez les logs d'erreur"
echo "3. Testez les fonctionnalités principales"

