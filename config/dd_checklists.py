"""
Checklists de due diligence par catégorie de risque, secteur et contexte pays.
Génère des checklists personnalisées pour la phase de due diligence.
"""

from typing import List, Dict, Optional

# =============================================================================
# Questions DD de base (toujours incluses)
# =============================================================================
BASE_DD_QUESTIONS = [
    {
        "id": "gov_1",
        "category": "Gouvernance",
        "question": "Vérifier la structure de gouvernance et l'organigramme",
        "documents": ["Statuts à jour", "PV des AG des 3 dernières années", "Organigramme"],
        "priority": "high",
        "ifc_standard": "PS1"
    },
    {
        "id": "gov_2",
        "category": "Gouvernance",
        "question": "Existence et composition du conseil d'administration / comité de direction",
        "documents": ["Liste des administrateurs", "CV des dirigeants clés"],
        "priority": "high",
        "ifc_standard": "PS1"
    },
    {
        "id": "gov_3",
        "category": "Gouvernance",
        "question": "Politique anti-corruption et code d'éthique",
        "documents": ["Code d'éthique", "Politique anti-corruption", "Registre des cadeaux"],
        "priority": "medium",
        "ifc_standard": "PS1"
    },
    {
        "id": "lab_1",
        "category": "Social - Travail",
        "question": "Contrats de travail conformes au code du travail local",
        "documents": ["Modèles de contrats CDI/CDD", "Registre du personnel"],
        "priority": "high",
        "ifc_standard": "PS2"
    },
    {
        "id": "lab_2",
        "category": "Social - Travail",
        "question": "Politique de rémunération et conformité salaire minimum",
        "documents": ["Grille salariale", "Bulletins de paie échantillon"],
        "priority": "high",
        "ifc_standard": "PS2"
    },
    {
        "id": "lab_3",
        "category": "Social - Travail",
        "question": "Couverture sociale des employés (CNPS, assurance, retraite)",
        "documents": ["Attestations CNPS/sécurité sociale", "Contrats assurance"],
        "priority": "medium",
        "ifc_standard": "PS2"
    },
    {
        "id": "lab_4",
        "category": "Social - Travail",
        "question": "Politique de non-discrimination et égalité des chances",
        "documents": ["Politique RH", "Données désagrégées H/F"],
        "priority": "medium",
        "ifc_standard": "PS2"
    },
]

# =============================================================================
# Questions DD par catégorie de risque IFC
# =============================================================================
RISK_CATEGORY_DD = {
    "B+": [
        {
            "id": "env_b+_1",
            "category": "Environnement",
            "question": "Étude d'impact environnemental et social (EIES) existante et valide",
            "documents": ["Rapport EIES", "Certificat de conformité environnementale"],
            "priority": "high",
            "ifc_standard": "PS1"
        },
        {
            "id": "env_b+_2",
            "category": "Environnement",
            "question": "Plan de gestion environnementale et sociale (PGES) avec indicateurs",
            "documents": ["PGES", "Rapports de suivi trimestriels/annuels"],
            "priority": "high",
            "ifc_standard": "PS1"
        },
        {
            "id": "hse_b+_1",
            "category": "HSE",
            "question": "Politique HSE formalisée et système de management HSE",
            "documents": ["Politique HSE signée", "Manuel HSE", "Certifications ISO 14001/45001"],
            "priority": "high",
            "ifc_standard": "PS2"
        },
        {
            "id": "hse_b+_2",
            "category": "HSE",
            "question": "Registre des accidents et incidents avec analyse des causes",
            "documents": ["Registre accidents/incidents", "Rapports d'investigation"],
            "priority": "high",
            "ifc_standard": "PS2"
        },
        {
            "id": "hse_b+_3",
            "category": "HSE",
            "question": "Comité HSE ou CHSCT fonctionnel avec PV de réunions",
            "documents": ["PV réunions CHSCT", "Composition du comité"],
            "priority": "medium",
            "ifc_standard": "PS2"
        },
        {
            "id": "com_b+_1",
            "category": "Communautés",
            "question": "Mécanisme de gestion des plaintes communautaires opérationnel",
            "documents": ["Procédure de plaintes", "Registre des plaintes", "Rapports de résolution"],
            "priority": "medium",
            "ifc_standard": "PS4"
        },
        {
            "id": "com_b+_2",
            "category": "Communautés",
            "question": "Consultations des parties prenantes documentées",
            "documents": ["Rapports de consultation", "Listes de présence", "CR de réunions"],
            "priority": "medium",
            "ifc_standard": "PS1"
        },
        {
            "id": "env_b+_3",
            "category": "Environnement",
            "question": "Permis et autorisations environnementales en vigueur",
            "documents": ["Permis environnemental", "Autorisations d'exploitation"],
            "priority": "high",
            "ifc_standard": "PS1"
        },
    ],
    "B-": [
        {
            "id": "hse_b-_1",
            "category": "HSE",
            "question": "Existence d'un responsable HSE ou point focal identifié",
            "documents": ["Fiche de poste HSE", "Organigramme"],
            "priority": "medium",
            "ifc_standard": "PS2"
        },
        {
            "id": "hse_b-_2",
            "category": "HSE",
            "question": "Équipements de protection individuelle (EPI) fournis et utilisés",
            "documents": ["Liste EPI", "Registre de distribution", "Photos"],
            "priority": "medium",
            "ifc_standard": "PS2"
        },
        {
            "id": "env_b-_1",
            "category": "Environnement",
            "question": "Gestion des déchets et effluents conforme",
            "documents": ["Procédure déchets", "Contrats prestataires agréés", "Bordereaux"],
            "priority": "medium",
            "ifc_standard": "PS3"
        },
        {
            "id": "env_b-_2",
            "category": "Environnement",
            "question": "Consommation d'eau et d'énergie suivie",
            "documents": ["Relevés consommation", "Factures"],
            "priority": "low",
            "ifc_standard": "PS3"
        },
    ],
    "C": [
        {
            "id": "gen_c_1",
            "category": "Général",
            "question": "Conformité réglementaire générale (licences, autorisations)",
            "documents": ["Registre de commerce", "Licences d'exploitation", "Autorisations sectorielles"],
            "priority": "medium",
            "ifc_standard": "PS1"
        },
        {
            "id": "gen_c_2",
            "category": "Général",
            "question": "Respect basique du code du travail",
            "documents": ["Règlement intérieur", "Affichage obligatoire"],
            "priority": "low",
            "ifc_standard": "PS2"
        },
    ],
}

# =============================================================================
# Questions DD par secteur
# =============================================================================
SECTOR_DD = {
    "Agribusiness": [
        {
            "id": "agri_1",
            "category": "Environnement",
            "question": "Inventaire et gestion des pesticides et produits phytosanitaires",
            "documents": ["Liste des produits utilisés", "Fiches de données de sécurité (FDS)", "Formation applicateurs"],
            "priority": "high",
            "ifc_standard": "PS3"
        },
        {
            "id": "agri_2",
            "category": "Social",
            "question": "Conditions de travail des saisonniers et journaliers",
            "documents": ["Contrats saisonniers", "Registre journaliers", "Conditions de logement si applicable"],
            "priority": "high",
            "ifc_standard": "PS2"
        },
        {
            "id": "agri_3",
            "category": "Social",
            "question": "Politique sur le travail des enfants dans la chaîne de valeur",
            "documents": ["Politique travail des enfants", "Procédure de vérification fournisseurs"],
            "priority": "high",
            "ifc_standard": "PS2"
        },
        {
            "id": "agri_4",
            "category": "Environnement",
            "question": "Gestion de l'eau et droits d'irrigation",
            "documents": ["Permis d'eau", "Données consommation", "Sources d'approvisionnement"],
            "priority": "medium",
            "ifc_standard": "PS3"
        },
        {
            "id": "agri_5",
            "category": "Environnement",
            "question": "Impact sur la biodiversité et les écosystèmes locaux",
            "documents": ["Carte d'occupation des sols", "Étude biodiversité si zone sensible"],
            "priority": "medium",
            "ifc_standard": "PS6"
        },
        {
            "id": "agri_6",
            "category": "Social",
            "question": "Relations avec les communautés agricoles voisines",
            "documents": ["Accords fonciers", "PV réunions communautaires"],
            "priority": "medium",
            "ifc_standard": "PS4"
        },
    ],
    "Industrie & Manufacturing": [
        {
            "id": "ind_1",
            "category": "Environnement",
            "question": "Émissions atmosphériques et qualité de l'air",
            "documents": ["Mesures émissions", "Autorisation ICPE/équivalent", "Registre rejets"],
            "priority": "high",
            "ifc_standard": "PS3"
        },
        {
            "id": "ind_2",
            "category": "HSE",
            "question": "Sécurité des machines et équipements industriels",
            "documents": ["Registre maintenance", "Certifications équipements", "Consignes de sécurité"],
            "priority": "high",
            "ifc_standard": "PS2"
        },
        {
            "id": "ind_3",
            "category": "Environnement",
            "question": "Gestion des produits chimiques et substances dangereuses",
            "documents": ["Inventaire substances", "FDS", "Stockage conforme", "Formation"],
            "priority": "high",
            "ifc_standard": "PS3"
        },
        {
            "id": "ind_4",
            "category": "HSE",
            "question": "Risque incendie et plan d'évacuation",
            "documents": ["Plan d'évacuation", "Exercices incendie", "Équipements anti-incendie"],
            "priority": "medium",
            "ifc_standard": "PS2"
        },
        {
            "id": "ind_5",
            "category": "Environnement",
            "question": "Bruit industriel et nuisances sonores",
            "documents": ["Mesures de bruit", "Plaintes riverains", "Mesures de mitigation"],
            "priority": "low",
            "ifc_standard": "PS3"
        },
    ],
    "Santé": [
        {
            "id": "san_1",
            "category": "Spécifique Santé",
            "question": "Gestion des déchets médicaux (DASRI)",
            "documents": ["Procédure DASRI", "Contrat incinération agréé", "Bordereaux traçabilité"],
            "priority": "high",
            "ifc_standard": "PS3"
        },
        {
            "id": "san_2",
            "category": "Spécifique Santé",
            "question": "Autorisations sanitaires et accréditations",
            "documents": ["Autorisation ministère santé", "Accréditations", "Agréments"],
            "priority": "high",
            "ifc_standard": "PS1"
        },
        {
            "id": "san_3",
            "category": "HSE",
            "question": "Protection du personnel soignant (exposition biologique)",
            "documents": ["Protocole AES", "Vaccination personnel", "EPI médicaux"],
            "priority": "high",
            "ifc_standard": "PS2"
        },
        {
            "id": "san_4",
            "category": "Spécifique Santé",
            "question": "Gestion des médicaments et produits pharmaceutiques",
            "documents": ["Procédure pharmacie", "Chaîne du froid", "Gestion péremption"],
            "priority": "medium",
            "ifc_standard": "PS3"
        },
    ],
    "Énergie": [
        {
            "id": "ene_1",
            "category": "Environnement",
            "question": "Études d'impact sur la biodiversité (solaire/éolien)",
            "documents": ["Étude faune/flore", "Plan évitement/réduction/compensation"],
            "priority": "medium",
            "ifc_standard": "PS6"
        },
        {
            "id": "ene_2",
            "category": "Communautés",
            "question": "Accès à la terre et droits fonciers",
            "documents": ["Titres fonciers", "Accords avec propriétaires", "Compensations"],
            "priority": "high",
            "ifc_standard": "PS5"
        },
        {
            "id": "ene_3",
            "category": "HSE",
            "question": "Sécurité des installations électriques",
            "documents": ["Certifications électriques", "Habilitations personnel", "Consignation"],
            "priority": "high",
            "ifc_standard": "PS2"
        },
    ],
    "Services financiers": [
        {
            "id": "fin_1",
            "category": "Gouvernance",
            "question": "Politique de prêt responsable et surendettement",
            "documents": ["Politique crédit", "Procédure évaluation capacité de remboursement"],
            "priority": "medium",
            "ifc_standard": "PS1"
        },
        {
            "id": "fin_2",
            "category": "Social",
            "question": "Protection des données clients",
            "documents": ["Politique confidentialité", "Mesures cybersécurité"],
            "priority": "medium",
            "ifc_standard": "PS1"
        },
        {
            "id": "fin_3",
            "category": "Gouvernance",
            "question": "Politique E&S pour le portefeuille de prêts/investissements",
            "documents": ["Liste d'exclusion", "Procédure screening E&S des clients"],
            "priority": "high",
            "ifc_standard": "PS1"
        },
    ],
    "Tech & Digital": [
        {
            "id": "tech_1",
            "category": "Gouvernance",
            "question": "Protection des données personnelles (RGPD ou équivalent)",
            "documents": ["Politique données", "Registre traitements", "Consentements"],
            "priority": "high",
            "ifc_standard": "PS1"
        },
        {
            "id": "tech_2",
            "category": "Environnement",
            "question": "Gestion des déchets électroniques (DEEE)",
            "documents": ["Procédure DEEE", "Filière recyclage"],
            "priority": "low",
            "ifc_standard": "PS3"
        },
    ],
    "Distribution & Retail": [
        {
            "id": "dist_1",
            "category": "Social",
            "question": "Conditions de travail dans la chaîne d'approvisionnement",
            "documents": ["Code de conduite fournisseurs", "Audits fournisseurs"],
            "priority": "medium",
            "ifc_standard": "PS2"
        },
        {
            "id": "dist_2",
            "category": "HSE",
            "question": "Sécurité des entrepôts et manutention",
            "documents": ["Plan de circulation", "Formation caristes", "EPI"],
            "priority": "medium",
            "ifc_standard": "PS2"
        },
    ],
    "Tourisme & Hôtellerie": [
        {
            "id": "tour_1",
            "category": "Environnement",
            "question": "Gestion de l'eau et des eaux usées",
            "documents": ["Consommation eau", "Traitement eaux usées", "Permis rejet"],
            "priority": "medium",
            "ifc_standard": "PS3"
        },
        {
            "id": "tour_2",
            "category": "Communautés",
            "question": "Relations avec les communautés locales et retombées économiques",
            "documents": ["Politique achats locaux", "Emploi local", "Initiatives communautaires"],
            "priority": "medium",
            "ifc_standard": "PS4"
        },
        {
            "id": "tour_3",
            "category": "Environnement",
            "question": "Impact sur les sites naturels et culturels",
            "documents": ["Proximité zones protégées", "Mesures de protection"],
            "priority": "medium",
            "ifc_standard": "PS6"
        },
    ],
}

# =============================================================================
# Questions DD pour pays fragiles
# =============================================================================
COUNTRY_DD = {
    "fragile_states": [
        {
            "id": "frag_1",
            "category": "Sécurité",
            "question": "Évaluation des risques sécuritaires et plan de sûreté",
            "documents": ["Analyse risques sécurité", "Plan de sûreté", "Procédures d'urgence"],
            "priority": "high",
            "ifc_standard": "PS4"
        },
        {
            "id": "frag_2",
            "category": "Gouvernance",
            "question": "Due diligence intégrité renforcée (KYC/KYB)",
            "documents": ["Vérifications KYC complètes", "Déclarations UBO", "Screening sanctions"],
            "priority": "high",
            "ifc_standard": "PS1"
        },
        {
            "id": "frag_3",
            "category": "Sécurité",
            "question": "Gestion des prestataires de sécurité",
            "documents": ["Contrats sécurité", "Formation droits humains", "Code de conduite"],
            "priority": "medium",
            "ifc_standard": "PS4"
        },
        {
            "id": "frag_4",
            "category": "Communautés",
            "question": "Risques de tensions communautaires ou conflits",
            "documents": ["Analyse conflits", "Cartographie parties prenantes sensibles"],
            "priority": "medium",
            "ifc_standard": "PS1"
        },
    ],
    "ldc_countries": [
        {
            "id": "ldc_1",
            "category": "Social",
            "question": "Respect du salaire minimum et conditions de travail décentes",
            "documents": ["Grille salariale vs minimum légal", "Heures supplémentaires"],
            "priority": "high",
            "ifc_standard": "PS2"
        },
    ],
}

# =============================================================================
# Questions 2X Challenge (si gaps identifiés)
# =============================================================================
TWO_X_DD_QUESTIONS = {
    "Leadership": {
        "id": "2x_leadership",
        "category": "2X Challenge - Genre",
        "question": "Plan d'action pour augmenter la représentation des femmes au management",
        "documents": ["Plan action genre", "Objectifs chiffrés", "Politique promotion"],
        "priority": "medium",
        "ifc_standard": "PS2"
    },
    "Emploi": {
        "id": "2x_employment",
        "category": "2X Challenge - Genre",
        "question": "Stratégie de recrutement et rétention des femmes",
        "documents": ["Politique recrutement inclusive", "Données turnover H/F", "Mesures rétention"],
        "priority": "medium",
        "ifc_standard": "PS2"
    },
    "Entrepreneuriat": {
        "id": "2x_entrepreneurship",
        "category": "2X Challenge - Genre",
        "question": "Documentation de l'actionnariat et gouvernance genre",
        "documents": ["Table de capitalisation", "Statuts", "Pacte d'actionnaires"],
        "priority": "low",
        "ifc_standard": "PS1"
    },
}


def generate_dd_checklist(
    sector: str,
    risk_category: str,
    country_fragile: bool = False,
    country_ldc: bool = False,
    two_x_gaps: Optional[List[Dict]] = None
) -> List[Dict]:
    """
    Génère une checklist DD personnalisée selon le contexte.
    
    Args:
        sector: Secteur de l'entreprise
        risk_category: Catégorie de risque IFC (A, B+, B-, C)
        country_fragile: Si le pays est classé État fragile
        country_ldc: Si le pays est un Pays Moins Avancé (LDC)
        two_x_gaps: Liste des gaps 2X identifiés [{"criterion": "Leadership", ...}]
    
    Returns:
        Liste de questions DD triées par priorité
    """
    checklist = []
    
    # 1. Questions de base (toujours incluses)
    checklist.extend(BASE_DD_QUESTIONS)
    
    # 2. Questions selon catégorie de risque
    if risk_category in RISK_CATEGORY_DD:
        checklist.extend(RISK_CATEGORY_DD[risk_category])
    
    # Si B+, inclure aussi les questions B- (cumulatif)
    if risk_category == "B+" and "B-" in RISK_CATEGORY_DD:
        checklist.extend(RISK_CATEGORY_DD["B-"])
    
    # 3. Questions selon secteur
    if sector in SECTOR_DD:
        checklist.extend(SECTOR_DD[sector])
    
    # 4. Questions pays fragile
    if country_fragile:
        checklist.extend(COUNTRY_DD["fragile_states"])
    
    # 5. Questions pays LDC
    if country_ldc:
        checklist.extend(COUNTRY_DD["ldc_countries"])
    
    # 6. Questions 2X si gaps identifiés
    if two_x_gaps:
        for gap in two_x_gaps:
            criterion = gap.get("criterion", "")
            if criterion in TWO_X_DD_QUESTIONS:
                question = TWO_X_DD_QUESTIONS[criterion].copy()
                question["question"] = f"{question['question']} (objectif : {gap.get('target', 'à définir')})"
                checklist.append(question)
    
    # Trier par priorité
    priority_order = {"high": 0, "medium": 1, "low": 2}
    checklist.sort(key=lambda x: (priority_order.get(x["priority"], 2), x["category"]))
    
    # Dédupliquer par ID
    seen = set()
    unique_checklist = []
    for item in checklist:
        if item["id"] not in seen:
            seen.add(item["id"])
            unique_checklist.append(item)
    
    # Ajouter numérotation
    for i, item in enumerate(unique_checklist, 1):
        item["number"] = i
    
    return unique_checklist


def get_checklist_summary(checklist: List[Dict]) -> Dict:
    """
    Retourne un résumé de la checklist.
    """
    categories = {}
    priorities = {"high": 0, "medium": 0, "low": 0}
    
    for item in checklist:
        cat = item["category"]
        categories[cat] = categories.get(cat, 0) + 1
        priorities[item["priority"]] = priorities.get(item["priority"], 0) + 1
    
    return {
        "total": len(checklist),
        "by_category": categories,
        "by_priority": priorities,
        "high_priority_count": priorities["high"]
    }
