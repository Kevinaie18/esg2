"""
Modèle de données pour un deal (opportunité d'investissement).
Gère la persistence et les transitions entre stages du cycle d'investissement IPAE3.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum
import json
import hashlib


class DealStage(Enum):
    """Étapes du cycle d'investissement IPAE3."""
    SCREENING = "screening"
    DUE_DILIGENCE = "due_diligence"
    INVESTMENT_COMMITTEE = "investment_committee"
    MONITORING = "monitoring"
    EXITED = "exited"
    REJECTED = "rejected"


class DealStatus(Enum):
    """Statut du deal à chaque étape."""
    DRAFT = "draft"
    IN_PROGRESS = "in_progress"
    PENDING_REVIEW = "pending_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    ON_HOLD = "on_hold"


@dataclass
class StageData:
    """Données spécifiques à une étape du cycle."""
    stage: DealStage
    status: DealStatus
    started_at: datetime
    completed_at: Optional[datetime] = None
    analyst: Optional[str] = None
    
    # Résultats d'analyse
    analysis_result: Optional[str] = None
    checklist_status: Optional[Dict] = None
    
    # Documents et commentaires
    documents: List[str] = field(default_factory=list)
    comments: List[Dict] = field(default_factory=list)
    
    # Décision
    decision: Optional[str] = None  # GO, NO-GO, GO_WITH_CONDITIONS
    decision_rationale: Optional[str] = None
    conditions: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        return {
            "stage": self.stage.value,
            "status": self.status.value,
            "started_at": self.started_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "analyst": self.analyst,
            "analysis_result": self.analysis_result,
            "checklist_status": self.checklist_status,
            "documents": self.documents,
            "comments": self.comments,
            "decision": self.decision,
            "decision_rationale": self.decision_rationale,
            "conditions": self.conditions
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'StageData':
        return cls(
            stage=DealStage(data["stage"]),
            status=DealStatus(data["status"]),
            started_at=datetime.fromisoformat(data["started_at"]),
            completed_at=datetime.fromisoformat(data["completed_at"]) if data.get("completed_at") else None,
            analyst=data.get("analyst"),
            analysis_result=data.get("analysis_result"),
            checklist_status=data.get("checklist_status"),
            documents=data.get("documents", []),
            comments=data.get("comments", []),
            decision=data.get("decision"),
            decision_rationale=data.get("decision_rationale"),
            conditions=data.get("conditions", [])
        )


@dataclass
class ESAPItem:
    """Environmental and Social Action Plan item."""
    id: str
    category: str  # E&S, Gouvernance, Genre/2X, HSE, Climat
    action: str
    responsible: str
    deadline: Optional[datetime]
    status: str  # not_started, in_progress, completed, overdue
    priority: str  # high, medium, low
    kpi: Optional[str] = None
    progress_notes: List[Dict] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "category": self.category,
            "action": self.action,
            "responsible": self.responsible,
            "deadline": self.deadline.isoformat() if self.deadline else None,
            "status": self.status,
            "priority": self.priority,
            "kpi": self.kpi,
            "progress_notes": self.progress_notes
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'ESAPItem':
        return cls(
            id=data["id"],
            category=data["category"],
            action=data["action"],
            responsible=data["responsible"],
            deadline=datetime.fromisoformat(data["deadline"]) if data.get("deadline") else None,
            status=data["status"],
            priority=data["priority"],
            kpi=data.get("kpi"),
            progress_notes=data.get("progress_notes", [])
        )
    
    def is_overdue(self) -> bool:
        """Vérifie si l'action est en retard."""
        if self.deadline and self.status != "completed":
            return datetime.now() > self.deadline
        return False


@dataclass
class Deal:
    """
    Modèle principal d'un deal/opportunité d'investissement.
    Contient toutes les données à travers les stages du cycle.
    """
    # Identifiants
    id: str
    created_at: datetime
    updated_at: datetime
    
    # Informations entreprise
    company_name: str
    country: str
    sector: str
    subsector: str
    description: str
    
    # Données structurées
    employees: Optional[int] = None
    revenue: Optional[str] = None
    year_founded: Optional[int] = None
    target_market: Optional[str] = None
    geographic_scope: List[str] = field(default_factory=list)
    
    # Classification E&S
    risk_category: str = "B-"
    applicable_standards: List[str] = field(default_factory=list)
    
    # 2X Challenge
    two_x_data: Dict = field(default_factory=dict)
    two_x_eligible: bool = False
    two_x_criteria_met: int = 0
    
    # Stage actuel et historique
    current_stage: DealStage = DealStage.SCREENING
    stage_history: Dict[str, StageData] = field(default_factory=dict)
    
    # Documents uploadés
    uploaded_documents: List[Dict] = field(default_factory=list)
    
    # ESAP (après IC)
    esap_items: List[ESAPItem] = field(default_factory=list)
    
    # Monitoring KPIs
    monitoring_kpis: List[Dict] = field(default_factory=list)
    
    # Métadonnées
    tags: List[str] = field(default_factory=list)
    
    @staticmethod
    def generate_id(company_name: str) -> str:
        """Génère un ID unique basé sur le nom et timestamp."""
        timestamp = datetime.now().isoformat()
        hash_input = f"{company_name}_{timestamp}"
        return hashlib.md5(hash_input.encode()).hexdigest()[:12].upper()
    
    def get_current_stage_data(self) -> Optional[StageData]:
        """Retourne les données du stage actuel."""
        return self.stage_history.get(self.current_stage.value)
    
    def get_stage_data(self, stage: DealStage) -> Optional[StageData]:
        """Retourne les données d'un stage spécifique."""
        return self.stage_history.get(stage.value)
    
    def can_advance_to(self, target_stage: DealStage) -> tuple:
        """
        Vérifie si le deal peut avancer vers un stage donné.
        Retourne (bool, raison).
        """
        stage_order = [
            DealStage.SCREENING,
            DealStage.DUE_DILIGENCE,
            DealStage.INVESTMENT_COMMITTEE,
            DealStage.MONITORING
        ]
        
        # Vérifier si le stage actuel est dans l'ordre
        if self.current_stage not in stage_order:
            return False, f"Stage actuel {self.current_stage.value} ne permet pas d'avancer"
        
        current_idx = stage_order.index(self.current_stage)
        
        # Vérifier si le target est dans l'ordre
        if target_stage not in stage_order:
            return False, f"Stage cible {target_stage.value} invalide"
        
        target_idx = stage_order.index(target_stage)
        
        # Vérifier que c'est bien l'étape suivante
        if target_idx != current_idx + 1:
            return False, f"Impossible de passer de {self.current_stage.value} à {target_stage.value}"
        
        # Vérifier que l'étape actuelle est approuvée
        current_data = self.get_current_stage_data()
        if not current_data:
            return False, f"Données du stage {self.current_stage.value} non trouvées"
        
        if current_data.status != DealStatus.APPROVED:
            return False, f"L'étape {self.current_stage.value} doit être approuvée avant de continuer"
        
        # Vérifications spécifiques par stage
        if target_stage == DealStage.DUE_DILIGENCE:
            if current_data.decision == "NO-GO":
                return False, "Deal rejeté au screening"
        
        if target_stage == DealStage.INVESTMENT_COMMITTEE:
            # Vérifier que la checklist DD a été travaillée
            pass  # Validation optionnelle
        
        return True, "OK"
    
    def advance_stage(self, target_stage: DealStage, analyst: str = None) -> bool:
        """Avance le deal vers le stage suivant."""
        can_advance, reason = self.can_advance_to(target_stage)
        if not can_advance:
            raise ValueError(reason)
        
        # Compléter le stage actuel
        current_data = self.get_current_stage_data()
        if current_data:
            current_data.completed_at = datetime.now()
        
        # Créer le nouveau stage
        new_stage_data = StageData(
            stage=target_stage,
            status=DealStatus.IN_PROGRESS,
            started_at=datetime.now(),
            analyst=analyst
        )
        
        self.stage_history[target_stage.value] = new_stage_data
        self.current_stage = target_stage
        self.updated_at = datetime.now()
        
        return True
    
    def reject(self, rationale: str):
        """Rejette le deal."""
        current_data = self.get_current_stage_data()
        if current_data:
            current_data.decision = "NO-GO"
            current_data.decision_rationale = rationale
            current_data.status = DealStatus.REJECTED
            current_data.completed_at = datetime.now()
        
        self.current_stage = DealStage.REJECTED
        self.updated_at = datetime.now()
    
    def add_comment(self, text: str, author: str = "Analyste"):
        """Ajoute un commentaire au stage actuel."""
        current_data = self.get_current_stage_data()
        if current_data:
            current_data.comments.append({
                "text": text,
                "author": author,
                "timestamp": datetime.now().isoformat()
            })
            self.updated_at = datetime.now()
    
    def add_esap_item(self, item: ESAPItem):
        """Ajoute une action ESAP."""
        self.esap_items.append(item)
        self.updated_at = datetime.now()
    
    def update_esap_status(self, item_id: str, new_status: str, note: str = None):
        """Met à jour le statut d'une action ESAP."""
        for item in self.esap_items:
            if item.id == item_id:
                item.status = new_status
                if note:
                    item.progress_notes.append({
                        "date": datetime.now().isoformat(),
                        "note": note,
                        "status": new_status
                    })
                self.updated_at = datetime.now()
                return True
        return False
    
    def add_kpi_snapshot(self, kpi_data: Dict):
        """Ajoute un snapshot des KPIs."""
        snapshot = {
            "date": datetime.now().isoformat(),
            "data": kpi_data
        }
        self.monitoring_kpis.append(snapshot)
        self.updated_at = datetime.now()
    
    def get_esap_summary(self) -> Dict:
        """Retourne un résumé de l'ESAP."""
        total = len(self.esap_items)
        if total == 0:
            return {"total": 0, "completed": 0, "in_progress": 0, "overdue": 0, "completion_rate": 0}
        
        completed = sum(1 for item in self.esap_items if item.status == "completed")
        in_progress = sum(1 for item in self.esap_items if item.status == "in_progress")
        overdue = sum(1 for item in self.esap_items if item.is_overdue())
        
        return {
            "total": total,
            "completed": completed,
            "in_progress": in_progress,
            "not_started": total - completed - in_progress,
            "overdue": overdue,
            "completion_rate": (completed / total) * 100
        }
    
    def to_dict(self) -> Dict:
        """Sérialise le deal en dictionnaire."""
        return {
            "id": self.id,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "company_name": self.company_name,
            "country": self.country,
            "sector": self.sector,
            "subsector": self.subsector,
            "description": self.description,
            "employees": self.employees,
            "revenue": self.revenue,
            "year_founded": self.year_founded,
            "target_market": self.target_market,
            "geographic_scope": self.geographic_scope,
            "risk_category": self.risk_category,
            "applicable_standards": self.applicable_standards,
            "two_x_data": self.two_x_data,
            "two_x_eligible": self.two_x_eligible,
            "two_x_criteria_met": self.two_x_criteria_met,
            "current_stage": self.current_stage.value,
            "stage_history": {k: v.to_dict() for k, v in self.stage_history.items()},
            "uploaded_documents": self.uploaded_documents,
            "esap_items": [item.to_dict() for item in self.esap_items],
            "monitoring_kpis": self.monitoring_kpis,
            "tags": self.tags
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Deal':
        """Désérialise un deal depuis un dictionnaire."""
        # Reconstruire stage_history
        stage_history = {}
        for stage_name, stage_data in data.get("stage_history", {}).items():
            stage_history[stage_name] = StageData.from_dict(stage_data)
        
        # Reconstruire ESAP items
        esap_items = [ESAPItem.from_dict(item) for item in data.get("esap_items", [])]
        
        return cls(
            id=data["id"],
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
            company_name=data["company_name"],
            country=data["country"],
            sector=data["sector"],
            subsector=data["subsector"],
            description=data["description"],
            employees=data.get("employees"),
            revenue=data.get("revenue"),
            year_founded=data.get("year_founded"),
            target_market=data.get("target_market"),
            geographic_scope=data.get("geographic_scope", []),
            risk_category=data.get("risk_category", "B-"),
            applicable_standards=data.get("applicable_standards", []),
            two_x_data=data.get("two_x_data", {}),
            two_x_eligible=data.get("two_x_eligible", False),
            two_x_criteria_met=data.get("two_x_criteria_met", 0),
            current_stage=DealStage(data["current_stage"]),
            stage_history=stage_history,
            uploaded_documents=data.get("uploaded_documents", []),
            esap_items=esap_items,
            monitoring_kpis=data.get("monitoring_kpis", []),
            tags=data.get("tags", [])
        )
    
    def to_json(self) -> str:
        """Sérialise en JSON."""
        return json.dumps(self.to_dict(), indent=2, ensure_ascii=False)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'Deal':
        """Désérialise depuis JSON."""
        return cls.from_dict(json.loads(json_str))
