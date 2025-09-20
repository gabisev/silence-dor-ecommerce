#!/usr/bin/env python3
"""
Script pour générer le guide utilisateur admin en PDF avec ReportLab
"""

import os
import sys
import re
from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor, black, white
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.pdfgen import canvas
from reportlab.lib import colors

def clean_markdown_text(text):
    """Nettoie le texte Markdown pour ReportLab"""
    # Supprimer les liens markdown
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
    # Supprimer les emojis
    text = re.sub(r'[^\w\s\-.,!?;:()\[\]{}"\']', '', text)
    # Nettoyer les espaces multiples
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def create_pdf_guide():
    """Crée le guide PDF avec ReportLab"""
    
    # Chemins des fichiers
    base_dir = Path(__file__).parent.parent
    markdown_file = base_dir / "GUIDE_UTILISATEUR_ADMIN.md"
    output_file = base_dir / "GUIDE_UTILISATEUR_ADMIN.pdf"
    
    print("🔄 Génération du guide utilisateur admin en PDF avec ReportLab...")
    
    try:
        # Lire le fichier Markdown
        with open(markdown_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print("✅ Fichier Markdown lu avec succès")
        
        # Créer le document PDF
        doc = SimpleDocTemplate(
            str(output_file),
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18
        )
        
        # Styles
        styles = getSampleStyleSheet()
        
        # Style personnalisé pour le titre principal
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            textColor=HexColor('#e91e63'),
            alignment=TA_CENTER
        )
        
        # Style pour les titres de section
        section_style = ParagraphStyle(
            'CustomSection',
            parent=styles['Heading2'],
            fontSize=16,
            spaceAfter=20,
            spaceBefore=20,
            textColor=HexColor('#ff9800'),
            borderWidth=1,
            borderColor=HexColor('#ff9800'),
            borderPadding=10
        )
        
        # Style pour les sous-titres
        subsection_style = ParagraphStyle(
            'CustomSubsection',
            parent=styles['Heading3'],
            fontSize=14,
            spaceAfter=15,
            spaceBefore=15,
            textColor=HexColor('#2196f3')
        )
        
        # Style pour le texte normal
        normal_style = ParagraphStyle(
            'CustomNormal',
            parent=styles['Normal'],
            fontSize=11,
            spaceAfter=12,
            alignment=TA_JUSTIFY
        )
        
        # Style pour les listes
        list_style = ParagraphStyle(
            'CustomList',
            parent=styles['Normal'],
            fontSize=11,
            spaceAfter=8,
            leftIndent=20
        )
        
        # Style pour le code
        code_style = ParagraphStyle(
            'CustomCode',
            parent=styles['Code'],
            fontSize=9,
            spaceAfter=10,
            spaceBefore=10,
            leftIndent=20,
            rightIndent=20,
            backColor=HexColor('#f5f5f5'),
            borderWidth=1,
            borderColor=HexColor('#e91e63'),
            borderPadding=10
        )
        
        # Construire le contenu
        story = []
        
        # Titre principal
        story.append(Paragraph("Guide Utilisateur Admin", title_style))
        story.append(Paragraph("Silence d'Or E-commerce", title_style))
        story.append(Spacer(1, 20))
        story.append(Paragraph("Version 1.0 - Septembre 2025", normal_style))
        story.append(PageBreak())
        
        # Table des matières
        story.append(Paragraph("Table des Matières", section_style))
        toc_items = [
            "1. Introduction",
            "2. Accès à l'Administration", 
            "3. Gestion des Produits",
            "4. Gestion des Commandes",
            "5. Gestion des Utilisateurs",
            "6. Fonctionnalités Avancées",
            "7. Configuration du Site",
            "8. Sécurité et Maintenance",
            "9. Dépannage",
            "10. Support"
        ]
        
        for item in toc_items:
            story.append(Paragraph(f"• {item}", list_style))
        
        story.append(PageBreak())
        
        # Traiter le contenu markdown
        lines = content.split('\n')
        current_section = ""
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Titre principal
            if line.startswith('# '):
                story.append(PageBreak())
                title = clean_markdown_text(line[2:])
                story.append(Paragraph(title, title_style))
                
            # Titre de section
            elif line.startswith('## '):
                story.append(Spacer(1, 20))
                title = clean_markdown_text(line[3:])
                story.append(Paragraph(title, section_style))
                
            # Sous-titre
            elif line.startswith('### '):
                story.append(Spacer(1, 15))
                title = clean_markdown_text(line[4:])
                story.append(Paragraph(title, subsection_style))
                
            # Code
            elif line.startswith('```'):
                continue  # Ignorer les blocs de code pour simplifier
                
            # Liste
            elif line.startswith('- ') or line.startswith('* '):
                item = clean_markdown_text(line[2:])
                story.append(Paragraph(f"• {item}", list_style))
                
            # Texte normal
            else:
                if line and not line.startswith('#'):
                    clean_line = clean_markdown_text(line)
                    if clean_line:
                        story.append(Paragraph(clean_line, normal_style))
        
        # Construire le PDF
        doc.build(story)
        
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
    
    success = create_pdf_guide()
    
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
        print("\n💡 Vous pouvez maintenant :")
        print("   • Ouvrir le fichier PDF")
        print("   • L'imprimer pour votre équipe")
        print("   • Le partager avec vos collaborateurs")
    else:
        print("\n❌ Échec de la génération du PDF")
        sys.exit(1)

if __name__ == "__main__":
    main()
