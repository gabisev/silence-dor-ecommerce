#!/usr/bin/env python
"""
Script de démarrage simple pour Silence d'Or E-commerce
Utilise une configuration minimale pour éviter les erreurs
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def run_command(command, description):
    """Exécuter une commande et gérer les erreurs"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} - Succès")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - Erreur: {e.stderr}")
        return False

def check_python_version():
    """Vérifier la version de Python"""
    print("🔍 Vérification de la version Python...")
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ requis. Version actuelle:", sys.version)
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} détecté")
    return True

def install_django():
    """Installer Django"""
    return run_command('pip install Django', 'Installation de Django')

def create_directories():
    """Créer les dossiers nécessaires"""
    directories = ['media', 'staticfiles', 'logs']
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✅ Dossier {directory} créé/vérifié")
    return True

def run_migrations_simple():
    """Exécuter les migrations avec la configuration simple"""
    commands = [
        ('python manage.py makemigrations --settings=silence_dor.settings_simple', 'Création des migrations'),
        ('python manage.py migrate --settings=silence_dor.settings_simple', 'Application des migrations')
    ]
    
    for command, description in commands:
        if not run_command(command, description):
            return False
    return True

def collect_static_simple():
    """Collecter les fichiers statiques avec la configuration simple"""
    return run_command(
        'python manage.py collectstatic --noinput --settings=silence_dor.settings_simple',
        'Collecte des fichiers statiques'
    )

def create_superuser_simple():
    """Créer un superutilisateur avec la configuration simple"""
    print("👤 Création du superutilisateur...")
    print("Veuillez entrer les informations du superutilisateur:")
    
    return run_command(
        'python manage.py createsuperuser --settings=silence_dor.settings_simple',
        'Création du superutilisateur'
    )

def main():
    """Fonction principale"""
    print("🚀 Démarrage simple de Silence d'Or E-commerce\n")
    
    # Vérifications préliminaires
    if not check_python_version():
        sys.exit(1)
    
    # Configuration de l'environnement
    steps = [
        (install_django, "Installation de Django"),
        (create_directories, "Création des dossiers"),
        (run_migrations_simple, "Exécution des migrations"),
        (collect_static_simple, "Collecte des fichiers statiques"),
    ]
    
    for step_func, step_name in steps:
        if not step_func():
            print(f"\n❌ Échec à l'étape: {step_name}")
            sys.exit(1)
    
    # Création du superutilisateur (optionnel)
    create_superuser_choice = input("\n👤 Voulez-vous créer un superutilisateur maintenant? (y/n): ")
    if create_superuser_choice.lower() in ['y', 'yes', 'oui']:
        create_superuser_simple()
    
    print("\n🎉 Configuration terminée avec succès!")
    print("\n📋 Prochaines étapes:")
    print("1. Démarrez le serveur de développement:")
    print("   python manage.py runserver --settings=silence_dor.settings_simple")
    print("\n2. Accédez à l'application:")
    print("   - Site web: http://localhost:8000")
    print("   - Admin: http://localhost:8000/admin")
    print("\n3. Pour utiliser la configuration complète plus tard:")
    print("   - Installez les dépendances: pip install -r requirements.txt")
    print("   - Utilisez: python manage.py runserver")

if __name__ == '__main__':
    main()

