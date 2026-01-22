"""
Classification des risques E&S par secteur/sous-secteur selon IFC.
Structure hiérarchique pour filtrage dynamique dans l'UI.
"""

SECTOR_HIERARCHY = {
    "Agribusiness": {
        "risk": "B+",
        "subsectors": {
            "Production agricole": "B+",
            "Transformation agroalimentaire": "B+",
            "Élevage": "B+",
            "Aquaculture": "B+",
            "Intrants agricoles": "B-",
            "Distribution alimentaire": "C",
        }
    },
    "Industrie & Manufacturing": {
        "risk": "B+",
        "subsectors": {
            "Matériaux de construction": "B+",
            "Textile & Habillement": "B+",
            "Plastique & Emballage": "B+",
            "Bois & Ameublement": "B-",
            "Agroalimentaire industriel": "B+",
            "Chimie légère & Cosmétiques": "B+",
        }
    },
    "Services financiers": {
        "risk": "C",
        "subsectors": {
            "Microfinance": "C",
            "Banque": "C",
            "Assurance": "C",
            "Fintech": "C",
            "Mobile Money": "C",
        }
    },
    "Santé": {
        "risk": "B-",
        "subsectors": {
            "Cliniques & Hôpitaux": "B-",
            "Pharmacie & Distribution": "C",
            "Laboratoires": "B-",
            "E-santé": "C",
        }
    },
    "Éducation & Formation": {
        "risk": "C",
        "subsectors": {
            "Écoles & Universités": "C",
            "Formation professionnelle": "C",
            "EdTech": "C",
        }
    },
    "Énergie": {
        "risk": "B+",
        "subsectors": {
            "Solaire": "B-",
            "Mini-grid": "B-",
            "Distribution électrique": "B+",
            "Efficacité énergétique": "C",
        }
    },
    "Tech & Digital": {
        "risk": "C",
        "subsectors": {
            "Logiciels & SaaS": "C",
            "E-commerce": "C",
            "Services IT": "C",
            "Télécom & Connectivité": "B-",
        }
    },
    "Distribution & Retail": {
        "risk": "C",
        "subsectors": {
            "Grande distribution": "C",
            "Distribution spécialisée": "C",
            "Logistique & Transport": "B-",
        }
    },
    "Tourisme & Hôtellerie": {
        "risk": "B-",
        "subsectors": {
            "Hôtellerie": "B-",
            "Restauration": "C",
            "Tourisme durable": "B-",
        }
    },
}

# Catégories de risque IFC
RISK_CATEGORIES = {
    'A': {
        'name': 'High Risk',
        'color': '🔴',
        'hex_color': '#FF0000',
        'investment_allowed': False,
        'due_diligence': 'Non éligible IPAE3 - Risques E&S significatifs et irréversibles'
    },
    'B+': {
        'name': 'Medium-High Risk',
        'color': '🟠',
        'hex_color': '#FF8C00',
        'investment_allowed': True,
        'due_diligence': 'Due diligence E&S externe requise'
    },
    'B-': {
        'name': 'Medium-Low Risk',
        'color': '🟡',
        'hex_color': '#FFD700',
        'investment_allowed': True,
        'due_diligence': 'Due diligence E&S interne'
    },
    'C': {
        'name': 'Low Risk',
        'color': '🟢',
        'hex_color': '#32CD32',
        'investment_allowed': True,
        'due_diligence': 'Screening ESG basique'
    }
}

# Standards IFC applicables par secteur
SECTOR_IFC_STANDARDS = {
    'Agribusiness': [1, 2, 3, 4, 5, 6],
    'Industrie & Manufacturing': [1, 2, 3, 4],
    'Services financiers': [1, 2],
    'Santé': [1, 2, 3, 4],
    'Éducation & Formation': [1, 2],
    'Énergie': [1, 2, 3, 4, 6],
    'Tech & Digital': [1, 2],
    'Distribution & Retail': [1, 2, 3],
    'Tourisme & Hôtellerie': [1, 2, 3, 4, 6],
}

# Description des 8 Performance Standards IFC
IFC_STANDARDS = {
    1: 'Assessment and Management of Environmental and Social Risks and Impacts',
    2: 'Labor and Working Conditions',
    3: 'Resource Efficiency and Pollution Prevention',
    4: 'Community Health, Safety and Security',
    5: 'Land Acquisition and Involuntary Resettlement',
    6: 'Biodiversity Conservation and Sustainable Natural Resource Management',
    7: 'Indigenous Peoples',
    8: 'Cultural Heritage'
}


def get_sectors() -> list:
    """Retourne la liste des secteurs."""
    return list(SECTOR_HIERARCHY.keys())


def get_subsectors(sector: str) -> list:
    """Retourne la liste des sous-secteurs pour un secteur donné."""
    if sector in SECTOR_HIERARCHY:
        return list(SECTOR_HIERARCHY[sector]["subsectors"].keys())
    return []


def get_risk_category(sector: str, subsector: str = None) -> str:
    """Retourne la catégorie de risque pour un secteur/sous-secteur."""
    if sector not in SECTOR_HIERARCHY:
        return "B-"  # Default
    
    if subsector and subsector in SECTOR_HIERARCHY[sector]["subsectors"]:
        return SECTOR_HIERARCHY[sector]["subsectors"][subsector]
    
    return SECTOR_HIERARCHY[sector]["risk"]


def get_risk_display(risk_category: str) -> dict:
    """Retourne les informations d'affichage pour une catégorie de risque."""
    if risk_category in RISK_CATEGORIES:
        return RISK_CATEGORIES[risk_category]
    return RISK_CATEGORIES['B-']  # Default


def get_applicable_standards(sector: str) -> list:
    """Retourne les standards IFC applicables pour un secteur."""
    if sector in SECTOR_IFC_STANDARDS:
        standard_ids = SECTOR_IFC_STANDARDS[sector]
        return [(id, IFC_STANDARDS[id]) for id in standard_ids]
    return [(1, IFC_STANDARDS[1]), (2, IFC_STANDARDS[2])]  # Minimum PS1 & PS2
