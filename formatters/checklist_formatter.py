"""
Export de la checklist DD en format Excel interactif.
Génère un fichier Excel avec colonnes de suivi pour la due diligence terrain.
"""

import pandas as pd
from io import BytesIO
from typing import List, Dict
from datetime import datetime


def export_checklist_to_excel(
    checklist: List[Dict],
    company_name: str,
    sector: str,
    risk_category: str,
    country: str = "",
    analyst_name: str = ""
) -> BytesIO:
    """
    Exporte la checklist en Excel avec colonnes pour le suivi.
    
    Args:
        checklist: Liste des questions DD
        company_name: Nom de l'entreprise
        sector: Secteur
        risk_category: Catégorie de risque
        country: Pays
        analyst_name: Nom de l'analyste (optionnel)
    
    Returns:
        BytesIO contenant le fichier Excel
    """
    # Préparer les données pour la feuille principale
    rows = []
    for item in checklist:
        priority_display = {
            "high": "🔴 Haute",
            "medium": "🟠 Moyenne",
            "low": "🟢 Basse"
        }.get(item["priority"], item["priority"])
        
        rows.append({
            "N°": item.get("number", ""),
            "Catégorie": item["category"],
            "Point de contrôle": item["question"],
            "Documents requis": ", ".join(item["documents"]),
            "Standard IFC": item.get("ifc_standard", ""),
            "Priorité": priority_display,
            "Statut": "",  # À remplir : ✅ Conforme / ⚠️ Partiel / ❌ Non conforme / ❓ À vérifier
            "Documents obtenus": "",  # À remplir
            "Commentaires / Observations": "",  # À remplir
            "Actions correctives requises": "",  # À remplir
        })
    
    df_checklist = pd.DataFrame(rows)
    
    # Créer le fichier Excel
    buffer = BytesIO()
    
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        # =====================================================================
        # Feuille 1 : Checklist principale
        # =====================================================================
        df_checklist.to_excel(writer, sheet_name='Checklist DD', index=False)
        
        # Ajuster les largeurs de colonnes
        worksheet = writer.sheets['Checklist DD']
        column_widths = {
            'A': 5,   # N°
            'B': 25,  # Catégorie
            'C': 60,  # Point de contrôle
            'D': 50,  # Documents requis
            'E': 12,  # Standard IFC
            'F': 15,  # Priorité
            'G': 15,  # Statut
            'H': 30,  # Documents obtenus
            'I': 40,  # Commentaires
            'J': 40,  # Actions correctives
        }
        for col, width in column_widths.items():
            worksheet.column_dimensions[col].width = width
        
        # Figer la première ligne
        worksheet.freeze_panes = 'A2'
        
        # =====================================================================
        # Feuille 2 : Informations générales
        # =====================================================================
        meta_data = [
            {"Champ": "Entreprise", "Valeur": company_name},
            {"Champ": "Secteur", "Valeur": sector},
            {"Champ": "Pays", "Valeur": country},
            {"Champ": "Catégorie de risque", "Valeur": risk_category},
            {"Champ": "Nombre de points de contrôle", "Valeur": len(checklist)},
            {"Champ": "Points haute priorité", "Valeur": sum(1 for c in checklist if c["priority"] == "high")},
            {"Champ": "Date de génération", "Valeur": datetime.now().strftime("%d/%m/%Y %H:%M")},
            {"Champ": "Analyste", "Valeur": analyst_name},
            {"Champ": "", "Valeur": ""},
            {"Champ": "Instructions", "Valeur": "Remplir les colonnes Statut, Documents obtenus, Commentaires et Actions correctives"},
        ]
        df_meta = pd.DataFrame(meta_data)
        df_meta.to_excel(writer, sheet_name='Informations', index=False)
        
        ws_meta = writer.sheets['Informations']
        ws_meta.column_dimensions['A'].width = 30
        ws_meta.column_dimensions['B'].width = 60
        
        # =====================================================================
        # Feuille 3 : Légende des statuts
        # =====================================================================
        legend_data = [
            {"Statut": "✅ Conforme", "Description": "Le point est conforme, documents obtenus et satisfaisants"},
            {"Statut": "⚠️ Partiel", "Description": "Partiellement conforme, améliorations nécessaires mais non bloquantes"},
            {"Statut": "❌ Non conforme", "Description": "Non conforme, action corrective requise avant closing"},
            {"Statut": "❓ À vérifier", "Description": "Information manquante, à vérifier lors de la visite terrain"},
            {"Statut": "N/A", "Description": "Non applicable à cette entreprise"},
        ]
        df_legend = pd.DataFrame(legend_data)
        df_legend.to_excel(writer, sheet_name='Légende', index=False)
        
        ws_legend = writer.sheets['Légende']
        ws_legend.column_dimensions['A'].width = 20
        ws_legend.column_dimensions['B'].width = 70
        
        # =====================================================================
        # Feuille 4 : Résumé par catégorie
        # =====================================================================
        categories = {}
        for item in checklist:
            cat = item["category"]
            if cat not in categories:
                categories[cat] = {"total": 0, "high": 0, "medium": 0, "low": 0}
            categories[cat]["total"] += 1
            categories[cat][item["priority"]] += 1
        
        summary_rows = []
        for cat, counts in categories.items():
            summary_rows.append({
                "Catégorie": cat,
                "Total": counts["total"],
                "Haute priorité": counts["high"],
                "Moyenne priorité": counts["medium"],
                "Basse priorité": counts["low"],
            })
        
        df_summary = pd.DataFrame(summary_rows)
        df_summary.to_excel(writer, sheet_name='Résumé', index=False)
        
        ws_summary = writer.sheets['Résumé']
        ws_summary.column_dimensions['A'].width = 30
        for col in ['B', 'C', 'D', 'E']:
            ws_summary.column_dimensions[col].width = 18
    
    buffer.seek(0)
    return buffer


def export_checklist_to_markdown(
    checklist: List[Dict],
    company_name: str,
    sector: str,
    risk_category: str
) -> str:
    """
    Exporte la checklist en format Markdown.
    
    Returns:
        String Markdown
    """
    lines = [
        f"# Checklist Due Diligence - {company_name}",
        "",
        f"**Secteur:** {sector}",
        f"**Catégorie de risque:** {risk_category}",
        f"**Date:** {datetime.now().strftime('%d/%m/%Y')}",
        f"**Nombre de points:** {len(checklist)}",
        "",
        "---",
        "",
    ]
    
    # Grouper par catégorie
    categories = {}
    for item in checklist:
        cat = item["category"]
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(item)
    
    for category, items in categories.items():
        lines.append(f"## {category}")
        lines.append("")
        lines.append("| N° | Point de contrôle | Documents | Priorité | Statut |")
        lines.append("|:--:|-------------------|-----------|:--------:|:------:|")
        
        for item in items:
            priority_icon = {"high": "🔴", "medium": "🟠", "low": "🟢"}.get(item["priority"], "")
            docs = ", ".join(item["documents"][:2])  # Max 2 docs pour la lisibilité
            if len(item["documents"]) > 2:
                docs += ", ..."
            lines.append(f"| {item.get('number', '')} | {item['question'][:60]}{'...' if len(item['question']) > 60 else ''} | {docs} | {priority_icon} | ☐ |")
        
        lines.append("")
    
    lines.extend([
        "---",
        "",
        "### Légende des statuts",
        "- ✅ Conforme",
        "- ⚠️ Partiellement conforme",
        "- ❌ Non conforme",
        "- ❓ À vérifier",
        "- N/A Non applicable",
    ])
    
    return "\n".join(lines)
