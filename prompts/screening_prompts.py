"""
Prompts pour l'analyse IA au stade Screening.
Génère une recommandation GO/NO-GO basée sur les informations du deal.
"""

SCREENING_SYSTEM_PROMPT = """Tu es un analyste ESG senior spécialisé dans l'investissement à impact en Afrique.
Tu travailles pour IPAE3, un fonds d'investissement à impact qui cible les PME africaines.

Ton rôle est d'effectuer une première évaluation rapide (screening) des opportunités d'investissement
pour déterminer si elles méritent une Due Diligence approfondie.

Tu dois être:
- Rigoureux et factuel
- Attentif aux risques E&S selon les standards IFC
- Sensible aux enjeux de genre (2X Challenge)
- Pragmatique sur le contexte africain

Format de réponse attendu: analyse structurée avec recommandation claire."""


def format_screening_prompt(
    company_name: str,
    country: str,
    country_context: str,
    sector: str,
    subsector: str,
    description: str,
    employees: int,
    revenue: str,
    risk_category: str,
    two_x_eligible: bool,
    two_x_criteria_met: int,
    two_x_data: dict
) -> str:
    """Formate le prompt pour l'analyse de screening."""
    
    return f"""# ANALYSE SCREENING - {company_name}

## INFORMATIONS ENTREPRISE

**Entreprise:** {company_name}
**Pays:** {country}
**Secteur:** {sector} / {subsector}
**Description:** {description}
**Taille:** {employees} employés | CA: {revenue}

## CONTEXTE PAYS
{country_context}

## CLASSIFICATION E&S PRÉLIMINAIRE
- **Catégorie de risque:** {risk_category}
- Cette classification détermine le niveau de Due Diligence requis

## ÉLIGIBILITÉ 2X CHALLENGE
- **Statut:** {"✅ ÉLIGIBLE" if two_x_eligible else "❌ NON ÉLIGIBLE"}
- **Critères validés:** {two_x_criteria_met}/4
- Détention féminine: {two_x_data.get('women_ownership_pct', 0)}%
- Management féminin: {two_x_data.get('women_management_pct', 0)}%
- Employées femmes: {two_x_data.get('women_employees_pct', 0)}%
- Produit bénéficiant aux femmes: {"Oui" if two_x_data.get('benefits_women') else "Non"}

---

## TÂCHE

Effectue une analyse de screening rapide et fournis:

### 1. SYNTHÈSE (3-4 lignes)
Résume le profil de l'entreprise et son potentiel d'investissement.

### 2. POINTS FORTS (3-5 points)
Liste les atouts de cette opportunité.

### 3. POINTS D'ATTENTION (3-5 points)
Liste les risques et points à approfondir en DD.

### 4. RISQUES E&S PRINCIPAUX
Identifie les 2-3 risques E&S majeurs liés au secteur et au pays.

### 5. POTENTIEL 2X CHALLENGE
Évalue le potentiel d'amélioration sur les critères genre.

### 6. RECOMMANDATION

**DÉCISION:** [GO / NO-GO / GO AVEC RÉSERVES]

**Justification:** (2-3 phrases)

**Conditions préalables à la DD (si GO):**
- Liste des points à vérifier en priorité

---

Réponds de manière structurée et concise. Sois direct dans ta recommandation."""


SCREENING_DD_CHECKLIST_PROMPT = """Tu es un analyste ESG senior. Basé sur le profil de l'entreprise ci-dessous,
génère une liste des 5-10 points prioritaires à vérifier lors de la Due Diligence terrain.

{deal_info}

Format de réponse:
Pour chaque point, indique:
1. Le point à vérifier
2. Pourquoi c'est important
3. Documents à demander

Sois spécifique au secteur et au contexte pays."""
