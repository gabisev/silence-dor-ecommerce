#!/usr/bin/env python3
"""
Script pour mettre à jour le guide utilisateur admin
"""

import os
import sys
from pathlib import Path

def update_guide():
    """Met à jour le guide utilisateur admin"""
    
    print("🔄 Mise à jour du guide utilisateur admin...")
    
    try:
        # Exécuter le script de génération PDF
        script_path = Path(__file__).parent / "generate_pdf_guide_reportlab.py"
        
        import subprocess
        result = subprocess.run([
            sys.executable, 
            str(script_path)
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Guide mis à jour avec succès !")
            print("📁 Fichier PDF : GUIDE_UTILISATEUR_ADMIN.pdf")
            return True
        else:
            print(f"❌ Erreur lors de la mise à jour : {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur : {e}")
        return False

def main():
    """Fonction principale"""
    print("🚀 Mise à jour du Guide Utilisateur Admin")
    print("=" * 50)
    
    success = update_guide()
    
    if success:
        print("\n🎉 Guide utilisateur admin mis à jour !")
        print("📖 Le fichier PDF est prêt à être utilisé.")
    else:
        print("\n❌ Échec de la mise à jour")
        sys.exit(1)

if __name__ == "__main__":
    main()
