"""
ESG & Impact Pre-Investment Analyzer
Version 2.3 - Multi-Stage Workflow

Application principale - Dashboard du portfolio et navigation.
"""

import os
import streamlit as st
from dotenv import load_dotenv
import pandas as pd

from models.deal import Deal, DealStage, DealStatus
from services.deal_storage import get_deal_storage

load_dotenv()

st.set_page_config(
    page_title="ESG Analyzer - IPAE3",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize Storage
storage = get_deal_storage()

# Header
st.title("🌍 ESG & Impact Pre-Investment Analyzer")
st.markdown("**Version 2.3** — Workflow multi-stage pour IPAE3")

st.markdown("---")

# Dashboard Stats
stats = storage.get_statistics()

st.header("📊 Dashboard Portfolio")

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric("Total deals", stats['total'])
with col2:
    st.metric("En screening", stats['by_stage'].get('screening', 0))
with col3:
    st.metric("En DD", stats['by_stage'].get('due_diligence', 0))
with col4:
    st.metric("En monitoring", stats['by_stage'].get('monitoring', 0))
with col5:
    st.metric("Taux 2X", f"{stats['two_x_rate']:.0f}%")

st.markdown("---")

# Pipeline Visuel
st.header("🔄 Pipeline d'investissement")

col1, col2, col3, col4 = st.columns(4)

stages_config = [
    (col1, "🔍 Screening", DealStage.SCREENING, "#e3f2fd"),
    (col2, "📋 Due Diligence", DealStage.DUE_DILIGENCE, "#fff3e0"),
    (col3, "👥 Comité Invest.", DealStage.INVESTMENT_COMMITTEE, "#f3e5f5"),
    (col4, "📊 Monitoring", DealStage.MONITORING, "#e8f5e9"),
]

for col, title, stage, color in stages_config:
    with col:
        count = stats['by_stage'].get(stage.value, 0)
        
        st.markdown(f"""
        <div style="background-color: {color}; padding: 15px; border-radius: 10px; min-height: 150px;">
            <h4>{title}</h4>
            <h2>{count}</h2>
            <p style="color: #666;">deal(s)</p>
        </div>
        """, unsafe_allow_html=True)
        
        deals = storage.get_by_stage(stage)
        if deals:
            for deal in deals[:3]:
                st.caption(f"• {deal.company_name}")
            if len(deals) > 3:
                st.caption(f"... +{len(deals) - 3}")

st.markdown("---")

# Répartition
col1, col2 = st.columns(2)

with col1:
    st.markdown("### 📈 Par secteur")
    if stats['by_sector']:
        sector_df = pd.DataFrame([{"Secteur": k, "Deals": v} for k, v in stats['by_sector'].items()])
        st.bar_chart(sector_df.set_index("Secteur"))
    else:
        st.info("Aucun deal")

with col2:
    st.markdown("### 🌍 Par pays")
    if stats['by_country']:
        country_df = pd.DataFrame([{"Pays": k, "Deals": v} for k, v in stats['by_country'].items()])
        st.bar_chart(country_df.set_index("Pays"))
    else:
        st.info("Aucun deal")

st.markdown("---")

# Deals récents
st.header("🕐 Activité récente")

recent_deals = storage.get_recent_deals(limit=5)

if recent_deals:
    for deal in recent_deals:
        stage_icon = {"screening": "🔍", "due_diligence": "📋", "investment_committee": "👥", "monitoring": "📊", "rejected": "❌"}.get(deal.current_stage.value, "❓")
        
        col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
        with col1:
            st.markdown(f"**{deal.company_name}** — {deal.country}")
        with col2:
            st.markdown(f"{stage_icon} {deal.current_stage.value.replace('_', ' ').title()}")
        with col3:
            st.markdown(f"{'✅' if deal.two_x_eligible else '❌'} 2X")
        with col4:
            st.caption(f"Màj: {deal.updated_at.strftime('%d/%m %H:%M')}")
else:
    st.info("Aucun deal. Commencez par créer un deal dans Screening.")

st.markdown("---")

# Actions rapides
st.header("🚀 Actions rapides")

col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("➕ Nouveau screening", use_container_width=True, type="primary"):
        st.switch_page("pages/1_Screening.py")
with col2:
    if st.button("📋 Due Diligence", use_container_width=True):
        st.switch_page("pages/2_Due_Diligence.py")
with col3:
    if st.button("👥 Comité Invest.", use_container_width=True):
        st.switch_page("pages/3_Investment_Committee.py")
with col4:
    if st.button("📊 Monitoring", use_container_width=True):
        st.switch_page("pages/4_Monitoring.py")

# Sidebar
with st.sidebar:
    st.header("ℹ️ À propos")
    st.markdown("""
    **ESG Analyzer v2.3**
    
    Workflow multi-stage :
    1. 🔍 Screening
    2. 📋 Due Diligence
    3. 👥 Investment Committee
    4. 📊 Monitoring
    """)
    st.markdown("---")
    st.metric("Total deals", stats['total'])
    st.metric("Taux 2X", f"{stats['two_x_rate']:.0f}%")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 20px;">
    <p><strong>ESG Analyzer v2.3</strong> | IPAE3</p>
</div>
""", unsafe_allow_html=True)
