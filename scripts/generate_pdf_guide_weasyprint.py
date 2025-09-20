#!/usr/bin/env python3
"""
Script pour générer le guide utilisateur admin en PDF avec WeasyPrint
"""

import os
import sys
import markdown
from pathlib import Path
from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration

def convert_markdown_to_pdf():
    """Convertit le guide Markdown en PDF avec WeasyPrint"""
    
    # Chemins des fichiers
    base_dir = Path(__file__).parent.parent
    markdown_file = base_dir / "GUIDE_UTILISATEUR_ADMIN.md"
    output_file = base_dir / "GUIDE_UTILISATEUR_ADMIN.pdf"
    
    print("🔄 Génération du guide utilisateur admin en PDF avec WeasyPrint...")
    
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
        
        # Template HTML avec CSS intégré
        html_template = f"""
        <!DOCTYPE html>
        <html lang="fr">
        <head>
            <meta charset="utf-8">
            <title>Guide Utilisateur Admin - Silence d'Or E-commerce</title>
            <style>
                @page {{
                    size: A4;
                    margin: 2cm;
                    @top-center {{
                        content: "Guide Utilisateur Admin - Silence d'Or";
                        font-size: 10pt;
                        color: #666;
                    }}
                    @bottom-center {{
                        content: "Page " counter(page);
                        font-size: 10pt;
                        color: #666;
                    }}
                }}
                
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    font-size: 11pt;
                }}
                
                h1 {{
                    color: #e91e63;
                    border-bottom: 3px solid #e91e63;
                    padding-bottom: 10px;
                    page-break-before: always;
                    font-size: 24pt;
                    margin-top: 0;
                }}
                
                h1:first-child {{
                    page-break-before: avoid;
                }}
                
                h2 {{
                    color: #ff9800;
                    border-bottom: 2px solid #ff9800;
                    padding-bottom: 5px;
                    margin-top: 30px;
                    font-size: 18pt;
                    page-break-after: avoid;
                }}
                
                h3 {{
                    color: #2196f3;
                    margin-top: 25px;
                    font-size: 14pt;
                    page-break-after: avoid;
                }}
                
                h4 {{
                    color: #4caf50;
                    margin-top: 20px;
                    font-size: 12pt;
                    page-break-after: avoid;
                }}
                
                p {{
                    text-align: justify;
                    margin: 10px 0;
                }}
                
                code {{
                    background-color: #f5f5f5;
                    padding: 2px 4px;
                    border-radius: 3px;
                    font-family: 'Courier New', monospace;
                    font-size: 10pt;
                }}
                
                pre {{
                    background-color: #f5f5f5;
                    padding: 15px;
                    border-radius: 5px;
                    overflow-x: auto;
                    border-left: 4px solid #e91e63;
                    font-family: 'Courier New', monospace;
                    font-size: 9pt;
                    page-break-inside: avoid;
                }}
                
                blockquote {{
                    border-left: 4px solid #ff9800;
                    margin: 15px 0;
                    padding-left: 20px;
                    color: #666;
                    font-style: italic;
                }}
                
                table {{
                    border-collapse: collapse;
                    width: 100%;
                    margin: 20px 0;
                    page-break-inside: avoid;
                }}
                
                th, td {{
                    border: 1px solid #ddd;
                    padding: 8px;
                    text-align: left;
                    font-size: 10pt;
                }}
                
                th {{
                    background-color: #e91e63;
                    color: white;
                    font-weight: bold;
                }}
                
                tr:nth-child(even) {{
                    background-color: #f9f9f9;
                }}
                
                ul, ol {{
                    padding-left: 30px;
                    margin: 10px 0;
                }}
                
                li {{
                    margin: 5px 0;
                }}
                
                .toc {{
                    background-color: #f8f9fa;
                    padding: 20px;
                    border-radius: 5px;
                    margin: 20px 0;
                    page-break-inside: avoid;
                }}
                
                .highlight {{
                    background-color: #fff3cd;
                    padding: 10px;
                    border-radius: 5px;
                    border-left: 4px solid #ffc107;
                    margin: 15px 0;
                    page-break-inside: avoid;
                }}
                
                .success {{
                    background-color: #d4edda;
                    padding: 10px;
                    border-radius: 5px;
                    border-left: 4px solid #28a745;
                    margin: 15px 0;
                    page-break-inside: avoid;
                }}
                
                .warning {{
                    background-color: #f8d7da;
                    padding: 10px;
                    border-radius: 5px;
                    border-left: 4px solid #dc3545;
                    margin: 15px 0;
                    page-break-inside: avoid;
                }}
                
                .info {{
                    background-color: #d1ecf1;
                    padding: 10px;
                    border-radius: 5px;
                    border-left: 4px solid #17a2b8;
                    margin: 15px 0;
                    page-break-inside: avoid;
                }}
                
                hr {{
                    border: none;
                    border-top: 2px solid #e91e63;
                    margin: 30px 0;
                }}
                
                strong {{
                    color: #e91e63;
                }}
                
                em {{
                    color: #ff9800;
                }}
                
                a {{
                    color: #2196f3;
                    text-decoration: none;
                }}
                
                a:hover {{
                    text-decoration: underline;
                }}
                
                .page-break {{
                    page-break-before: always;
                }}
                
                .no-break {{
                    page-break-inside: avoid;
                }}
            </style>
        </head>
        <body>
            {html_content}
        </body>
        </html>
        """
        
        print("✅ Contenu HTML généré avec succès")
        
        # Configuration des polices
        font_config = FontConfiguration()
        
        # Générer le PDF avec WeasyPrint
        html_doc = HTML(string=html_template)
        html_doc.write_pdf(
            str(output_file),
            font_config=font_config
        )
        
        print(f"✅ PDF généré avec succès : {output_file}")
        print(f"📄 Taille du fichier : {output_file.stat().st_size / 1024:.1f} KB")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la génération du PDF : {e}")
        import traceback
        traceback.print_exc()
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
        print("\n📖 Le guide est maintenant prêt à être utilisé !")
    else:
        print("\n❌ Échec de la génération du PDF")
        sys.exit(1)

if __name__ == "__main__":
    main()
