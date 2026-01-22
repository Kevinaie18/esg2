"""
Prompts pour l'analyse IA au stade Monitoring.
Génère des rapports de suivi et analyse l'évolution des KPIs.
"""

MONITORING_SYSTEM_PROMPT = """Tu es un analyste ESG senior spécialisé dans le suivi post-investissement pour un fonds à impact.
Tu travailles pour IPAE3 et tu surveilles le portfolio d'entreprises investies en Afrique.

Ton rôle est de:
1. Analyser l'évolution des KPIs ESG et impact
2. Suivre l'avancement des plans d'action (ESAP)
3. Identifier les risques émergents
4. Proposer des actions correctives
5. Rédiger des rapports de suivi pour les investisseurs

Tu es pragmatique et orienté solutions."""


def format_monitoring_report_prompt(
    company_name: str,
    country: str,
    sector: str,
    investment_date: str,
    current_kpis: dict,
    kpi_history: list,
    esap_summary: dict,
    esap_items: list
) -> str:
    """Formate le prompt pour le rapport de monitoring."""
    
    # Construire l'historique KPIs
    kpi_evolution = ""
    if kpi_history and len(kpi_history) > 1:
        first = kpi_history[0]['data']
        last = kpi_history[-1]['data']
        
        kpi_evolution = f"""
### Évolution des KPIs
| Indicateur | Début | Actuel | Évolution |
|------------|-------|--------|-----------|
| % Femmes ownership | {first.get('women_ownership_pct', 'N/A')}% | {last.get('women_ownership_pct', 'N/A')}% | {last.get('women_ownership_pct', 0) - first.get('women_ownership_pct', 0):+.0f}% |
| % Femmes management | {first.get('women_management_pct', 'N/A')}% | {last.get('women_management_pct', 'N/A')}% | {last.get('women_management_pct', 0) - first.get('women_management_pct', 0):+.0f}% |
| % Femmes employées | {first.get('women_employees_pct', 'N/A')}% | {last.get('women_employees_pct', 'N/A')}% | {last.get('women_employees_pct', 0) - first.get('women_employees_pct', 0):+.0f}% |
| Total employés | {first.get('total_employees', 'N/A')} | {last.get('total_employees', 'N/A')} | {last.get('total_employees', 0) - first.get('total_employees', 0):+.0f} |
"""
    
    # Construire le statut ESAP
    esap_details = ""
    if esap_items:
        esap_details = "\n### Détail des actions ESAP\n"
        for item in esap_items:
            status_icon = {"completed": "✅", "in_progress": "🔄", "not_started": "⏳"}.get(item.status, "❓")
            priority_icon = {"high": "🔴", "medium": "🟠", "low": "🟢"}.get(item.priority, "")
            deadline_str = item.deadline.strftime('%d/%m/%Y') if item.deadline else "Non défini"
            esap_details += f"- {status_icon} {priority_icon} **{item.action}** (Échéance: {deadline_str}) - {item.responsible}\n"
    
    return f"""# RAPPORT DE MONITORING - {company_name}

## INFORMATIONS GÉNÉRALES
- **Entreprise:** {company_name}
- **Pays:** {country}
- **Secteur:** {sector}
- **Date d'investissement:** {investment_date}

## KPIs ACTUELS
- Détention féminine: {current_kpis.get('women_ownership_pct', 'N/A')}%
- Management féminin: {current_kpis.get('women_management_pct', 'N/A')}%
- Employées femmes: {current_kpis.get('women_employees_pct', 'N/A')}%
- Total employés: {current_kpis.get('total_employees', 'N/A')}
- Éligibilité 2X: {"✅ Oui" if current_kpis.get('two_x_eligible') else "❌ Non"}
{kpi_evolution}

## AVANCEMENT ESAP
- **Total actions:** {esap_summary.get('total', 0)}
- **Complétées:** {esap_summary.get('completed', 0)} ({esap_summary.get('completion_rate', 0):.0f}%)
- **En cours:** {esap_summary.get('in_progress', 0)}
- **En retard:** {esap_summary.get('overdue', 0)}
{esap_details}

---

## TÂCHE

Génère un rapport de monitoring trimestriel incluant:

### 1. SYNTHÈSE EXÉCUTIVE (5-6 lignes)
Résumé de la situation E&S et impact de l'entreprise.

### 2. ANALYSE DES KPIs
- Évolution positive/négative
- Écarts par rapport aux objectifs
- Facteurs explicatifs

### 3. AVANCEMENT ESAP
- Actions complétées et impact
- Actions en retard et raisons
- Recommandations pour accélérer

### 4. RISQUES IDENTIFIÉS
Liste les risques E&S actuels ou émergents à surveiller.

### 5. OPPORTUNITÉS D'AMÉLIORATION
Propose 2-3 actions pour améliorer la performance ESG/impact.

### 6. PROCHAINES ÉTAPES
Actions recommandées pour le prochain trimestre.

### 7. NOTE GLOBALE
Attribue une note de 1 à 5 (5 = excellent) avec justification courte.

---

Sois factuel et constructif. Ce rapport sera partagé avec l'entreprise et les investisseurs."""


def format_esap_recommendations_prompt(
    company_name: str,
    sector: str,
    country: str,
    current_gaps: list,
    two_x_eligible: bool,
    two_x_data: dict
) -> str:
    """Prompt pour générer des recommandations ESAP additionnelles."""
    
    gaps_text = "\n".join([f"- {g}" for g in current_gaps]) if current_gaps else "Aucun gap identifié"
    
    return f"""# RECOMMANDATIONS ESAP - {company_name}

## CONTEXTE
- **Secteur:** {sector}
- **Pays:** {country}
- **Éligibilité 2X:** {"Oui" if two_x_eligible else "Non"}

## DONNÉES GENRE ACTUELLES
- Détention féminine: {two_x_data.get('women_ownership_pct', 0)}%
- Management féminin: {two_x_data.get('women_management_pct', 0)}%
- Employées femmes: {two_x_data.get('women_employees_pct', 0)}%

## GAPS IDENTIFIÉS
{gaps_text}

---

## TÂCHE

Propose 5-7 actions ESAP concrètes et réalistes pour:
1. Améliorer la performance E&S
2. Progresser vers l'éligibilité 2X Challenge
3. Renforcer les pratiques HSE

Pour chaque action, précise:
| Action | Catégorie | Responsable suggéré | Délai recommandé | Priorité | KPI de suivi |
|--------|-----------|---------------------|------------------|----------|--------------|

Catégories possibles: E&S, Genre/2X, HSE, Gouvernance, Climat, Social

Sois spécifique au secteur {sector} et au contexte {country}."""


def format_kpi_analysis_prompt(
    company_name: str,
    kpi_history: list,
    sector: str
) -> str:
    """Prompt pour analyser l'évolution des KPIs."""
    
    if not kpi_history or len(kpi_history) < 2:
        return "Pas assez de données historiques pour l'analyse."
    
    history_text = ""
    for i, snapshot in enumerate(kpi_history):
        date = snapshot['date'][:10]
        data = snapshot['data']
        history_text += f"""
**{date}:**
- Ownership: {data.get('women_ownership_pct', 'N/A')}%
- Management: {data.get('women_management_pct', 'N/A')}%
- Employées: {data.get('women_employees_pct', 'N/A')}%
- Total: {data.get('total_employees', 'N/A')}
"""
    
    return f"""# ANALYSE ÉVOLUTION KPIs - {company_name}

## HISTORIQUE DES KPIs
{history_text}

## SECTEUR
{sector}

---

## TÂCHE

Analyse l'évolution des KPIs et fournis:

1. **Tendances observées** (positives et négatives)
2. **Comparaison avec les standards sectoriels**
3. **Facteurs de succès** identifiés
4. **Points de vigilance**
5. **Projections** pour les 6 prochains mois
6. **Recommandations** pour améliorer les trajectoires

Sois analytique et propose des insights actionnables."""
