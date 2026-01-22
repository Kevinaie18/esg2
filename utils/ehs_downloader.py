"""
Télécharge les guidelines IFC-EHS depuis GitHub Releases au premier lancement.
"""
import os
import requests
from pathlib import Path
from loguru import logger

RELEASE_BASE_URL = "https://github.com/Kevinaie18/esg-analyzer/releases/download/v1.0-data/"

EHS_FILES = [
    "2007-airlines-ehs-guidelines-en.pdf",
    "2007-airports-ehs-guidelines-en.pdf",
    "2007-aquaculture-ehs-guidelines-en.pdf",
    "2007-board-and-particle-based-products-ehs-guidelines-en.pdf",
    "2007-breweries-ehs-guidelines-en.pdf",
    "2007-ceramic-tile-sanitary-ware-ehs-guidelines-en.pdf",
    "2007-coal-processing-ehs-guidelines-en.pdf",
    "2007-construction-materials-extraction-ehs-guidelines-en.pdf",
    "2007-crude-petroleum-products-terminals-ehs-guidelines-en.pdf",
    "2007-dairy-processing-ehs-guidelines-en.pdf",
    "2007-electric-transmission-distribution-ehs-guidelines-en.pdf",
    "2007-fish-processing-ehs-guidelines-en.pdf",
    "2007-food-and-beverage-processing-ehs-guidelines-en.pdf",
    "2007-forest-harvesting-operations-ehs-guidelines-en.pdf",
    "2007-foundries-ehs-guidelines-en.pdf",
    "2007-gas-distribution-systems-ehs-guidelines-en.pdf",
    "2007-geothermal-power-generation-ehs-guidelines-en.pdf",
    "2007-glass-manufacturing-ehs-guidelines-en.pdf",
    "2007-health-care-facilities-ehs-guidelines-en.pdf",
    "2007-integrated-steel-mills-ehs-guidelines-en.pdf",
    "2007-large-vol-inorganic-compounds-coaltar-ehs-guidelines-en.pdf",
    "2007-large-vol-petro-organic-chemcials-ehs-guidelines-en.pdf",
    "2007-mammalian-livestock-production-ehs-guidelines-en.pdf",
    "2007-meat-processing-ehs-guidelines-en.pdf",
    "2007-metal-plastic-rubber-products-ehs-guidelines-en.pdf",
    "2007-metal-smelting-refining-ehs-guidelines-en.pdf",
    "2007-mining-ehs-guidelines-en.pdf",
    "2007-natural-gas-processing-ehs-guidelines-en.pdf",
    "2007-nitrogenous-fertilizers-ehs-guidelines-en.pdf",
    "2007-oleochemicals-manufacturing-ehs-guidelines-en.pdf",
    "2007-onshore-oil-gas-development-ehs-guidelines-en.pdf",
    "2007-pesticides-ehs-guidelines-en.pdf",
    "2007-petroleum-polymers-ehs-guidelines-en.pdf",
    "2007-pharma-biotech-ehs-guidelines-en.pdf",
    "2007-phosphate-fertilizer-ehs-guidelines-en.pdf",
    "2007-poultry-processing-ehs-guidelines-en.pdf",
    "2007-poultry-production-ehs-guidelines-en.pdf",
    "2007-printing-ehs-guidelines-en.pdf",
    "2007-pulp-and-paper-mills-ehs-guidelines-en.pdf",
    "2007-railways-ehs-guidelines-en.pdf",
    "2007-retail-petroleum-networks-ehs-guidelines-en.pdf",
    "2007-sawmilling-wood-products-ehs-guidelines-en.pdf",
    "2007-semiconductors-electronic-ehs-guidelines-en.pdf",
    "2007-shipping-ehs-guidelines-en.pdf",
    "2007-sugar-manufacturing-ehs-guidelines-en.pdf",
    "2007-tanning-leather-finishing-ehs-guidelines-en.pdf",
    "2007-telecommunications-ehs-guidelines-en.pdf",
    "2007-textiles-manufacturing-ehs-guidelines-en.pdf",
    "2007-toll-roads-ehs-guidelines-en.pdf",
    "2007-tourism-hospitality-development-ehs-guidelines-en.pdf",
    "2007-waste-management-facilities-ehs-guidelines-en.pdf",
    "2007-water-and-sanitation-ehs-guidelines-en.pdf",
    "2008-thermal-power-ehs-guidelines-en.pdf",
    "2015-offshore-oil-gas-development-ehs-guidelines-en.pdf",
    "2015-vegetable-oil-processing-ehs-guidelines-en.pdf",
    "2015-wind-energy-ehs-guidelines-en.pdf",
    "2016-annual-crop-production-ehs-guidelines-en.pdf",
    "2016-perennial-crop-production-ehs-guidelines-en.pdf",
    "2016-petroleum-refining-ehs-guidelines-en.pdf",
    "2017-lng-ehs-guidelines-en.pdf",
    "2017-ports-harbors-terminals-ehs-guidelines-en.pdf",
    "2022-cement-lime-manufacturing-ehs-guidelines-en.pdf",
]


def ensure_ehs_files(target_dir: str = "ifc-ehs") -> bool:
    """
    Vérifie et télécharge les PDFs manquants.
    Retourne True si tous les fichiers sont disponibles.
    """
    target_path = Path(target_dir)
    target_path.mkdir(exist_ok=True)
    
    # Vérifier les fichiers manquants
    missing = []
    for filename in EHS_FILES:
        if not (target_path / filename).exists():
            missing.append(filename)
    
    if not missing:
        logger.info("✅ Tous les fichiers IFC-EHS sont présents.")
        return True
    
    logger.info(f"📥 Téléchargement de {len(missing)} fichiers IFC-EHS...")
    
    success_count = 0
    for i, filename in enumerate(missing, 1):
        url = f"{RELEASE_BASE_URL}{filename}"
        filepath = target_path / filename
        
        try:
            logger.info(f"[{i}/{len(missing)}] Téléchargement de {filename}...")
            response = requests.get(url, timeout=60)
            response.raise_for_status()
            filepath.write_bytes(response.content)
            success_count += 1
            logger.info(f"✓ {filename}")
        except requests.exceptions.RequestException as e:
            logger.error(f"✗ {filename}: {e}")
    
    if success_count == len(missing):
        logger.info(f"✅ {success_count} fichiers téléchargés avec succès.")
        return True
    else:
        logger.warning(f"⚠️ {success_count}/{len(missing)} fichiers téléchargés.")
        return False


def get_ehs_file_for_sector(sector: str) -> list:
    """
    Retourne la liste des fichiers EHS pertinents pour un secteur donné.
    """
    sector_mapping = {
        "Agribusiness": [
            "2007-food-and-beverage-processing-ehs-guidelines-en.pdf",
            "2016-annual-crop-production-ehs-guidelines-en.pdf",
            "2007-mammalian-livestock-production-ehs-guidelines-en.pdf",
            "2007-poultry-production-ehs-guidelines-en.pdf",
            "2007-aquaculture-ehs-guidelines-en.pdf",
            "2007-dairy-processing-ehs-guidelines-en.pdf",
            "2007-meat-processing-ehs-guidelines-en.pdf",
            "2007-sugar-manufacturing-ehs-guidelines-en.pdf",
            "2015-vegetable-oil-processing-ehs-guidelines-en.pdf",
        ],
        "Industrie & Manufacturing": [
            "2007-textiles-manufacturing-ehs-guidelines-en.pdf",
            "2022-cement-lime-manufacturing-ehs-guidelines-en.pdf",
            "2007-glass-manufacturing-ehs-guidelines-en.pdf",
            "2007-metal-plastic-rubber-products-ehs-guidelines-en.pdf",
            "2007-sawmilling-wood-products-ehs-guidelines-en.pdf",
            "2007-printing-ehs-guidelines-en.pdf",
        ],
        "Santé": [
            "2007-health-care-facilities-ehs-guidelines-en.pdf",
            "2007-pharma-biotech-ehs-guidelines-en.pdf",
        ],
        "Énergie": [
            "2015-wind-energy-ehs-guidelines-en.pdf",
            "2008-thermal-power-ehs-guidelines-en.pdf",
            "2007-electric-transmission-distribution-ehs-guidelines-en.pdf",
            "2007-geothermal-power-generation-ehs-guidelines-en.pdf",
        ],
        "Tourisme & Hôtellerie": [
            "2007-tourism-hospitality-development-ehs-guidelines-en.pdf",
        ],
        "Tech & Digital": [
            "2007-telecommunications-ehs-guidelines-en.pdf",
            "2007-semiconductors-electronic-ehs-guidelines-en.pdf",
        ],
        "Distribution & Retail": [
            "2007-railways-ehs-guidelines-en.pdf",
            "2007-toll-roads-ehs-guidelines-en.pdf",
        ],
    }
    
    return sector_mapping.get(sector, [])


if __name__ == "__main__":
    # Test du téléchargement
    ensure_ehs_files()
