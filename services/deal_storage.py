"""
Service de stockage des deals avec persistence fichiers JSON.
Utilise Streamlit session_state comme cache et fichiers JSON pour persistence.
"""

import json
from pathlib import Path
from typing import List, Optional, Dict
from datetime import datetime
import streamlit as st
from loguru import logger

from models.deal import Deal, DealStage, DealStatus


class DealStorage:
    """
    Service de stockage des deals.
    - Cache en mémoire via session_state
    - Persistence via fichiers JSON
    """
    
    STORAGE_DIR = Path("data/deals")
    
    def __init__(self):
        """Initialise le stockage."""
        # Créer le répertoire si nécessaire
        self.STORAGE_DIR.mkdir(parents=True, exist_ok=True)
        
        # Initialiser le cache session
        if 'deals_cache' not in st.session_state:
            st.session_state.deals_cache = {}
            self._load_all_deals()
    
    def _load_all_deals(self):
        """Charge tous les deals depuis les fichiers JSON."""
        loaded = 0
        errors = 0
        
        for filepath in self.STORAGE_DIR.glob("*.json"):
            try:
                content = filepath.read_text(encoding='utf-8')
                data = json.loads(content)
                deal = Deal.from_dict(data)
                st.session_state.deals_cache[deal.id] = deal
                loaded += 1
            except Exception as e:
                logger.error(f"Error loading deal from {filepath}: {e}")
                errors += 1
        
        if loaded > 0 or errors > 0:
            logger.info(f"Loaded {loaded} deals, {errors} errors")
    
    def save(self, deal: Deal) -> bool:
        """
        Sauvegarde un deal.
        Met à jour le cache et écrit sur disque.
        """
        try:
            # Mettre à jour le timestamp
            deal.updated_at = datetime.now()
            
            # Mettre à jour le cache
            st.session_state.deals_cache[deal.id] = deal
            
            # Sauvegarder sur disque
            filepath = self.STORAGE_DIR / f"{deal.id}.json"
            filepath.write_text(deal.to_json(), encoding='utf-8')
            
            logger.debug(f"Deal {deal.id} ({deal.company_name}) saved successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error saving deal {deal.id}: {e}")
            return False
    
    def get(self, deal_id: str) -> Optional[Deal]:
        """Récupère un deal par son ID."""
        return st.session_state.deals_cache.get(deal_id)
    
    def get_all(self) -> List[Deal]:
        """Récupère tous les deals."""
        return list(st.session_state.deals_cache.values())
    
    def get_by_stage(self, stage: DealStage) -> List[Deal]:
        """Récupère les deals à un stage donné."""
        return [d for d in self.get_all() if d.current_stage == stage]
    
    def get_by_status(self, stage: DealStage, status: DealStatus) -> List[Deal]:
        """Récupère les deals à un stage et statut donnés."""
        deals = self.get_by_stage(stage)
        return [d for d in deals if d.get_current_stage_data() and d.get_current_stage_data().status == status]
    
    def get_active_deals(self) -> List[Deal]:
        """Récupère les deals actifs (non rejetés, non sortis)."""
        excluded = [DealStage.REJECTED, DealStage.EXITED]
        return [d for d in self.get_all() if d.current_stage not in excluded]
    
    def delete(self, deal_id: str) -> bool:
        """Supprime un deal."""
        try:
            # Supprimer du cache
            if deal_id in st.session_state.deals_cache:
                del st.session_state.deals_cache[deal_id]
            
            # Supprimer le fichier
            filepath = self.STORAGE_DIR / f"{deal_id}.json"
            if filepath.exists():
                filepath.unlink()
            
            logger.info(f"Deal {deal_id} deleted")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting deal {deal_id}: {e}")
            return False
    
    def search(self, query: str) -> List[Deal]:
        """Recherche des deals par nom d'entreprise ou pays."""
        query_lower = query.lower()
        results = []
        
        for deal in self.get_all():
            if (query_lower in deal.company_name.lower() or 
                query_lower in deal.country.lower() or
                query_lower in deal.sector.lower()):
                results.append(deal)
        
        return results
    
    def get_statistics(self) -> Dict:
        """Retourne des statistiques sur le portfolio."""
        deals = self.get_all()
        
        # Par stage
        by_stage = {}
        for stage in DealStage:
            by_stage[stage.value] = len([d for d in deals if d.current_stage == stage])
        
        # Par secteur
        by_sector = {}
        for deal in deals:
            by_sector[deal.sector] = by_sector.get(deal.sector, 0) + 1
        
        # Par pays
        by_country = {}
        for deal in deals:
            by_country[deal.country] = by_country.get(deal.country, 0) + 1
        
        # 2X Challenge
        active_deals = self.get_active_deals()
        two_x_eligible = len([d for d in active_deals if d.two_x_eligible])
        
        # ESAP (pour deals en monitoring)
        monitoring_deals = self.get_by_stage(DealStage.MONITORING)
        total_esap_items = sum(len(d.esap_items) for d in monitoring_deals)
        completed_esap = sum(
            sum(1 for item in d.esap_items if item.status == "completed")
            for d in monitoring_deals
        )
        
        return {
            "total": len(deals),
            "active": len(active_deals),
            "by_stage": by_stage,
            "by_sector": by_sector,
            "by_country": by_country,
            "two_x_eligible": two_x_eligible,
            "two_x_rate": (two_x_eligible / len(active_deals) * 100) if active_deals else 0,
            "esap_total": total_esap_items,
            "esap_completed": completed_esap,
            "esap_completion_rate": (completed_esap / total_esap_items * 100) if total_esap_items > 0 else 0
        }
    
    def get_recent_deals(self, limit: int = 10) -> List[Deal]:
        """Récupère les deals les plus récents."""
        deals = self.get_all()
        deals.sort(key=lambda d: d.updated_at, reverse=True)
        return deals[:limit]
    
    def export_portfolio(self) -> Dict:
        """Exporte tout le portfolio pour backup."""
        return {
            "exported_at": datetime.now().isoformat(),
            "deals": [deal.to_dict() for deal in self.get_all()]
        }


# Singleton pattern
_storage_instance = None


def get_deal_storage() -> DealStorage:
    """Retourne l'instance singleton du storage."""
    global _storage_instance
    if _storage_instance is None:
        _storage_instance = DealStorage()
    return _storage_instance


def reset_storage():
    """Reset le storage (pour tests)."""
    global _storage_instance
    _storage_instance = None
    if 'deals_cache' in st.session_state:
        del st.session_state.deals_cache
