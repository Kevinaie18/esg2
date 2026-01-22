"""
Page Monitoring - Suivi post-investissement des KPIs ESG et ESAP.
"""
import streamlit as st
from datetime import datetime
import pandas as pd

from models.deal import Deal, DealStage, DealStatus
from services.deal_storage import get_deal_storage
from config.two_x_challenge import calculate_2x_eligibility

st.set_page_config(
    page_title="Monitoring - ESG Analyzer",
    page_icon="📊",
    layout="wide"
)

# Initialiser le storage
storage = get_deal_storage()

# Header
st.title("📊 Monitoring Portfolio")
st.markdown("Suivi post-investissement des KPIs ESG et ESAP")

st.markdown("---")

# Stats globales
stats = storage.get_statistics()

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric("Total deals", stats['total'])
with col2:
    st.metric("Deals actifs", stats['active'])
with col3:
    st.metric("En monitoring", stats['by_stage'].get('monitoring', 0))
with col4:
    st.metric("Taux 2X", f"{stats['two_x_rate']:.0f}%")
with col5:
    st.metric("ESAP complétés", f"{stats['esap_completion_rate']:.0f}%")

st.markdown("---")

# Deals IC approuvés prêts pour monitoring
ic_approved = storage.get_by_status(DealStage.INVESTMENT_COMMITTEE, DealStatus.APPROVED)

if ic_approved:
    st.info(f"🚀 **{len(ic_approved)} deal(s)** approuvé(s) par le IC, prêts pour le monitoring")
    
    with st.expander("Activer le monitoring"):
        for deal in ic_approved:
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"**{deal.company_name}** — {deal.country} — {deal.sector}")
            with col2:
                if st.button(f"▶️ Activer", key=f"activate_{deal.id}"):
                    try:
                        deal.advance_stage(DealStage.MONITORING)
                        storage.save(deal)
                        st.success(f"Monitoring activé pour {deal.company_name}")
                        st.rerun()
                    except ValueError as e:
                        st.error(f"Erreur : {e}")
    st.markdown("---")

# Deals en monitoring
monitoring_deals = storage.get_by_stage(DealStage.MONITORING)

if not monitoring_deals:
    st.warning("📭 Aucun deal en monitoring actuellement.")
    st.info("💡 Les deals doivent être approuvés par le Comité d'Investissement pour passer en monitoring.")
    st.stop()

# Tabs
tab1, tab2, tab3 = st.tabs(["📊 Vue portfolio", "📋 ESAP Tracker", "📈 KPIs"])

# TAB 1: Vue portfolio
with tab1:
    st.subheader("Portfolio en monitoring")
    
    data = []
    for deal in monitoring_deals:
        esap_summary = deal.get_esap_summary()
        data.append({
            "Entreprise": deal.company_name,
            "Pays": deal.country,
            "Secteur": deal.sector,
            "Risque": deal.risk_category,
            "2X": "✅" if deal.two_x_eligible else "❌",
            "ESAP": f"{esap_summary['completed']}/{esap_summary['total']}",
            "% ESAP": esap_summary['completion_rate'],
            "En retard": esap_summary['overdue']
        })
    
    df = pd.DataFrame(data)
    st.dataframe(df, use_container_width=True, hide_index=True)
    
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Par secteur**")
        sector_counts = df['Secteur'].value_counts()
        st.bar_chart(sector_counts)
    with col2:
        st.markdown("**Par pays**")
        country_counts = df['Pays'].value_counts()
        st.bar_chart(country_counts)

# TAB 2: ESAP Tracker
with tab2:
    st.subheader("Suivi ESAP")
    
    selected_deal_id = st.selectbox(
        "Sélectionner un deal",
        options=[d.id for d in monitoring_deals],
        format_func=lambda x: f"{storage.get(x).company_name}",
        key="esap_tracker_deal"
    )
    
    deal = storage.get(selected_deal_id)
    
    if deal:
        st.markdown(f"### 📋 ESAP - {deal.company_name}")
        
        esap_summary = deal.get_esap_summary()
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total actions", esap_summary['total'])
        with col2:
            st.metric("Complétées", esap_summary['completed'])
        with col3:
            st.metric("En cours", esap_summary['in_progress'])
        with col4:
            st.metric("En retard", esap_summary['overdue'])
        
        if esap_summary['total'] > 0:
            st.progress(esap_summary['completion_rate'] / 100)
        
        st.markdown("---")
        
        if deal.esap_items:
            for item in deal.esap_items:
                priority_icon = {"high": "🔴", "medium": "🟠", "low": "🟢"}[item.priority]
                is_overdue = item.is_overdue()
                
                col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
                
                with col1:
                    st.markdown(f"{priority_icon} **{item.action}**")
                    st.caption(f"Responsable: {item.responsible}")
                
                with col2:
                    if item.deadline:
                        days_left = (item.deadline - datetime.now()).days
                        color = "🔴" if days_left < 0 else ("🟠" if days_left < 30 else "🟢")
                        st.markdown(f"{color} **{days_left}j**")
                
                with col3:
                    new_status = st.selectbox(
                        "Statut",
                        ["not_started", "in_progress", "completed"],
                        index=["not_started", "in_progress", "completed"].index(item.status),
                        key=f"esap_status_{deal.id}_{item.id}",
                        format_func=lambda x: {"not_started": "À faire", "in_progress": "En cours", "completed": "Terminé"}[x],
                        label_visibility="collapsed"
                    )
                    if new_status != item.status:
                        item.status = new_status
                        storage.save(deal)
                        st.rerun()
                
                st.markdown("---")
        else:
            st.info("Aucune action ESAP pour ce deal.")

# TAB 3: KPIs
with tab3:
    st.subheader("KPIs ESG & Impact")
    
    selected_deal_id = st.selectbox(
        "Sélectionner un deal",
        options=[d.id for d in monitoring_deals],
        format_func=lambda x: f"{storage.get(x).company_name}",
        key="kpi_deal"
    )
    
    deal = storage.get(selected_deal_id)
    
    if deal:
        st.markdown(f"### 📈 KPIs - {deal.company_name}")
        st.markdown("#### 🎯 Indicateurs 2X Challenge")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            new_ownership = st.number_input(
                "% Détention femmes", 0, 100,
                int(deal.two_x_data.get('women_ownership_pct', 0)),
                key="kpi_ownership"
            )
        with col2:
            new_management = st.number_input(
                "% Management femmes", 0, 100,
                int(deal.two_x_data.get('women_management_pct', 0)),
                key="kpi_management"
            )
        with col3:
            new_employees = st.number_input(
                "% Employées femmes", 0, 100,
                int(deal.two_x_data.get('women_employees_pct', 0)),
                key="kpi_employees"
            )
        with col4:
            total_employees = st.number_input(
                "Total employés", 1, 100000,
                deal.employees or 50,
                key="kpi_total_emp"
            )
        
        if st.button("📊 Mettre à jour les KPIs", type="primary"):
            deal.two_x_data['women_ownership_pct'] = new_ownership
            deal.two_x_data['women_management_pct'] = new_management
            deal.two_x_data['women_employees_pct'] = new_employees
            deal.employees = total_employees
            
            result = calculate_2x_eligibility(deal.two_x_data, deal.sector)
            deal.two_x_eligible = result['eligible']
            deal.two_x_criteria_met = result['criteria_met']
            
            deal.add_kpi_snapshot({
                "women_ownership_pct": new_ownership,
                "women_management_pct": new_management,
                "women_employees_pct": new_employees,
                "total_employees": total_employees,
                "two_x_eligible": deal.two_x_eligible
            })
            
            storage.save(deal)
            st.success("✅ KPIs mis à jour !")
            st.rerun()
        
        st.markdown("---")
        if deal.two_x_eligible:
            st.success(f"✅ **Éligible 2X Challenge** ({deal.two_x_criteria_met}/4 critères)")
        else:
            st.warning(f"❌ **Non éligible 2X** ({deal.two_x_criteria_met}/4 critères)")
        
        st.markdown("---")
        st.markdown("#### 📜 Historique des KPIs")
        
        if deal.monitoring_kpis:
            hist_data = []
            for kpi in deal.monitoring_kpis:
                hist_data.append({
                    "Date": kpi['date'][:10],
                    "% Ownership": kpi['data'].get('women_ownership_pct', 0),
                    "% Management": kpi['data'].get('women_management_pct', 0),
                    "% Employées": kpi['data'].get('women_employees_pct', 0),
                    "2X": "✅" if kpi['data'].get('two_x_eligible') else "❌"
                })
            st.dataframe(pd.DataFrame(hist_data), use_container_width=True, hide_index=True)
        else:
            st.info("Aucun historique de KPIs.")

# Footer
st.markdown("---")
st.caption("ESG Analyzer v2.3 | Monitoring Portfolio")
