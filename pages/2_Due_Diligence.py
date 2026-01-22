"""
Page Due Diligence - Analyse terrain approfondie avec assistance IA.
"""
import streamlit as st
from datetime import datetime

from models.deal import Deal, DealStage, DealStatus
from services.deal_storage import get_deal_storage
from config.dd_checklists import generate_dd_checklist, get_checklist_summary
from config.countries import IPAE3_COUNTRIES, get_country_for_prompt
from formatters.checklist_formatter import export_checklist_to_excel
from engine.llm_service import get_llm_manager, ProviderType
from prompts.dd_prompts import DD_SYSTEM_PROMPT, format_dd_analysis_prompt, format_dd_synthesis_prompt

st.set_page_config(page_title="Due Diligence - ESG Analyzer", page_icon="📋", layout="wide")

storage = get_deal_storage()

st.title("📋 Due Diligence")
st.markdown("Analyse terrain et vérification des points de contrôle ESG")
st.markdown("---")

# Deals prêts pour DD
screening_approved = storage.get_by_status(DealStage.SCREENING, DealStatus.APPROVED)
if screening_approved:
    st.info(f"📥 **{len(screening_approved)} deal(s)** prêts pour DD")
    with st.expander("Démarrer la DD"):
        for deal in screening_approved:
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"**{deal.company_name}** — {deal.country}")
            with col2:
                if st.button(f"▶️ Démarrer", key=f"start_{deal.id}"):
                    deal.advance_stage(DealStage.DUE_DILIGENCE)
                    storage.save(deal)
                    st.rerun()
    st.markdown("---")

# Deals en DD
dd_deals = storage.get_by_stage(DealStage.DUE_DILIGENCE)

if not dd_deals:
    st.warning("📭 Aucun deal en Due Diligence.")
    st.stop()

# Sélection
col1, col2 = st.columns([3, 1])
with col1:
    selected_id = st.selectbox("Sélectionner un deal", options=[d.id for d in dd_deals], format_func=lambda x: f"{storage.get(x).company_name} ({x})")
with col2:
    llm_provider = st.selectbox("Fournisseur IA", ["anthropic", "openai", "deepseek"], format_func=lambda x: {"anthropic": "Claude", "openai": "GPT-4", "deepseek": "DeepSeek"}[x])

deal = storage.get(selected_id)
if not deal:
    st.error("Deal non trouvé")
    st.stop()

st.markdown("---")
st.header(f"📋 DD - {deal.company_name}")

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Pays", deal.country)
with col2:
    st.metric("Secteur", deal.sector)
with col3:
    st.metric("Risque", f"Cat. {deal.risk_category}")
with col4:
    st.metric("2X", "✅" if deal.two_x_eligible else "❌")

st.markdown("---")

tab1, tab2, tab3, tab4 = st.tabs(["📋 Checklist", "🤖 Analyse IA", "📝 Notes", "✅ Validation"])

# =============================================================================
# TAB 1: Checklist
# =============================================================================
with tab1:
    st.subheader("Checklist Due Diligence")
    
    country_info = IPAE3_COUNTRIES.get(deal.country, {})
    checklist = generate_dd_checklist(
        sector=deal.sector,
        risk_category=deal.risk_category,
        country_fragile=country_info.get('fragile', False),
        country_ldc=country_info.get('ldc', False),
        two_x_gaps=[]
    )
    
    summary = get_checklist_summary(checklist)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total", summary['total'])
    with col2:
        st.metric("Haute priorité", summary['high_priority_count'])
    with col3:
        st.metric("Catégories", len(summary['by_category']))
    with col4:
        excel_buf = export_checklist_to_excel(checklist, deal.company_name, deal.sector, deal.risk_category, deal.country)
        st.download_button("📥 Excel", excel_buf, f"checklist_{deal.id}.xlsx")
    
    stage_data = deal.get_current_stage_data()
    if not stage_data.checklist_status:
        stage_data.checklist_status = {item['id']: 'pending' for item in checklist}
    
    categories = {}
    for item in checklist:
        cat = item['category']
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(item)
    
    for cat_name, items in categories.items():
        with st.expander(f"**{cat_name}** ({len(items)} points)", expanded=False):
            for item in items:
                col1, col2 = st.columns([4, 1])
                with col1:
                    priority_icon = {"high": "🔴", "medium": "🟠", "low": "🟢"}.get(item['priority'], "")
                    st.markdown(f"{priority_icon} {item['question']}")
                with col2:
                    current = stage_data.checklist_status.get(item['id'], 'pending')
                    new_status = st.selectbox(
                        "Statut", ["pending", "conforme", "partiel", "non_conforme", "na"],
                        index=["pending", "conforme", "partiel", "non_conforme", "na"].index(current),
                        format_func=lambda x: {"pending": "⏳", "conforme": "✅", "partiel": "⚠️", "non_conforme": "❌", "na": "➖"}[x],
                        key=f"chk_{item['id']}",
                        label_visibility="collapsed"
                    )
                    if new_status != current:
                        stage_data.checklist_status[item['id']] = new_status
    
    if st.button("💾 Sauvegarder", type="primary", use_container_width=True):
        storage.save(deal)
        st.success("✅ Sauvegardé !")

# =============================================================================
# TAB 2: Analyse IA
# =============================================================================
with tab2:
    st.subheader("🤖 Analyse IA Due Diligence")
    
    stage_data = deal.get_current_stage_data()
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🤖 Générer l'analyse DD complète", type="primary", use_container_width=True):
            with st.spinner("🔄 Analyse en cours... (60-90 sec)"):
                try:
                    llm_manager = get_llm_manager()
                    country_context = get_country_for_prompt(deal.country)
                    
                    prompt = format_dd_analysis_prompt(
                        company_name=deal.company_name,
                        country=deal.country,
                        country_context=country_context,
                        sector=deal.sector,
                        subsector=deal.subsector,
                        description=deal.description,
                        risk_category=deal.risk_category,
                        employees=deal.employees,
                        two_x_data=deal.two_x_data,
                        checklist_status=stage_data.checklist_status
                    )
                    
                    response = llm_manager.generate_response(
                        prompt=prompt,
                        system_prompt=DD_SYSTEM_PROMPT,
                        primary_provider=ProviderType(llm_provider),
                        max_tokens=4000,
                        temperature=0.3
                    )
                    
                    stage_data.analysis_result = response
                    storage.save(deal)
                    st.success("✅ Analyse générée !")
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"❌ Erreur : {str(e)}")
    
    with col2:
        if st.button("📝 Générer synthèse DD", use_container_width=True):
            with st.spinner("🔄 Génération..."):
                try:
                    llm_manager = get_llm_manager()
                    
                    prompt = format_dd_synthesis_prompt(
                        company_name=deal.company_name,
                        country=deal.country,
                        sector=deal.sector,
                        risk_category=deal.risk_category,
                        checklist_status=stage_data.checklist_status or {},
                        conditions=stage_data.conditions or [],
                        comments=stage_data.comments or []
                    )
                    
                    response = llm_manager.generate_response(
                        prompt=prompt,
                        system_prompt=DD_SYSTEM_PROMPT,
                        primary_provider=ProviderType(llm_provider),
                        max_tokens=1500,
                        temperature=0.3
                    )
                    
                    if stage_data.analysis_result:
                        stage_data.analysis_result += "\n\n---\n\n## SYNTHÈSE DD\n\n" + response
                    else:
                        stage_data.analysis_result = response
                    storage.save(deal)
                    st.success("✅ Synthèse ajoutée !")
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"❌ Erreur : {str(e)}")
    
    if stage_data.analysis_result:
        st.markdown("---")
        st.markdown("### 📋 Résultat de l'analyse")
        st.markdown(stage_data.analysis_result)
        st.download_button("📥 Télécharger", stage_data.analysis_result, f"dd_analysis_{deal.id}.md")

# =============================================================================
# TAB 3: Notes
# =============================================================================
with tab3:
    st.subheader("Notes et observations")
    
    stage_data = deal.get_current_stage_data()
    
    new_comment = st.text_area("Nouvelle note", placeholder="Observations terrain...")
    if st.button("💬 Ajouter") and new_comment:
        deal.add_comment(new_comment, "Analyste DD")
        storage.save(deal)
        st.rerun()
    
    st.markdown("---")
    if stage_data and stage_data.comments:
        for c in reversed(stage_data.comments):
            st.markdown(f"**{c.get('author')}** — {c.get('timestamp', '')[:16]}")
            st.markdown(c.get('text', ''))
            st.markdown("---")
    else:
        st.info("Aucune note.")

# =============================================================================
# TAB 4: Validation
# =============================================================================
with tab4:
    st.subheader("Validation Due Diligence")
    
    stage_data = deal.get_current_stage_data()
    
    if stage_data.checklist_status:
        total = len(stage_data.checklist_status)
        conformes = sum(1 for v in stage_data.checklist_status.values() if v == 'conforme')
        partiels = sum(1 for v in stage_data.checklist_status.values() if v == 'partiel')
        non_conformes = sum(1 for v in stage_data.checklist_status.values() if v == 'non_conforme')
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Conformes", conformes)
        with col2:
            st.metric("Partiels", partiels)
        with col3:
            st.metric("Non conformes", non_conformes)
        with col4:
            rate = (conformes / total * 100) if total > 0 else 0
            st.metric("Taux", f"{rate:.0f}%")
    
    st.markdown("---")
    st.markdown("### Décision DD")
    
    decision = st.radio("Recommandation", ["GO - Passer au IC", "GO avec conditions", "NO-GO - Rejeter"])
    
    conditions_text = ""
    if "conditions" in decision.lower():
        conditions_text = st.text_area("Conditions (une par ligne)")
    
    rationale = st.text_area("Synthèse et justification")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("✅ Valider la DD", type="primary", use_container_width=True):
            if "NO-GO" in decision:
                deal.reject(rationale)
                storage.save(deal)
                st.error("❌ Deal rejeté")
            else:
                stage_data.decision = "GO" if "GO -" in decision else "GO_WITH_CONDITIONS"
                stage_data.decision_rationale = rationale
                if conditions_text:
                    stage_data.conditions = [c.strip() for c in conditions_text.split('\n') if c.strip()]
                stage_data.status = DealStatus.APPROVED
                storage.save(deal)
                st.success("✅ DD validée !")
                st.balloons()
    
    with col2:
        if stage_data and stage_data.status == DealStatus.APPROVED:
            if st.button("🚀 Passer au IC", use_container_width=True):
                try:
                    deal.advance_stage(DealStage.INVESTMENT_COMMITTEE)
                    storage.save(deal)
                    st.rerun()
                except ValueError as e:
                    st.error(str(e))

st.markdown("---")
st.caption("ESG Analyzer v2.3 | Due Diligence")
