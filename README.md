# 🌍 ESG & Impact Pre-Investment Analyzer v2.3

Outil d'analyse ESG et impact avec workflow multi-stage pour IPAE3.

## 🚀 Nouveautés V2.3

### Workflow multi-stage complet
```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  SCREENING  │ →  │     DD      │ →  │     IC      │ →  │ MONITORING  │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
     Go/No-Go        Checklist DD      Mémo IC + ESAP     KPIs tracking
```

### Fonctionnalités
- **Screening** : Évaluation rapide, classification E&S, 2X Challenge
- **Due Diligence** : Checklist dynamique, documents, validation
- **Investment Committee** : Génération mémo IC, gestion ESAP
- **Monitoring** : Suivi KPIs, tracker ESAP, historique

### Persistence
- Deals stockés en JSON dans `data/deals/`
- Conservation des données entre sessions
- Export portfolio possible

## 📦 Installation

```bash
pip install -r requirements.txt
cp .env.example .env
# Configurer les clés API
```

## 🚀 Lancement

```bash
streamlit run app.py
```

## 📁 Structure V2.3

```
esg-analyzer/
├── app.py                          # Dashboard principal
├── pages/
│   ├── 1_🔍_Screening.py
│   ├── 2_📋_Due_Diligence.py
│   ├── 3_👥_Investment_Committee.py
│   └── 4_📊_Monitoring.py
├── models/
│   └── deal.py                     # Modèle Deal, Stage, ESAP
├── services/
│   └── deal_storage.py             # Persistence JSON
├── components/
├── config/
├── data/
│   └── deals/                      # Stockage JSON
└── requirements.txt
```

## 📄 License

MIT

**IPAE3** — Fonds d'investissement à impact africain
