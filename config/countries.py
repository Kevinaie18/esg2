"""
Configuration enrichie des pays IPAE3 avec contexte détaillé.
Inclut : réglementations, risques climat, contexte genre, indicateurs macro.
"""

from typing import Dict, List, Optional

IPAE3_COUNTRIES: Dict[str, Dict] = {
    
    "Côte d'Ivoire": {
        "region": "Afrique de l'Ouest",
        "ldc": False,
        "fragile": False,
        "iso_code": "CIV",
        "regulatory_context": {
            "environmental_agency": "ANDE (Agence Nationale De l'Environnement)",
            "eie_required": True,
            "eie_threshold": "Tous projets industriels, agricoles >10ha",
            "labor_code": "Code du Travail 2015",
            "minimum_wage": "60,000 FCFA/mois (~90 EUR)",
            "social_security": "CNPS obligatoire",
            "key_regulations": ["Loi n°96-766 Code Environnement", "Code du Travail 2015"]
        },
        "climate_risks": {
            "exposure": "Moyen",
            "main_risks": ["Sécheresse Nord", "Inondations côtières", "Érosion côtière"],
            "vulnerable_sectors": ["Agriculture cacaoyère", "Pêche", "Infrastructure côtière"],
            "ndc_target": "Réduction 28% d'ici 2030"
        },
        "macro_indicators": {
            "population": "28 millions",
            "gdp_growth_2023": "6.5%",
            "inflation_2023": "4.4%",
            "ease_of_business_rank": 110,
            "currency": "FCFA (XOF)",
            "main_exports": ["Cacao", "Café", "Huile de palme", "Caoutchouc"]
        },
        "gender_context": {
            "women_labor_participation": "52%",
            "gender_gap_index_rank": 118,
            "key_challenges": ["Accès au foncier", "Financement", "Représentation politique"],
            "positive_factors": ["Politique nationale genre", "Quota 30% femmes élues"]
        }
    },
    
    "Sénégal": {
        "region": "Afrique de l'Ouest",
        "ldc": True,
        "fragile": False,
        "iso_code": "SEN",
        "regulatory_context": {
            "environmental_agency": "DEEC (Direction de l'Environnement)",
            "eie_required": True,
            "eie_threshold": "Catégorie 1 et 2",
            "labor_code": "Code du Travail 1997",
            "minimum_wage": "302 FCFA/heure (~55 EUR/mois)",
            "social_security": "CSS et IPRES obligatoires",
            "key_regulations": ["Code Environnement 2001", "Code du Travail"]
        },
        "climate_risks": {
            "exposure": "Élevé",
            "main_risks": ["Sécheresse", "Élévation niveau mer", "Salinisation"],
            "vulnerable_sectors": ["Agriculture", "Pêche", "Tourisme côtier"],
            "ndc_target": "Réduction 29.5% d'ici 2030"
        },
        "macro_indicators": {
            "population": "18 millions",
            "gdp_growth_2023": "4.1%",
            "inflation_2023": "5.9%",
            "ease_of_business_rank": 123,
            "currency": "FCFA (XOF)",
            "main_exports": ["Or", "Phosphates", "Poisson", "Arachide"]
        },
        "gender_context": {
            "women_labor_participation": "33%",
            "gender_gap_index_rank": 130,
            "key_challenges": ["Emploi formel", "Accès crédit", "Charge domestique"],
            "positive_factors": ["Loi parité 2010", "Stratégie nationale genre"]
        }
    },
    
    "Mali": {
        "region": "Afrique de l'Ouest",
        "ldc": True,
        "fragile": True,
        "iso_code": "MLI",
        "regulatory_context": {
            "environmental_agency": "DNACPN",
            "eie_required": True,
            "eie_threshold": "Projets catégorie A et B",
            "labor_code": "Code du Travail 1992",
            "minimum_wage": "40,000 FCFA/mois (~60 EUR)",
            "social_security": "INPS obligatoire",
            "key_regulations": ["Loi pollutions 01-020", "Code du Travail"]
        },
        "climate_risks": {
            "exposure": "Très élevé",
            "main_risks": ["Sécheresse sévère", "Désertification", "Inondations"],
            "vulnerable_sectors": ["Agriculture", "Élevage", "Ressources en eau"],
            "ndc_target": "Réduction 31% d'ici 2030"
        },
        "macro_indicators": {
            "population": "22 millions",
            "gdp_growth_2023": "3.7%",
            "inflation_2023": "2.8%",
            "ease_of_business_rank": 148,
            "currency": "FCFA (XOF)",
            "main_exports": ["Or", "Coton", "Bétail"]
        },
        "gender_context": {
            "women_labor_participation": "40%",
            "gender_gap_index_rank": 158,
            "key_challenges": ["Mariage précoce", "Éducation filles", "Accès santé"],
            "positive_factors": ["Politique nationale genre 2011"]
        },
        "security_context": {
            "risk_level": "Élevé",
            "affected_regions": ["Nord", "Centre"],
            "stable_regions": ["Bamako", "Sud"],
            "recommendations": ["DD sécurité renforcée", "Plan de continuité requis"]
        }
    },
    
    "Burkina Faso": {
        "region": "Afrique de l'Ouest",
        "ldc": True,
        "fragile": True,
        "iso_code": "BFA",
        "regulatory_context": {
            "environmental_agency": "BUNEE",
            "eie_required": True,
            "eie_threshold": "Projets listés Code Environnement",
            "labor_code": "Code du Travail 2008",
            "minimum_wage": "34,664 FCFA/mois (~52 EUR)",
            "social_security": "CNSS obligatoire",
            "key_regulations": ["Code Environnement 2013", "Code du Travail 2008"]
        },
        "climate_risks": {
            "exposure": "Très élevé",
            "main_risks": ["Sécheresse", "Dégradation sols", "Inondations"],
            "vulnerable_sectors": ["Agriculture", "Élevage", "Ressources eau"],
            "ndc_target": "Réduction 18.2% d'ici 2030"
        },
        "macro_indicators": {
            "population": "22 millions",
            "gdp_growth_2023": "4.3%",
            "inflation_2023": "1.4%",
            "ease_of_business_rank": 151,
            "currency": "FCFA (XOF)",
            "main_exports": ["Or", "Coton", "Bétail", "Karité"]
        },
        "gender_context": {
            "women_labor_participation": "45%",
            "gender_gap_index_rank": 147,
            "key_challenges": ["Mariage précoce", "Accès éducation"],
            "positive_factors": ["Politique nationale genre"]
        },
        "security_context": {
            "risk_level": "Très élevé",
            "affected_regions": ["Nord", "Est", "Sahel", "Centre-Nord"],
            "stable_regions": ["Ouagadougou", "Sud-Ouest"],
            "recommendations": ["Extrême prudence", "Limiter zones stables"]
        }
    },
    
    "Niger": {
        "region": "Afrique de l'Ouest",
        "ldc": True,
        "fragile": True,
        "iso_code": "NER",
        "regulatory_context": {
            "environmental_agency": "BNEE",
            "eie_required": True,
            "eie_threshold": "Projets impact significatif",
            "labor_code": "Code du Travail 2012",
            "minimum_wage": "30,047 FCFA/mois (~45 EUR)",
            "social_security": "CNSS obligatoire",
            "key_regulations": ["Loi-cadre environnement 98-56", "Code du Travail 2012"]
        },
        "climate_risks": {
            "exposure": "Très élevé",
            "main_risks": ["Sécheresse extrême", "Désertification", "Crises alimentaires"],
            "vulnerable_sectors": ["Agriculture subsistance", "Élevage nomade"],
            "ndc_target": "Réduction 25% d'ici 2030"
        },
        "macro_indicators": {
            "population": "26 millions",
            "gdp_growth_2023": "2.5%",
            "inflation_2023": "3.7%",
            "ease_of_business_rank": 132,
            "currency": "FCFA (XOF)",
            "main_exports": ["Uranium", "Or", "Pétrole", "Bétail"]
        },
        "gender_context": {
            "women_labor_participation": "28%",
            "gender_gap_index_rank": 177,
            "key_challenges": ["Mariage précoce (plus haut mondial)", "Très faible scolarisation"],
            "positive_factors": ["Plan d'action genre"]
        },
        "security_context": {
            "risk_level": "Très élevé",
            "affected_regions": ["Tillabéri", "Tahoua", "Diffa", "Agadez"],
            "stable_regions": ["Niamey", "Maradi", "Zinder"],
            "recommendations": ["Investissements très prudents", "Limiter à Niamey"]
        }
    },
    
    "Bénin": {
        "region": "Afrique de l'Ouest",
        "ldc": True,
        "fragile": False,
        "iso_code": "BEN",
        "regulatory_context": {
            "environmental_agency": "ABE (Agence Béninoise Environnement)",
            "eie_required": True,
            "eie_threshold": "Projets listés par décret",
            "labor_code": "Code du Travail 1998",
            "minimum_wage": "40,000 FCFA/mois (~60 EUR)",
            "social_security": "CNSS obligatoire",
            "key_regulations": ["Loi-cadre environnement 98-030", "Code du Travail 1998"]
        },
        "climate_risks": {
            "exposure": "Moyen",
            "main_risks": ["Inondations", "Érosion côtière", "Sécheresse Nord"],
            "vulnerable_sectors": ["Agriculture", "Pêche", "Zones côtières"],
            "ndc_target": "Réduction 21.4% d'ici 2030"
        },
        "macro_indicators": {
            "population": "13 millions",
            "gdp_growth_2023": "6.0%",
            "inflation_2023": "3.0%",
            "ease_of_business_rank": 149,
            "currency": "FCFA (XOF)",
            "main_exports": ["Coton", "Noix cajou", "Karité", "Ananas"]
        },
        "gender_context": {
            "women_labor_participation": "68%",
            "gender_gap_index_rank": 145,
            "key_challenges": ["Accès foncier", "Violence basée sur genre"],
            "positive_factors": ["Forte participation économique", "Politique nationale genre"]
        }
    },
    
    "Togo": {
        "region": "Afrique de l'Ouest",
        "ldc": True,
        "fragile": False,
        "iso_code": "TGO",
        "regulatory_context": {
            "environmental_agency": "ANGE",
            "eie_required": True,
            "eie_threshold": "Projets impact significatif",
            "labor_code": "Code du Travail 2006",
            "minimum_wage": "35,000 FCFA/mois (~53 EUR)",
            "social_security": "CNSS obligatoire",
            "key_regulations": ["Loi-cadre environnement 2008-005", "Code du Travail 2006"]
        },
        "climate_risks": {
            "exposure": "Moyen",
            "main_risks": ["Érosion côtière", "Inondations", "Sécheresse Nord"],
            "vulnerable_sectors": ["Agriculture", "Pêche", "Zone côtière Lomé"],
            "ndc_target": "Réduction 31% d'ici 2030"
        },
        "macro_indicators": {
            "population": "8.5 millions",
            "gdp_growth_2023": "5.3%",
            "inflation_2023": "5.1%",
            "ease_of_business_rank": 97,
            "currency": "FCFA (XOF)",
            "main_exports": ["Phosphates", "Coton", "Ciment", "Café/Cacao"]
        },
        "gender_context": {
            "women_labor_participation": "63%",
            "gender_gap_index_rank": 142,
            "key_challenges": ["Accès crédit", "Travail domestique non rémunéré"],
            "positive_factors": ["Forte présence femmes dans commerce"]
        }
    },
    
    "Ghana": {
        "region": "Afrique de l'Ouest",
        "ldc": False,
        "fragile": False,
        "iso_code": "GHA",
        "regulatory_context": {
            "environmental_agency": "EPA (Environmental Protection Agency)",
            "eie_required": True,
            "eie_threshold": "Schedule 1 & 2 EIA Regulations",
            "labor_code": "Labour Act 2003",
            "minimum_wage": "14.88 GHS/jour (~47 EUR/mois)",
            "social_security": "SSNIT obligatoire (18.5%)",
            "key_regulations": ["EIA Regulations 1999", "Labour Act 2003"]
        },
        "climate_risks": {
            "exposure": "Moyen",
            "main_risks": ["Sécheresse Nord", "Inondations", "Élévation niveau mer"],
            "vulnerable_sectors": ["Agriculture", "Hydroélectricité", "Zones côtières"],
            "ndc_target": "Réduction 45% d'ici 2030"
        },
        "macro_indicators": {
            "population": "33 millions",
            "gdp_growth_2023": "2.3%",
            "inflation_2023": "42%",
            "ease_of_business_rank": 118,
            "currency": "Cedi (GHS)",
            "main_exports": ["Or", "Cacao", "Pétrole", "Noix cajou"]
        },
        "gender_context": {
            "women_labor_participation": "60%",
            "gender_gap_index_rank": 108,
            "key_challenges": ["Violence domestique", "Inégalités salariales"],
            "positive_factors": ["Bonne scolarisation filles", "Femmes entrepreneures actives"]
        }
    },
    
    "Guinée": {
        "region": "Afrique de l'Ouest",
        "ldc": True,
        "fragile": True,
        "iso_code": "GIN",
        "regulatory_context": {
            "environmental_agency": "BGEEE",
            "eie_required": True,
            "eie_threshold": "Projets catégorie A et B",
            "labor_code": "Code du Travail 2014",
            "minimum_wage": "440,000 GNF/mois (~40 EUR)",
            "social_security": "CNSS obligatoire",
            "key_regulations": ["Code Environnement 2019", "Code du Travail 2014"]
        },
        "climate_risks": {
            "exposure": "Élevé",
            "main_risks": ["Inondations", "Érosion", "Variabilité pluviométrique"],
            "vulnerable_sectors": ["Agriculture", "Mines", "Infrastructure"],
            "ndc_target": "Réduction 25% d'ici 2030"
        },
        "macro_indicators": {
            "population": "14 millions",
            "gdp_growth_2023": "4.8%",
            "inflation_2023": "8.5%",
            "ease_of_business_rank": 156,
            "currency": "Franc guinéen (GNF)",
            "main_exports": ["Bauxite", "Or", "Diamants", "Alumine"]
        },
        "gender_context": {
            "women_labor_participation": "45%",
            "gender_gap_index_rank": 150,
            "key_challenges": ["Mutilations génitales (97%)", "Mariage précoce"],
            "positive_factors": ["Forte présence commerce informel"]
        },
        "security_context": {
            "risk_level": "Modéré",
            "affected_regions": ["Frontière Sierra Leone/Liberia"],
            "stable_regions": ["Conakry", "Intérieur"],
            "recommendations": ["Suivi contexte politique"]
        }
    },
    
    "Kenya": {
        "region": "Afrique de l'Est",
        "ldc": False,
        "fragile": False,
        "iso_code": "KEN",
        "regulatory_context": {
            "environmental_agency": "NEMA (National Environment Management Authority)",
            "eie_required": True,
            "eie_threshold": "Second Schedule EMCA",
            "labor_code": "Employment Act 2007",
            "minimum_wage": "15,201 KES/mois (~105 EUR)",
            "social_security": "NSSF et NHIF obligatoires",
            "key_regulations": ["EMCA 1999/2015", "Employment Act 2007", "OSHA 2007"]
        },
        "climate_risks": {
            "exposure": "Élevé",
            "main_risks": ["Sécheresses récurrentes", "Inondations", "Glissements terrain"],
            "vulnerable_sectors": ["Agriculture", "Eau", "Énergie hydroélectrique"],
            "ndc_target": "Réduction 32% d'ici 2030"
        },
        "macro_indicators": {
            "population": "54 millions",
            "gdp_growth_2023": "5.0%",
            "inflation_2023": "7.9%",
            "ease_of_business_rank": 56,
            "currency": "Shilling kényan (KES)",
            "main_exports": ["Thé", "Fleurs", "Café", "Légumes", "Vêtements"]
        },
        "gender_context": {
            "women_labor_participation": "72%",
            "gender_gap_index_rank": 57,
            "key_challenges": ["Violence basée sur genre", "Inégalités foncières"],
            "positive_factors": ["Constitution 2010 (règle 2/3)", "Women Enterprise Fund"]
        }
    },
    
    "Ouganda": {
        "region": "Afrique de l'Est",
        "ldc": True,
        "fragile": False,
        "iso_code": "UGA",
        "regulatory_context": {
            "environmental_agency": "NEMA Uganda",
            "eie_required": True,
            "eie_threshold": "Third Schedule NEA",
            "labor_code": "Employment Act 2006",
            "minimum_wage": "Pas de minimum national",
            "social_security": "NSSF (15%)",
            "key_regulations": ["National Environment Act 2019", "Employment Act 2006"]
        },
        "climate_risks": {
            "exposure": "Élevé",
            "main_risks": ["Sécheresse", "Inondations", "Glissements terrain"],
            "vulnerable_sectors": ["Agriculture", "Pêche Lac Victoria", "Énergie hydro"],
            "ndc_target": "Réduction 22% d'ici 2030"
        },
        "macro_indicators": {
            "population": "47 millions",
            "gdp_growth_2023": "5.3%",
            "inflation_2023": "5.4%",
            "ease_of_business_rank": 116,
            "currency": "Shilling ougandais (UGX)",
            "main_exports": ["Café", "Poisson", "Or", "Thé", "Fleurs"]
        },
        "gender_context": {
            "women_labor_participation": "67%",
            "gender_gap_index_rank": 126,
            "key_challenges": ["Droits fonciers", "Violence domestique", "Mariage précoce"],
            "positive_factors": ["Quota parlementaire femmes", "Entrepreneuriat féminin actif"]
        }
    },
    
    "Tanzanie": {
        "region": "Afrique de l'Est",
        "ldc": True,
        "fragile": False,
        "iso_code": "TZA",
        "regulatory_context": {
            "environmental_agency": "NEMC",
            "eie_required": True,
            "eie_threshold": "EMA Schedule",
            "labor_code": "Employment and Labour Relations Act 2004",
            "minimum_wage": "100,000-400,000 TZS/mois selon secteur",
            "social_security": "NSSF/PSSSF obligatoire",
            "key_regulations": ["Environmental Management Act 2004", "Labour Act 2004"]
        },
        "climate_risks": {
            "exposure": "Moyen",
            "main_risks": ["Sécheresse", "Inondations côtières", "Montée des eaux"],
            "vulnerable_sectors": ["Agriculture", "Tourisme", "Pêche"],
            "ndc_target": "Réduction 30-35% d'ici 2030"
        },
        "macro_indicators": {
            "population": "63 millions",
            "gdp_growth_2023": "5.1%",
            "inflation_2023": "4.0%",
            "ease_of_business_rank": 141,
            "currency": "Shilling tanzanien (TZS)",
            "main_exports": ["Or", "Tabac", "Café", "Noix cajou", "Tourisme"]
        },
        "gender_context": {
            "women_labor_participation": "80%",
            "gender_gap_index_rank": 129,
            "key_challenges": ["Violence basée sur genre", "Accès crédit"],
            "positive_factors": ["Forte participation économique", "Politique nationale genre"]
        }
    },
    
    "Rwanda": {
        "region": "Afrique de l'Est",
        "ldc": True,
        "fragile": False,
        "iso_code": "RWA",
        "regulatory_context": {
            "environmental_agency": "REMA",
            "eie_required": True,
            "eie_threshold": "Projets listés Ministerial Order",
            "labor_code": "Labour Law 2018",
            "minimum_wage": "Pas de minimum officiel",
            "social_security": "RSSB obligatoire (8%)",
            "key_regulations": ["Organic Law Environment 2005", "Labour Law 2018"]
        },
        "climate_risks": {
            "exposure": "Moyen",
            "main_risks": ["Inondations", "Glissements terrain", "Sécheresse Est"],
            "vulnerable_sectors": ["Agriculture", "Infrastructure", "Énergie"],
            "ndc_target": "Réduction 38% d'ici 2030"
        },
        "macro_indicators": {
            "population": "14 millions",
            "gdp_growth_2023": "6.2%",
            "inflation_2023": "14.5%",
            "ease_of_business_rank": 38,
            "currency": "Franc rwandais (RWF)",
            "main_exports": ["Café", "Thé", "Minerais", "Tourisme"]
        },
        "gender_context": {
            "women_labor_participation": "84%",
            "gender_gap_index_rank": 6,
            "key_challenges": ["Inégalités économiques persistantes"],
            "positive_factors": ["61% femmes Parlement", "Politique genre très avancée"]
        }
    },
    
    "Éthiopie": {
        "region": "Afrique de l'Est",
        "ldc": True,
        "fragile": True,
        "iso_code": "ETH",
        "regulatory_context": {
            "environmental_agency": "EPA Ethiopia",
            "eie_required": True,
            "eie_threshold": "Directives sectorielles",
            "labor_code": "Labour Proclamation 2019",
            "minimum_wage": "Pas de minimum national",
            "social_security": "Pension publique",
            "key_regulations": ["EIA Proclamation 299/2002", "Labour Proclamation 2019"]
        },
        "climate_risks": {
            "exposure": "Très élevé",
            "main_risks": ["Sécheresse sévère", "Inondations", "Crises alimentaires"],
            "vulnerable_sectors": ["Agriculture (85% emploi)", "Élevage", "Eau"],
            "ndc_target": "Réduction 68.8% d'ici 2030"
        },
        "macro_indicators": {
            "population": "123 millions",
            "gdp_growth_2023": "6.1%",
            "inflation_2023": "30%",
            "ease_of_business_rank": 159,
            "currency": "Birr (ETB)",
            "main_exports": ["Café", "Oléagineux", "Or", "Fleurs"]
        },
        "gender_context": {
            "women_labor_participation": "73%",
            "gender_gap_index_rank": 127,
            "key_challenges": ["Mariage précoce", "Mutilations génitales"],
            "positive_factors": ["Quota 50% cabinet gouvernemental"]
        },
        "security_context": {
            "risk_level": "Élevé",
            "affected_regions": ["Tigré", "Amhara", "Oromia"],
            "stable_regions": ["Addis-Abeba", "Sud"],
            "recommendations": ["Prudence maximale", "Éviter régions en conflit"]
        }
    },
    
    "Cameroun": {
        "region": "Afrique Centrale",
        "ldc": False,
        "fragile": False,
        "iso_code": "CMR",
        "regulatory_context": {
            "environmental_agency": "MINEPDED",
            "eie_required": True,
            "eie_threshold": "Décret 2013/0171",
            "labor_code": "Code du Travail 1992",
            "minimum_wage": "41,875 FCFA/mois (~63 EUR)",
            "social_security": "CNPS obligatoire",
            "key_regulations": ["Loi-cadre environnement 96/12", "Code du Travail 1992"]
        },
        "climate_risks": {
            "exposure": "Moyen",
            "main_risks": ["Inondations", "Sécheresse Nord", "Érosion côtière"],
            "vulnerable_sectors": ["Agriculture", "Forêts", "Zones côtières"],
            "ndc_target": "Réduction 32% d'ici 2030"
        },
        "macro_indicators": {
            "population": "28 millions",
            "gdp_growth_2023": "3.8%",
            "inflation_2023": "6.3%",
            "ease_of_business_rank": 167,
            "currency": "FCFA (XAF)",
            "main_exports": ["Pétrole", "Cacao", "Bois", "Café", "Coton"]
        },
        "gender_context": {
            "women_labor_participation": "71%",
            "gender_gap_index_rank": 141,
            "key_challenges": ["Violence basée sur genre", "Inégalités salariales"],
            "positive_factors": ["Forte présence économique", "Politique nationale genre"]
        },
        "security_context": {
            "risk_level": "Modéré",
            "affected_regions": ["Nord-Ouest", "Sud-Ouest", "Extrême-Nord"],
            "stable_regions": ["Yaoundé", "Douala", "Centre", "Littoral"],
            "recommendations": ["Éviter régions anglophones et Extrême-Nord"]
        }
    },
    
    "RDC (Congo-Kinshasa)": {
        "region": "Afrique Centrale",
        "ldc": True,
        "fragile": True,
        "iso_code": "COD",
        "regulatory_context": {
            "environmental_agency": "ACE",
            "eie_required": True,
            "eie_threshold": "Projets impact significatif",
            "labor_code": "Code du Travail 2002",
            "minimum_wage": "7,075 CDF/jour (~3 EUR/jour)",
            "social_security": "CNSS obligatoire",
            "key_regulations": ["Loi environnement 11/009", "Code du Travail 2002"]
        },
        "climate_risks": {
            "exposure": "Moyen",
            "main_risks": ["Déforestation", "Érosion", "Inondations"],
            "vulnerable_sectors": ["Agriculture", "Forêts", "Mines"],
            "ndc_target": "Réduction 21% d'ici 2030"
        },
        "macro_indicators": {
            "population": "102 millions",
            "gdp_growth_2023": "6.2%",
            "inflation_2023": "19%",
            "ease_of_business_rank": 183,
            "currency": "Franc congolais (CDF)",
            "main_exports": ["Cuivre", "Cobalt", "Or", "Diamants", "Pétrole"]
        },
        "gender_context": {
            "women_labor_participation": "61%",
            "gender_gap_index_rank": 175,
            "key_challenges": ["Violence sexuelle", "Conflits armés"],
            "positive_factors": ["Politique nationale genre"]
        },
        "security_context": {
            "risk_level": "Très élevé",
            "affected_regions": ["Est (Nord-Kivu, Sud-Kivu, Ituri)", "Kasaï"],
            "stable_regions": ["Kinshasa", "Lubumbashi", "Ouest"],
            "recommendations": ["Extrême prudence", "Éviter totalement l'Est"]
        }
    },
    
    "Madagascar": {
        "region": "Afrique Australe",
        "ldc": True,
        "fragile": False,
        "iso_code": "MDG",
        "regulatory_context": {
            "environmental_agency": "ONE",
            "eie_required": True,
            "eie_threshold": "Décret MECIE 99-954",
            "labor_code": "Code du Travail 2003",
            "minimum_wage": "200,000 MGA/mois (~40 EUR)",
            "social_security": "CNaPS obligatoire",
            "key_regulations": ["Charte Environnement 90-033", "Code du Travail 2003"]
        },
        "climate_risks": {
            "exposure": "Très élevé",
            "main_risks": ["Cyclones tropicaux", "Sécheresse Sud", "Inondations"],
            "vulnerable_sectors": ["Agriculture", "Pêche", "Infrastructure côtière"],
            "ndc_target": "Réduction 14% d'ici 2030"
        },
        "macro_indicators": {
            "population": "30 millions",
            "gdp_growth_2023": "4.0%",
            "inflation_2023": "9.8%",
            "ease_of_business_rank": 161,
            "currency": "Ariary (MGA)",
            "main_exports": ["Vanille", "Nickel", "Textile", "Girofle", "Crevettes"]
        },
        "gender_context": {
            "women_labor_participation": "84%",
            "gender_gap_index_rank": 139,
            "key_challenges": ["Pauvreté élevée", "Mariage précoce Sud"],
            "positive_factors": ["Forte participation économique"]
        }
    },
    
    "Mozambique": {
        "region": "Afrique Australe",
        "ldc": True,
        "fragile": True,
        "iso_code": "MOZ",
        "regulatory_context": {
            "environmental_agency": "MITADER",
            "eie_required": True,
            "eie_threshold": "Catégorie A, B, C",
            "labor_code": "Labour Law 2007",
            "minimum_wage": "6,000-15,000 MZN/mois selon secteur",
            "social_security": "INSS obligatoire",
            "key_regulations": ["Lei do Ambiente 1997", "Labour Law 2007"]
        },
        "climate_risks": {
            "exposure": "Très élevé",
            "main_risks": ["Cyclones (Idai, Kenneth)", "Inondations", "Sécheresse Sud"],
            "vulnerable_sectors": ["Agriculture", "Infrastructure", "Zones côtières"],
            "ndc_target": "Réduction 40% d'ici 2030"
        },
        "macro_indicators": {
            "population": "33 millions",
            "gdp_growth_2023": "4.8%",
            "inflation_2023": "7.1%",
            "ease_of_business_rank": 138,
            "currency": "Metical (MZN)",
            "main_exports": ["Aluminium", "Charbon", "Gaz naturel", "Électricité"]
        },
        "gender_context": {
            "women_labor_participation": "80%",
            "gender_gap_index_rank": 134,
            "key_challenges": ["Mariage précoce Nord", "Violence basée sur genre"],
            "positive_factors": ["Forte présence agriculture"]
        },
        "security_context": {
            "risk_level": "Élevé",
            "affected_regions": ["Cabo Delgado"],
            "stable_regions": ["Maputo", "Centre", "Sud"],
            "recommendations": ["Éviter Cabo Delgado"]
        }
    },
    
    "Autre": {
        "region": "Autre",
        "ldc": None,
        "fragile": None,
        "iso_code": None,
        "regulatory_context": None,
        "climate_risks": None,
        "macro_indicators": None,
        "gender_context": None
    }
}


# =============================================================================
# Fonctions utilitaires
# =============================================================================

def get_country_context(country: str) -> str:
    """Retourne une description courte du contexte pays."""
    ctx = IPAE3_COUNTRIES.get(country, {})
    if not ctx or country == "Autre":
        return ""
    
    parts = [ctx.get('region', '')]
    if ctx.get('ldc'):
        parts.append("PMA")
    if ctx.get('fragile'):
        parts.append("État fragile")
    return " - ".join([p for p in parts if p])


def get_country_full_context(country: str) -> dict:
    """Retourne le contexte complet d'un pays."""
    return IPAE3_COUNTRIES.get(country, IPAE3_COUNTRIES.get("Autre", {}))


def get_all_countries() -> list:
    """Retourne la liste de tous les pays."""
    return list(IPAE3_COUNTRIES.keys())


def get_fragile_states() -> list:
    """Retourne la liste des états fragiles."""
    return [name for name, data in IPAE3_COUNTRIES.items() if data.get('fragile')]


def get_ldc_countries() -> list:
    """Retourne la liste des PMA."""
    return [name for name, data in IPAE3_COUNTRIES.items() if data.get('ldc')]


def get_country_for_prompt(country: str) -> str:
    """Génère le texte de contexte pays pour les prompts LLM."""
    ctx = IPAE3_COUNTRIES.get(country, {})
    if not ctx or country == "Autre":
        return f"Pays : {country}"
    
    lines = [f"CONTEXTE PAYS - {country}"]
    lines.append(f"Région : {ctx.get('region', 'N/A')}")
    
    statuses = []
    if ctx.get('ldc'):
        statuses.append("Pays Moins Avancé (PMA)")
    if ctx.get('fragile'):
        statuses.append("État fragile")
    if statuses:
        lines.append(f"Statut : {', '.join(statuses)}")
    
    reg = ctx.get('regulatory_context')
    if reg:
        lines.append("")
        lines.append("RÉGLEMENTATION E&S :")
        lines.append(f"- Agence environnementale : {reg.get('environmental_agency', 'N/A')}")
        lines.append(f"- EIE obligatoire : {'Oui' if reg.get('eie_required') else 'Non'}")
        lines.append(f"- Code du travail : {reg.get('labor_code', 'N/A')}")
        lines.append(f"- Salaire minimum : {reg.get('minimum_wage', 'N/A')}")
    
    climate = ctx.get('climate_risks')
    if climate:
        lines.append("")
        lines.append("RISQUES CLIMAT :")
        lines.append(f"- Exposition : {climate.get('exposure', 'N/A')}")
        lines.append(f"- Risques : {', '.join(climate.get('main_risks', []))}")
    
    gender = ctx.get('gender_context')
    if gender:
        lines.append("")
        lines.append("CONTEXTE GENRE :")
        lines.append(f"- Participation femmes travail : {gender.get('women_labor_participation', 'N/A')}")
        lines.append(f"- Rang Gender Gap : {gender.get('gender_gap_index_rank', 'N/A')}")
    
    security = ctx.get('security_context')
    if security:
        lines.append("")
        lines.append("SÉCURITÉ :")
        lines.append(f"- Risque : {security.get('risk_level', 'N/A')}")
        lines.append(f"- Zones affectées : {', '.join(security.get('affected_regions', []))}")
    
    return "\n".join(lines)
