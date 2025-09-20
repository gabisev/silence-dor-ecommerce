#!/usr/bin/env python3
"""
Script de déploiement pour Render
"""

import os
import sys
import subprocess
from pathlib import Path

def run_command(command, description):
    """Exécute une commande et affiche le résultat"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} - Succès")
        if result.stdout:
            print(f"📄 Sortie: {result.stdout}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - Échec")
        print(f"📄 Erreur: {e.stderr}")
        return False

def check_requirements():
    """Vérifie que tous les fichiers requis sont présents"""
    print("🔍 Vérification des fichiers requis...")
    
    required_files = [
        'requirements.txt',
        'render.yaml',
        'silence_dor/settings_production.py',
        'env.example'
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print(f"❌ Fichiers manquants: {', '.join(missing_files)}")
        return False
    
    print("✅ Tous les fichiers requis sont présents")
    return True

def prepare_deployment():
    """Prépare le déploiement"""
    print("🚀 Préparation du déploiement...")
    
    # Créer le dossier logs s'il n'existe pas
    logs_dir = Path('logs')
    logs_dir.mkdir(exist_ok=True)
    
    # Créer le fichier .gitignore s'il n'existe pas
    gitignore_content = """
# Django
*.log
*.pot
*.pyc
__pycache__/
local_settings.py
db.sqlite3
db.sqlite3-journal
media/
staticfiles/

# Environment variables
.env
.env.local
.env.production

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Logs
logs/
*.log

# Coverage
htmlcov/
.coverage
.coverage.*
coverage.xml

# Pytest
.pytest_cache/

# Celery
celerybeat-schedule
celerybeat.pid

# Node
node_modules/
npm-debug.log*

# Backup
*.bak
*.backup
"""
    
    gitignore_file = Path('.gitignore')
    if not gitignore_file.exists():
        gitignore_file.write_text(gitignore_content.strip())
        print("✅ Fichier .gitignore créé")
    
    return True

def run_tests():
    """Exécute les tests avant le déploiement"""
    print("🧪 Exécution des tests...")
    
    # Vérifier que Django peut démarrer
    if not run_command(
        "python manage.py check --settings=silence_dor.settings_production",
        "Vérification de la configuration Django"
    ):
        return False
    
    # Collecter les fichiers statiques
    if not run_command(
        "python manage.py collectstatic --noinput --settings=silence_dor.settings_production",
        "Collecte des fichiers statiques"
    ):
        return False
    
    print("✅ Tests réussis")
    return True

def create_health_check():
    """Crée l'endpoint de health check"""
    health_check_content = '''
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.db import connection
from django.core.cache import cache
import redis

@csrf_exempt
@require_http_methods(["GET"])
def health_check(request):
    """Endpoint de health check pour Render"""
    try:
        # Vérifier la base de données
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        
        # Vérifier le cache Redis
        cache.set('health_check', 'ok', 10)
        cache_result = cache.get('health_check')
        
        return JsonResponse({
            'status': 'healthy',
            'database': 'ok',
            'cache': 'ok' if cache_result == 'ok' else 'error',
            'timestamp': timezone.now().isoformat()
        })
    except Exception as e:
        return JsonResponse({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': timezone.now().isoformat()
        }, status=500)
'''
    
    health_file = Path('apps/core/health.py')
    health_file.write_text(health_check_content.strip())
    
    # Ajouter l'URL de health check
    urls_content = '''
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import health

urlpatterns = [
    path('admin/', admin.site.urls),
    path('health/', health.health_check, name='health_check'),
    path('', include('apps.core.urls')),
    path('products/', include('apps.products.urls')),
    path('accounts/', include('apps.accounts.urls')),
    path('orders/', include('apps.orders.urls')),
    path('cart/', include('apps.cart.urls')),
    
    # Nouvelles fonctionnalités avancées
    path('analytics/', include('apps.analytics.urls')),
    path('search/', include('apps.search.urls')),
    path('notifications/', include('apps.notifications.urls')),
    path('recommendations/', include('apps.recommendations.urls')),
    path('security/', include('apps.security.urls')),
    path('inventory/', include('apps.inventory.urls')),
    path('marketing/', include('apps.marketing.urls')),
    path('pwa/', include('apps.pwa.urls')),
    path('automation/', include('apps.automation.urls')),
    path('i18n/', include('apps.i18n.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
'''
    
    urls_file = Path('silence_dor/urls.py')
    urls_file.write_text(urls_content.strip())
    
    print("✅ Health check configuré")
    return True

def main():
    """Fonction principale"""
    print("🚀 Préparation du déploiement sur Render")
    print("=" * 50)
    
    # Vérifier les fichiers requis
    if not check_requirements():
        print("❌ Préparation échouée - fichiers manquants")
        sys.exit(1)
    
    # Préparer le déploiement
    if not prepare_deployment():
        print("❌ Préparation échouée")
        sys.exit(1)
    
    # Créer le health check
    if not create_health_check():
        print("❌ Configuration du health check échouée")
        sys.exit(1)
    
    # Exécuter les tests
    if not run_tests():
        print("❌ Tests échoués")
        sys.exit(1)
    
    print("\n🎉 Préparation du déploiement terminée avec succès !")
    print("\n📋 Prochaines étapes :")
    print("1. 📤 Pousser le code sur GitHub")
    print("2. 🔗 Connecter le repository à Render")
    print("3. ⚙️ Configurer les variables d'environnement")
    print("4. 🚀 Déployer l'application")
    print("\n📖 Consultez le guide de déploiement pour plus de détails")

if __name__ == "__main__":
    main()
