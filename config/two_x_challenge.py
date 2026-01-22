"""
Configuration et logique du 2X Challenge scoring.
Basé sur les critères officiels 2X Challenge (https://www.2xchallenge.org/criteria)

Le 2X Challenge est une initiative des DFIs du G7 pour mobiliser des capitaux
en faveur de l'autonomisation économique des femmes.

Une entreprise est éligible si elle valide AU MOINS 1 des 4 critères.
"""

from typing import Dict, List, Optional, Any

# Seuils par secteur (certains secteurs ont des seuils différents selon 2X)
SECTOR_THRESHOLDS = {
    "default": {
        "leadership": 0.30,  # 30% femmes senior management
        "employment": 0.30,  # 30% femmes employées
    },
    "Industrie & Manufacturing": {
        "leadership": 0.25,
        "employment": 0.25,
    },
    "Tech & Digital": {
        "leadership": 0.25,
        "employment": 0.20,
    },
    "Agribusiness": {
        "leadership": 0.25,
        "employment": 0.30,
    },
    "Énergie": {
        "leadership": 0.25,
        "employment": 0.25,
    },
    "Services financiers": {
        "leadership": 0.30,
        "employment": 0.40,
    },
}

# Configuration des 4 critères 2X Challenge
TWO_X_CRITERIA = {
    "entrepreneurship": {
        "id": "1",
        "name": "Entrepreneuriat",
        "short_name": "Fondatrice",
        "question": "L'entreprise est-elle fondée ou détenue majoritairement par une femme ?",
        "threshold": 0.51,  # 51% ownership
        "threshold_display": "≥51% détention féminine",
        "help": "Une femme détient au moins 51% du capital de l'entreprise, ou l'entreprise a été fondée par une femme qui reste impliquée dans la direction.",
        "data_field": "women_ownership_pct",
        "icon": "👩‍💼",
    },
    "leadership": {
        "id": "2",
        "name": "Leadership",
        "short_name": "Management",
        "question": "Quel est le pourcentage de femmes dans le senior management ?",
        "threshold": "sector_based",  # Dépend du secteur
        "threshold_display": "≥25-30% selon secteur",
        "help": "Pourcentage de femmes au niveau C-suite, direction générale, comité exécutif, ou postes de décision équivalents.",
        "data_field": "women_management_pct",
        "icon": "👔",
    },
    "employment": {
        "id": "3",
        "name": "Emploi",
        "short_name": "Employées",
        "question": "Quel est le pourcentage de femmes dans l'effectif total ?",
        "threshold": "sector_based",
        "threshold_display": "≥20-40% selon secteur",
        "help": "Pourcentage de femmes dans l'effectif total (CDI, CDD, temps plein équivalent). Inclut tous les niveaux hiérarchiques.",
        "data_field": "women_employees_pct",
        "icon": "👥",
    },
    "consumption": {
        "id": "4",
        "name": "Consommation",
        "short_name": "Produit/Service",
        "question": "Le produit ou service bénéficie-t-il spécifiquement aux femmes ?",
        "threshold": None,  # Qualitatif
        "threshold_display": "Produit/service ciblant les femmes",
        "help": "Le produit ou service est conçu pour répondre aux besoins spécifiques des femmes, ou bénéficie de manière disproportionnée aux femmes. Exemples : santé maternelle, produits d'hygiène féminine, services financiers pour femmes entrepreneures, éducation des filles.",
        "data_field": "benefits_women",
        "icon": "🎯",
    },
}


def get_threshold(criterion: str, sector: str) -> Optional[float]:
    """
    Retourne le seuil applicable pour un critère et un secteur.
    
    Args:
        criterion: Clé du critère ('entrepreneurship', 'leadership', 'employment', 'consumption')
        sector: Nom du secteur
    
    Returns:
        Seuil en décimal (ex: 0.30 pour 30%) ou None pour les critères qualitatifs
    """
    if criterion == "entrepreneurship":
        return TWO_X_CRITERIA["entrepreneurship"]["threshold"]
    
    if criterion == "consumption":
        return None
    
    if criterion in ["leadership", "employment"]:
        sector_config = SECTOR_THRESHOLDS.get(sector, SECTOR_THRESHOLDS["default"])
        return sector_config.get(criterion, SECTOR_THRESHOLDS["default"][criterion])
    
    return None


def get_threshold_display(criterion: str, sector: str) -> str:
    """
    Retourne le seuil formaté pour affichage (ex: "≥30%").
    """
    threshold = get_threshold(criterion, sector)
    if threshold is None:
        return "Qualitatif"
    return f"≥{int(threshold * 100)}%"


def evaluate_2x_criterion(criterion: str, value: Any, sector: str) -> Dict:
    """
    Évalue un critère 2X Challenge.
    
    Args:
        criterion: Clé du critère
        value: Valeur (pourcentage 0-100 ou booléen)
        sector: Nom du secteur
    
    Returns:
        {
            "met": bool,
            "threshold": float ou None,
            "value": valeur normalisée,
            "gap": écart si non atteint,
            "gap_display": écart formaté
        }
    """
    threshold = get_threshold(criterion, sector)
    
    # Critère qualitatif (consumption)
    if threshold is None:
        is_met = value is True or value == "yes" or value == "Oui"
        return {
            "met": is_met,
            "threshold": None,
            "value": value,
            "gap": None,
            "gap_display": None
        }
    
    # Critères quantitatifs
    # Normaliser la valeur (si en pourcentage 0-100, convertir en décimal)
    if isinstance(value, (int, float)):
        value_decimal = value / 100 if value > 1 else value
    else:
        value_decimal = 0
    
    met = value_decimal >= threshold
    gap = max(0, threshold - value_decimal)
    
    return {
        "met": met,
        "threshold": threshold,
        "value": value_decimal,
        "value_pct": value_decimal * 100,
        "threshold_pct": threshold * 100,
        "gap": gap,
        "gap_pct": gap * 100,
        "gap_display": f"+{gap * 100:.0f}% requis" if gap > 0 else None
    }


def calculate_2x_eligibility(data: Dict, sector: str) -> Dict:
    """
    Calcule l'éligibilité globale au 2X Challenge.
    Une entreprise est éligible si elle valide AU MOINS 1 critère.
    
    Args:
        data: {
            "women_ownership_pct": float (0-100),
            "women_management_pct": float (0-100),
            "women_employees_pct": float (0-100),
            "benefits_women": bool
        }
        sector: str
    
    Returns:
        {
            "eligible": bool,
            "criteria_met": int,
            "criteria_total": int,
            "criteria_details": {criterion: {name, met, value, threshold, gap, ...}},
            "recommendations": [{criterion, action, current, target}],
            "summary": str
        }
    """
    results = {}
    criteria_met = 0
    criteria_met_names = []
    recommendations = []
    
    # Évaluer chaque critère
    for key, config in TWO_X_CRITERIA.items():
        field = config["data_field"]
        value = data.get(field, 0 if field != "benefits_women" else False)
        
        evaluation = evaluate_2x_criterion(key, value, sector)
        
        results[key] = {
            "id": config["id"],
            "name": config["name"],
            "short_name": config["short_name"],
            "icon": config["icon"],
            "met": evaluation["met"],
            "value": evaluation.get("value_pct", evaluation["value"]),
            "threshold": evaluation.get("threshold_pct", evaluation["threshold"]),
            "gap": evaluation.get("gap_pct"),
            "gap_display": evaluation.get("gap_display"),
        }
        
        if evaluation["met"]:
            criteria_met += 1
            criteria_met_names.append(config["name"])
        elif evaluation.get("gap_display"):
            recommendations.append({
                "criterion": config["name"],
                "action": f"Augmenter le taux de femmes ({config['short_name'].lower()})",
                "current": f"{evaluation.get('value_pct', 0):.0f}%",
                "target": f"{evaluation.get('threshold_pct', 0):.0f}%",
                "gap": f"+{evaluation.get('gap_pct', 0):.0f} points",
                "priority": "high" if evaluation.get("gap_pct", 100) < 10 else "medium"
            })
    
    # Trier les recommandations par proximité du seuil (plus facile à atteindre en premier)
    recommendations.sort(key=lambda x: float(x["gap"].replace("+", "").replace(" points", "")))
    
    # Générer le résumé
    if criteria_met >= 1:
        summary = f"✅ Éligible 2X Challenge ({criteria_met}/4 critères validés : {', '.join(criteria_met_names)})"
    else:
        if recommendations:
            easiest = recommendations[0]
            summary = f"❌ Non éligible 2X. Action prioritaire : {easiest['action']} ({easiest['gap']})"
        else:
            summary = "❌ Non éligible 2X Challenge (0/4 critères validés)"
    
    return {
        "eligible": criteria_met >= 1,
        "criteria_met": criteria_met,
        "criteria_total": len(TWO_X_CRITERIA),
        "criteria_met_names": criteria_met_names,
        "criteria_details": results,
        "recommendations": recommendations[:3],  # Top 3 recommandations
        "summary": summary
    }


def get_2x_status_display(result: Dict) -> str:
    """
    Retourne le statut 2X formaté pour affichage.
    """
    if result["eligible"]:
        return f"✅ ÉLIGIBLE ({result['criteria_met']}/4)"
    else:
        return f"❌ NON ÉLIGIBLE (0/4)"


def get_2x_action_plan(result: Dict) -> List[str]:
    """
    Génère un plan d'action pour atteindre l'éligibilité 2X.
    """
    if result["eligible"]:
        return ["Maintenir les pratiques actuelles", "Documenter les indicateurs pour le reporting"]
    
    actions = []
    for rec in result["recommendations"]:
        actions.append(f"• {rec['action']} : passer de {rec['current']} à {rec['target']} ({rec['gap']})")
    
    if not actions:
        actions = ["• Évaluer les opportunités d'amélioration sur les 4 critères 2X"]
    
    return actions
