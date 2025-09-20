#!/usr/bin/env python
"""
Script de démarrage simple pour Silence d'Or E-commerce
"""

import os
import sys
import subprocess

def main():
    """Démarrage du serveur Django"""
    print("🚀 Démarrage de Silence d'Or E-commerce")
    print("=" * 50)
    
    # Vérifier que Django est installé
    try:
        import django
        print(f"✅ Django {django.get_version()} détecté")
    except ImportError:
        print("❌ Django n'est pas installé")
        print("Installez Django avec: pip install Django")
        return
    
    # Vérifier la configuration
    try:
        result = subprocess.run([
            sys.executable, 'manage.py', 'check', 
            '--settings=silence_dor.settings_simple'
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Configuration Django valide")
        else:
            print("❌ Erreur de configuration:")
            print(result.stderr)
            return
    except Exception as e:
        print(f"❌ Erreur lors de la vérification: {e}")
        return
    
    # Démarrer le serveur
    print("\n🌐 Démarrage du serveur de développement...")
    print("📱 Accès:")
    print("   - Site web: http://localhost:8000")
    print("   - Admin: http://localhost:8000/admin")
    print("   - API: http://localhost:8000/api")
    print("\n⏹️  Appuyez sur Ctrl+C pour arrêter le serveur")
    print("=" * 50)
    
    try:
        subprocess.run([
            sys.executable, 'manage.py', 'runserver', 
            '--settings=silence_dor.settings_simple'
        ])
    except KeyboardInterrupt:
        print("\n\n👋 Serveur arrêté. Au revoir!")
    except Exception as e:
        print(f"\n❌ Erreur lors du démarrage: {e}")

if __name__ == '__main__':
    main()

