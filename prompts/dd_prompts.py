"""
Prompts pour l'analyse IA au stade Due Diligence.
Aide à pré-remplir la checklist et analyser les documents.
"""

DD_SYSTEM_PROMPT = """Tu es un analyste ESG senior spécialisé dans la Due Diligence E&S pour les investissements à impact en Afrique.
Tu travailles pour IPAE3 et tu effectues des analyses terrain approfondies.

Tu connais parfaitement:
- Les Performance Standards de l'IFC (PS1-PS8)
- Les critères 2X Challenge
- Les réglementations E&S des pays africains
- Les bonnes pratiques HSE sectorielles

Ton rôle est d'aider l'analyste à:
1. Identifier les risques E&S prioritaires
2. Suggérer des questions pour la checklist
3. Proposer des actions correctives (ESAP)
4. Rédiger des synthèses de DD"""


def format_dd_analysis_prompt(
    company_name: str,
    country: str,
    country_context: str,
    sector: str,
    subsector: str,
    description: str,
    risk_category: str,
    employees: int,
    two_x_data: dict,
    checklist_status: dict = None
) -> str:
    """Formate le prompt pour l'analyse DD."""
    
    checklist_summary = ""
    if checklist_status:
        conformes = sum(1 for v in checklist_status.values() if v == 'conforme')
        partiels = sum(1 for v in checklist_status.values() if v == 'partiel')
        non_conformes = sum(1 for v in checklist_status.values() if v == 'non_conforme')
        total = len(checklist_status)
        checklist_summary = f"""
## ÉTAT DE LA CHECKLIST DD
- Points conformes: {conformes}/{total}
- Points partiels: {partiels}/{total}
- Points non conformes: {non_conformes}/{total}
"""
    
    return f"""# ANALYSE DUE DILIGENCE - {company_name}

## INFORMATIONS ENTREPRISE
- **Entreprise:** {company_name}
- **Pays:** {country}
- **Secteur:** {sector} / {subsector}
- **Description:** {description}
- **Employés:** {employees}
- **Catégorie de risque:** {risk_category}

## CONTEXTE PAYS
{country_context}

## DONNÉES GENRE (2X)
- Détention féminine: {two_x_data.get('women_ownership_pct', 0)}%
- Management féminin: {two_x_data.get('women_management_pct', 0)}%
- Employées femmes: {two_x_data.get('women_employees_pct', 0)}%
{checklist_summary}

---

## TÂCHE

Effectue une analyse DD approfondie et fournis:

### 1. RISQUES E&S PRIORITAIRES
Identifie les 5 risques E&S majeurs pour ce type d'entreprise dans ce contexte.
Pour chaque risque:
- Description du risque
- Performance Standard IFC concerné
- Niveau de risque (Élevé/Moyen/Faible)
- Mesures d'atténuation recommandées

### 2. POINTS DE VIGILANCE TERRAIN
Liste les 5-7 points clés à vérifier lors de la visite terrain:
- Quoi observer
- Questions à poser
- Documents à demander

### 3. GAPS 2X CHALLENGE
Analyse les lacunes sur les critères genre et propose des actions concrètes pour atteindre l'éligibilité 2X.

### 4. PROPOSITION ESAP PRÉLIMINAIRE
Propose 3-5 actions prioritaires pour le Plan d'Action E&S (ESAP):
| Action | Responsable | Délai | Priorité |
|--------|-------------|-------|----------|

### 5. CONDITIONS PRÉALABLES SUGGÉRÉES
Liste les conditions qui devraient être levées avant l'investissement.

### 6. SYNTHÈSE DD
Résumé en 5-6 lignes de l'état de préparation E&S de l'entreprise.

---

Sois spécifique et actionnable dans tes recommandations."""


def format_dd_checklist_assist_prompt(
    company_name: str,
    sector: str,
    country: str,
    risk_category: str,
    checklist_items: list
) -> str:
    """Prompt pour aider à pré-remplir la checklist."""
    
    items_text = "\n".join([f"- {item['question']}" for item in checklist_items[:15]])
    
    return f"""# ASSISTANCE CHECKLIST DD - {company_name}

**Secteur:** {sector}
**Pays:** {country}
**Catégorie risque:** {risk_category}

## QUESTIONS DE LA CHECKLIST
{items_text}

---

## TÂCHE

Pour une entreprise type dans ce secteur et ce pays, indique pour chaque question:

1. **Niveau de risque probable** (Élevé/Moyen/Faible)
2. **Points d'attention spécifiques** au contexte
3. **Documents à demander** pour vérification
4. **Bonnes pratiques** attendues dans ce secteur

Sois concis et pratique pour aider l'analyste terrain."""


def format_dd_synthesis_prompt(
    company_name: str,
    country: str,
    sector: str,
    risk_category: str,
    checklist_status: dict,
    conditions: list,
    comments: list
) -> str:
    """Prompt pour générer la synthèse DD."""
    
    # Analyser la checklist
    conformes = sum(1 for v in checklist_status.values() if v == 'conforme')
    partiels = sum(1 for v in checklist_status.values() if v == 'partiel')
    non_conformes = sum(1 for v in checklist_status.values() if v == 'non_conforme')
    total = len(checklist_status)
    
    conditions_text = "\n".join([f"- {c}" for c in conditions]) if conditions else "Aucune"
    comments_text = "\n".join([f"- {c.get('text', '')}" for c in comments[-5:]]) if comments else "Aucun"
    
    return f"""# SYNTHÈSE DUE DILIGENCE - {company_name}

## RÉSULTATS CHECKLIST
- **Conformes:** {conformes}/{total} ({conformes/total*100:.0f}%)
- **Partiels:** {partiels}/{total}
- **Non conformes:** {non_conformes}/{total}

## CONDITIONS IDENTIFIÉES
{conditions_text}

## OBSERVATIONS TERRAIN
{comments_text}

---

## TÂCHE

Rédige une synthèse DD professionnelle de 200-300 mots incluant:

1. **Conclusion générale** sur l'état de préparation E&S
2. **Points forts** de l'entreprise (2-3)
3. **Faiblesses principales** (2-3)
4. **Recommandation** (GO / GO avec conditions / NO-GO)
5. **Prochaines étapes** si GO

Cette synthèse sera incluse dans le mémo pour le Comité d'Investissement."""
