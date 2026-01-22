"""
Page Monitoring - Suivi post-investissement avec rapports IA.
"""
import streamlit as st
from datetime import datetime
import pandas as pd

from models.deal import Deal, DealStage, DealStatus
from services.deal_storage import get_deal_storage
from config.two_x_challenge import calculate_2x_eligibility
from engine.llm_service import get_llm_manager, ProviderType
from prompts.monitoring_prompts import (
    MONITORING_SYSTEM_PROMPT, 
    format_monitoring_report_prompt,
    format_esap_recommendations_prompt
)

st.set_page_config(page_title="Monitoring - ESG Analyzer", page_icon="📊", layout="wide")

storage = get_deal_storage()

st.title("📊 Monitoring Portfolio")
st.markdown("Suivi post-investissement et rapports IA")
st.markdown("---")

# Stats globales
stats = storage.get_statistics()

col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    st.metric("Total deals", stats['total'])
with col2:
    st.metric("Actifs", stats['active'])
with col3:
    st.metric("Monitoring", stats['by_stage'].get('monitoring', 0))
with col4:
    st.metric("Taux 2X", f"{stats['two_x_rate']:.0f}%")
with col5:
    st.metric("ESAP", f"{stats['esap_completion_rate']:.0f}%")

st.markdown("---")

# Deals IC approuvés
ic_approved = storage.get_by_status(DealStage.INVESTMENT_COMMITTEE, DealStatus.APPROVED)
if ic_approved:
    st.info(f"🚀 **{len(ic_approved)} deal(s)** prêts pour monitoring")
    with st.expander("Activer"):
        for deal in ic_approved:
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"**{deal.company_name}**")
            with col2:
                if st.button(f"▶️", key=f"act_{deal.id}"):
                    deal.advance_stage(DealStage.MONITORING)
                    storage.save(deal)
                    st.rerun()
    st.markdown("---")

# Deals en monitoring
monitoring_deals = storage.get_by_stage(DealStage.MONITORING)

if not monitoring_deals:
    st.warning("📭 Aucun deal en monitoring.")
    st.stop()

# Sélection LLM
col1, col2 = st.columns([3, 1])
with col2:
    llm_provider = st.selectbox(
        "Fournisseur IA",
        ["anthropic", "openai", "deepseek"],
        format_func=lambda x: {"anthropic": "Claude", "openai": "GPT-4", "deepseek": "DeepSeek"}[x]
    )

tab1, tab2, tab3, tab4 = st.tabs(["📊 Portfolio", "📋 ESAP", "📈 KPIs", "🤖 Rapports IA"])

# =============================================================================
# TAB 1: Portfolio
# =============================================================================
with tab1:
    st.subheader("Portfolio en monitoring")
    
    data = []
    for deal in monitoring_deals:
        esap = deal.get_esap_summary()
        data.append({
            "Entreprise": deal.company_name,
            "Pays": deal.country,
            "Secteur": deal.sector,
            "2X": "✅" if deal.two_x_eligible else "❌",
            "ESAP": f"{esap['completed']}/{esap['total']}",
            "% ESAP": esap['completion_rate'],
            "Retard": esap['overdue']
        })
    
    df = pd.DataFrame(data)
    st.dataframe(df, use_container_width=True, hide_index=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Par secteur**")
        st.bar_chart(df['Secteur'].value_counts())
    with col2:
        st.markdown("**Par pays**")
        st.bar_chart(df['Pays'].value_counts())

# =============================================================================
# TAB 2: ESAP
# =============================================================================
with tab2:
    st.subheader("Suivi ESAP")
    
    selected_id = st.selectbox("Deal", options=[d.id for d in monitoring_deals], format_func=lambda x: storage.get(x).company_name, key="esap_deal")
    deal = storage.get(selected_id)
    
    if deal:
        esap = deal.get_esap_summary()
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total", esap['total'])
        with col2:
            st.metric("Complétées", esap['completed'])
        with col3:
            st.metric("En cours", esap['in_progress'])
        with col4:
            st.metric("Retard", esap['overdue'])
        
        if esap['total'] > 0:
            st.progress(esap['completion_rate'] / 100)
        
        st.markdown("---")
        
        if deal.esap_items:
            for item in deal.esap_items:
                priority = {"high": "🔴", "medium": "🟠", "low": "🟢"}[item.priority]
                
                col1, col2, col3 = st.columns([3, 1, 1])
                with col1:
                    st.markdown(f"{priority} **{item.action}**")
                    st.caption(f"Responsable: {item.responsible}")
                with col2:
                    if item.deadline:
                        days = (item.deadline - datetime.now()).days
                        color = "🔴" if days < 0 else ("🟠" if days < 30 else "🟢")
                        st.markdown(f"{color} {days}j")
                with col3:
                    new_st = st.selectbox(
                        "St", ["not_started", "in_progress", "completed"],
                        index=["not_started", "in_progress", "completed"].index(item.status),
                        format_func=lambda x: {"not_started": "⏳", "in_progress": "🔄", "completed": "✅"}[x],
                        key=f"esap_{deal.id}_{item.id}",
                        label_visibility="collapsed"
                    )
                    if new_st != item.status:
                        item.status = new_st
                        storage.save(deal)
                        st.rerun()
                st.markdown("---")
        else:
            st.info("Aucune action ESAP.")

# =============================================================================
# TAB 3: KPIs
# =============================================================================
with tab3:
    st.subheader("KPIs ESG & Impact")
    
    selected_id = st.selectbox("Deal", options=[d.id for d in monitoring_deals], format_func=lambda x: storage.get(x).company_name, key="kpi_deal")
    deal = storage.get(selected_id)
    
    if deal:
        st.markdown(f"### {deal.company_name}")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            own = st.number_input("% Ownership femmes", 0, 100, int(deal.two_x_data.get('women_ownership_pct', 0)))
        with col2:
            mgmt = st.number_input("% Management femmes", 0, 100, int(deal.two_x_data.get('women_management_pct', 0)))
        with col3:
            emp = st.number_input("% Employées femmes", 0, 100, int(deal.two_x_data.get('women_employees_pct', 0)))
        with col4:
            total = st.number_input("Total employés", 1, 100000, deal.employees or 50)
        
        if st.button("📊 Mettre à jour", type="primary"):
            deal.two_x_data['women_ownership_pct'] = own
            deal.two_x_data['women_management_pct'] = mgmt
            deal.two_x_data['women_employees_pct'] = emp
            deal.employees = total
            
            result = calculate_2x_eligibility(deal.two_x_data, deal.sector)
            deal.two_x_eligible = result['eligible']
            deal.two_x_criteria_met = result['criteria_met']
            
            deal.add_kpi_snapshot({
                "women_ownership_pct": own,
                "women_management_pct": mgmt,
                "women_employees_pct": emp,
                "total_employees": total,
                "two_x_eligible": deal.two_x_eligible
            })
            
            storage.save(deal)
            st.success("✅ Mis à jour !")
            st.rerun()
        
        st.markdown("---")
        
        if deal.two_x_eligible:
            st.success(f"✅ **Éligible 2X** ({deal.two_x_criteria_met}/4)")
        else:
            st.warning(f"❌ **Non éligible 2X** ({deal.two_x_criteria_met}/4)")
        
        if deal.monitoring_kpis:
            st.markdown("### Historique")
            hist = [{"Date": k['date'][:10], "Own": k['data'].get('women_ownership_pct'), "Mgmt": k['data'].get('women_management_pct'), "Emp": k['data'].get('women_employees_pct')} for k in deal.monitoring_kpis]
            st.dataframe(pd.DataFrame(hist), hide_index=True)

# =============================================================================
# TAB 4: Rapports IA
# =============================================================================
with tab4:
    st.subheader("🤖 Rapports IA")
    
    selected_id = st.selectbox("Deal", options=[d.id for d in monitoring_deals], format_func=lambda x: storage.get(x).company_name, key="report_deal")
    deal = storage.get(selected_id)
    
    if deal:
        st.markdown(f"### {deal.company_name}")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📊 Générer rapport de monitoring", type="primary", use_container_width=True):
                with st.spinner("🔄 Génération... (60-90 sec)"):
                    try:
                        llm_manager = get_llm_manager()
                        esap_summary = deal.get_esap_summary()
                        
                        # Date investissement (approximation)
                        ic_data = deal.get_stage_data(DealStage.INVESTMENT_COMMITTEE)
                        invest_date = ic_data.completed_at.strftime('%d/%m/%Y') if ic_data and ic_data.completed_at else "N/A"
                        
                        current_kpis = {
                            'women_ownership_pct': deal.two_x_data.get('women_ownership_pct', 0),
                            'women_management_pct': deal.two_x_data.get('women_management_pct', 0),
                            'women_employees_pct': deal.two_x_data.get('women_employees_pct', 0),
                            'total_employees': deal.employees,
                            'two_x_eligible': deal.two_x_eligible
                        }
                        
                        prompt = format_monitoring_report_prompt(
                            company_name=deal.company_name,
                            country=deal.country,
                            sector=deal.sector,
                            investment_date=invest_date,
                            current_kpis=current_kpis,
                            kpi_history=deal.monitoring_kpis,
                            esap_summary=esap_summary,
                            esap_items=deal.esap_items
                        )
                        
                        response = llm_manager.generate_response(
                            prompt=prompt,
                            system_prompt=MONITORING_SYSTEM_PROMPT,
                            primary_provider=ProviderType(llm_provider),
                            max_tokens=3500,
                            temperature=0.3
                        )
                        
                        st.session_state[f'monitoring_report_{deal.id}'] = response
                        st.success("✅ Rapport généré !")
                        
                    except Exception as e:
                        st.error(f"❌ Erreur : {str(e)}")
        
        with col2:
            if st.button("💡 Recommandations ESAP", use_container_width=True):
                with st.spinner("🔄 Génération..."):
                    try:
                        llm_manager = get_llm_manager()
                        
                        gaps = []
                        if not deal.two_x_eligible:
                            if deal.two_x_data.get('women_ownership_pct', 0) < 51:
                                gaps.append("Ownership féminin < 51%")
                            if deal.two_x_data.get('women_management_pct', 0) < 30:
                                gaps.append("Management féminin < 30%")
                            if deal.two_x_data.get('women_employees_pct', 0) < 30:
                                gaps.append("Employées femmes < 30%")
                        
                        prompt = format_esap_recommendations_prompt(
                            company_name=deal.company_name,
                            sector=deal.sector,
                            country=deal.country,
                            current_gaps=gaps,
                            two_x_eligible=deal.two_x_eligible,
                            two_x_data=deal.two_x_data
                        )
                        
                        response = llm_manager.generate_response(
                            prompt=prompt,
                            system_prompt=MONITORING_SYSTEM_PROMPT,
                            primary_provider=ProviderType(llm_provider),
                            max_tokens=2000,
                            temperature=0.3
                        )
                        
                        st.session_state[f'esap_reco_{deal.id}'] = response
                        st.success("✅ Recommandations générées !")
                        
                    except Exception as e:
                        st.error(f"❌ Erreur : {str(e)}")
        
        st.markdown("---")
        
        # Afficher les rapports
        if f'monitoring_report_{deal.id}' in st.session_state:
            st.markdown("### 📊 Rapport de Monitoring")
            st.markdown(st.session_state[f'monitoring_report_{deal.id}'])
            st.download_button(
                "📥 Télécharger",
                st.session_state[f'monitoring_report_{deal.id}'],
                f"monitoring_{deal.company_name.replace(' ', '_')}.md"
            )
        
        if f'esap_reco_{deal.id}' in st.session_state:
            st.markdown("### 💡 Recommandations ESAP")
            st.markdown(st.session_state[f'esap_reco_{deal.id}'])

st.markdown("---")
st.caption("ESG Analyzer v2.3 | Monitoring")
