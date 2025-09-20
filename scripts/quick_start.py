#!/usr/bin/env python
"""
Script de démarrage rapide pour Silence d'Or E-commerce
Gère les erreurs courantes et configure automatiquement le projet
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

def create_virtual_environment():
    """Créer un environnement virtuel"""
    if os.path.exists('venv'):
        print("✅ Environnement virtuel existant trouvé")
        return True
    
    return run_command('python -m venv venv', 'Création de l\'environnement virtuel')

def activate_virtual_environment():
    """Activer l'environnement virtuel"""
    if os.name == 'nt':  # Windows
        activate_script = 'venv\\Scripts\\activate'
    else:  # Unix/Linux/Mac
        activate_script = 'source venv/bin/activate'
    
    print(f"🔧 Activation de l'environnement virtuel: {activate_script}")
    return True

def install_requirements():
    """Installer les dépendances"""
    if os.name == 'nt':  # Windows
        pip_command = 'venv\\Scripts\\pip'
    else:  # Unix/Linux/Mac
        pip_command = 'venv/bin/pip'
    
    commands = [
        (f'{pip_command} install --upgrade pip', 'Mise à jour de pip'),
        (f'{pip_command} install -r requirements.txt', 'Installation des dépendances')
    ]
    
    for command, description in commands:
        if not run_command(command, description):
            return False
    return True

def setup_environment():
    """Configurer l'environnement"""
    if not os.path.exists('.env'):
        if os.path.exists('env.example'):
            shutil.copy('env.example', '.env')
            print("✅ Fichier .env créé depuis env.example")
        else:
            print("❌ Fichier env.example non trouvé")
            return False
    else:
        print("✅ Fichier .env existant trouvé")
    return True

def create_directories():
    """Créer les dossiers nécessaires"""
    directories = ['media', 'staticfiles', 'logs']
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✅ Dossier {directory} créé/vérifié")
    return True

def run_migrations():
    """Exécuter les migrations"""
    if os.name == 'nt':  # Windows
        python_command = 'venv\\Scripts\\python'
    else:  # Unix/Linux/Mac
        python_command = 'venv/bin/python'
    
    commands = [
        (f'{python_command} manage.py makemigrations', 'Création des migrations'),
        (f'{python_command} manage.py migrate', 'Application des migrations')
    ]
    
    for command, description in commands:
        if not run_command(command, description):
            return False
    return True

def collect_static():
    """Collecter les fichiers statiques"""
    if os.name == 'nt':  # Windows
        python_command = 'venv\\Scripts\\python'
    else:  # Unix/Linux/Mac
        python_command = 'venv/bin/python'
    
    return run_command(
        f'{python_command} manage.py collectstatic --noinput',
        'Collecte des fichiers statiques'
    )

def create_superuser():
    """Créer un superutilisateur"""
    print("👤 Création du superutilisateur...")
    print("Veuillez entrer les informations du superutilisateur:")
    
    if os.name == 'nt':  # Windows
        python_command = 'venv\\Scripts\\python'
    else:  # Unix/Linux/Mac
        python_command = 'venv/bin/python'
    
    return run_command(
        f'{python_command} manage.py createsuperuser',
        'Création du superutilisateur'
    )

def main():
    """Fonction principale"""
    print("🚀 Démarrage rapide de Silence d'Or E-commerce\n")
    
    # Vérifications préliminaires
    if not check_python_version():
        sys.exit(1)
    
    # Configuration de l'environnement
    steps = [
        (create_virtual_environment, "Création de l'environnement virtuel"),
        (activate_virtual_environment, "Activation de l'environnement virtuel"),
        (install_requirements, "Installation des dépendances"),
        (setup_environment, "Configuration de l'environnement"),
        (create_directories, "Création des dossiers"),
        (run_migrations, "Exécution des migrations"),
        (collect_static, "Collecte des fichiers statiques"),
    ]
    
    for step_func, step_name in steps:
        if not step_func():
            print(f"\n❌ Échec à l'étape: {step_name}")
            print("Consultez docs/TROUBLESHOOTING.md pour plus d'aide")
            sys.exit(1)
    
    # Création du superutilisateur (optionnel)
    create_superuser_choice = input("\n👤 Voulez-vous créer un superutilisateur maintenant? (y/n): ")
    if create_superuser_choice.lower() in ['y', 'yes', 'oui']:
        create_superuser()
    
    print("\n🎉 Configuration terminée avec succès!")
    print("\n📋 Prochaines étapes:")
    print("1. Éditez le fichier .env avec vos paramètres")
    print("2. Démarrez le serveur de développement:")
    
    if os.name == 'nt':  # Windows
        print("   venv\\Scripts\\python manage.py runserver")
    else:  # Unix/Linux/Mac
        print("   source venv/bin/activate")
        print("   python manage.py runserver")
    
    print("\n3. Accédez à l'application:")
    print("   - Site web: http://localhost:8000")
    print("   - Admin: http://localhost:8000/admin")
    print("   - API: http://localhost:8000/api")

if __name__ == '__main__':
    main()

