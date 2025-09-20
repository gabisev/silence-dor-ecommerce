#!/usr/bin/env python3
"""
Script pour générer le guide utilisateur admin en PDF
"""

import os
import sys
import markdown
import pdfkit
from pathlib import Path

def convert_markdown_to_pdf():
    """Convertit le guide Markdown en PDF"""
    
    # Chemins des fichiers
    base_dir = Path(__file__).parent.parent
    markdown_file = base_dir / "GUIDE_UTILISATEUR_ADMIN.md"
    output_file = base_dir / "GUIDE_UTILISATEUR_ADMIN.pdf"
    
    print("🔄 Génération du guide utilisateur admin en PDF...")
    
    try:
        # Lire le fichier Markdown
        with open(markdown_file, 'r', encoding='utf-8') as f:
            markdown_content = f.read()
        
        print("✅ Fichier Markdown lu avec succès")
        
        # Convertir Markdown en HTML
        html_content = markdown.markdown(
            markdown_content,
            extensions=[
                'markdown.extensions.tables',
                'markdown.extensions.fenced_code',
                'markdown.extensions.toc',
                'markdown.extensions.codehilite'
            ]
        )
        
        # Ajouter le CSS pour un meilleur rendu
        html_template = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Guide Utilisateur Admin - Silence d'Or</title>
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 800px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                h1 {{
                    color: #e91e63;
                    border-bottom: 3px solid #e91e63;
                    padding-bottom: 10px;
                }}
                h2 {{
                    color: #ff9800;
                    border-bottom: 2px solid #ff9800;
                    padding-bottom: 5px;
                    margin-top: 30px;
                }}
                h3 {{
                    color: #2196f3;
                    margin-top: 25px;
                }}
                h4 {{
                    color: #4caf50;
                    margin-top: 20px;
                }}
                code {{
                    background-color: #f5f5f5;
                    padding: 2px 4px;
                    border-radius: 3px;
                    font-family: 'Courier New', monospace;
                }}
                pre {{
                    background-color: #f5f5f5;
                    padding: 15px;
                    border-radius: 5px;
                    overflow-x: auto;
                    border-left: 4px solid #e91e63;
                }}
                blockquote {{
                    border-left: 4px solid #ff9800;
                    margin: 0;
                    padding-left: 20px;
                    color: #666;
                }}
                table {{
                    border-collapse: collapse;
                    width: 100%;
                    margin: 20px 0;
                }}
                th, td {{
                    border: 1px solid #ddd;
                    padding: 12px;
                    text-align: left;
                }}
                th {{
                    background-color: #e91e63;
                    color: white;
                }}
                tr:nth-child(even) {{
                    background-color: #f9f9f9;
                }}
                ul, ol {{
                    padding-left: 30px;
                }}
                li {{
                    margin: 5px 0;
                }}
                .toc {{
                    background-color: #f8f9fa;
                    padding: 20px;
                    border-radius: 5px;
                    margin: 20px 0;
                }}
                .highlight {{
                    background-color: #fff3cd;
                    padding: 10px;
                    border-radius: 5px;
                    border-left: 4px solid #ffc107;
                    margin: 15px 0;
                }}
                .success {{
                    background-color: #d4edda;
                    padding: 10px;
                    border-radius: 5px;
                    border-left: 4px solid #28a745;
                    margin: 15px 0;
                }}
                .warning {{
                    background-color: #f8d7da;
                    padding: 10px;
                    border-radius: 5px;
                    border-left: 4px solid #dc3545;
                    margin: 15px 0;
                }}
                .info {{
                    background-color: #d1ecf1;
                    padding: 10px;
                    border-radius: 5px;
                    border-left: 4px solid #17a2b8;
                    margin: 15px 0;
                }}
                @media print {{
                    body {{
                        font-size: 12px;
                    }}
                    h1 {{
                        page-break-before: always;
                    }}
                    h1:first-child {{
                        page-break-before: avoid;
                    }}
                }}
            </style>
        </head>
        <body>
            {html_content}
        </body>
        </html>
        """
        
        print("✅ Contenu HTML généré avec succès")
        
        # Options pour PDF
        options = {
            'page-size': 'A4',
            'margin-top': '0.75in',
            'margin-right': '0.75in',
            'margin-bottom': '0.75in',
            'margin-left': '0.75in',
            'encoding': "UTF-8",
            'no-outline': None,
            'enable-local-file-access': None,
            'print-media-type': None,
            'disable-smart-shrinking': None,
        }
        
        # Générer le PDF
        pdfkit.from_string(html_template, str(output_file), options=options)
        
        print(f"✅ PDF généré avec succès : {output_file}")
        print(f"📄 Taille du fichier : {output_file.stat().st_size / 1024:.1f} KB")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la génération du PDF : {e}")
        return False

def main():
    """Fonction principale"""
    print("🚀 Génération du Guide Utilisateur Admin - Silence d'Or")
    print("=" * 60)
    
    success = convert_markdown_to_pdf()
    
    if success:
        print("\n🎉 Guide utilisateur admin généré avec succès !")
        print("📁 Fichier PDF disponible : GUIDE_UTILISATEUR_ADMIN.pdf")
        print("\n📋 Le guide contient :")
        print("   • Accès à l'administration")
        print("   • Gestion des produits")
        print("   • Gestion des commandes")
        print("   • Gestion des utilisateurs")
        print("   • Fonctionnalités avancées")
        print("   • Configuration du site")
        print("   • Sécurité et maintenance")
        print("   • Dépannage et support")
    else:
        print("\n❌ Échec de la génération du PDF")
        sys.exit(1)

if __name__ == "__main__":
    main()
