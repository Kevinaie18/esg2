"""
Page Screening - Première évaluation rapide des opportunités d'investissement.
Inclut l'analyse IA pour recommandation GO/NO-GO automatique.
"""
import streamlit as st
from datetime import datetime

from models.deal import Deal, DealStage, DealStatus, StageData
from services.deal_storage import get_deal_storage
from config.risk_classification import get_sectors, get_subsectors, get_risk_category, get_risk_display
from config.countries import IPAE3_COUNTRIES, get_country_for_prompt
from config.two_x_challenge import calculate_2x_eligibility, get_threshold
from engine.llm_service import get_llm_manager, ProviderType
from prompts.screening_prompts import SCREENING_SYSTEM_PROMPT, format_screening_prompt

st.set_page_config(
    page_title="Screening - ESG Analyzer",
    page_icon="🔍",
    layout="wide"
)

storage = get_deal_storage()

st.title("🔍 Screening")
st.markdown("Évaluation rapide des nouvelles opportunités d'investissement")
st.markdown("---")

tab1, tab2 = st.tabs(["➕ Nouveau deal", "📋 Deals en screening"])

# =============================================================================
# TAB 1: Nouveau deal
# =============================================================================
with tab1:
    st.header("Nouvelle opportunité")
    
    with st.form("screening_form"):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            company_name = st.text_input("Nom de l'entreprise *", placeholder="Ex: AgroCorp SARL")
        
        with col2:
            country = st.selectbox("Pays *", options=list(IPAE3_COUNTRIES.keys()), index=0)
            ctx = IPAE3_COUNTRIES.get(country, {})
            if ctx and country != "Autre":
                indicators = []
                if ctx.get('ldc'): indicators.append("🔸 PMA")
                if ctx.get('fragile'): indicators.append("⚠️ Fragile")
                if indicators:
                    st.caption(f"📍 {ctx.get('region', '')} | {' '.join(indicators)}")
        
        with col3:
            sector = st.selectbox("Secteur *", options=get_sectors())
        
        col1, col2 = st.columns(2)
        with col1:
            subsector_options = get_subsectors(sector)
            subsector = st.selectbox("Sous-secteur *", options=subsector_options if subsector_options else ["Non spécifié"])
        with col2:
            risk_cat = get_risk_category(sector, subsector)
            risk_info = get_risk_display(risk_cat)
            st.markdown(f"**Classification E&S:** {risk_info['color']} **Cat. {risk_cat}**")
        
        description = st.text_area("Description de l'activité *", placeholder="Ex: Production et distribution de produits laitiers", height=80)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            employees = st.number_input("Nombre d'employés", min_value=1, max_value=50000, value=50)
        with col2:
            revenue = st.selectbox("CA annuel (EUR)", ["< 500K", "500K - 2M", "2M - 5M", "5M - 10M", "10M - 50M", "> 50M"])
        with col3:
            target_market = st.selectbox("Marché cible", ["B2C - Particuliers", "B2B - Entreprises", "B2B2C - Les deux", "B2G - Institutions"])
        
        st.markdown("---")
        st.subheader("🎯 Évaluation 2X Challenge")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            women_ownership = st.slider("% Détention femmes", 0, 100, 0)
        with col2:
            women_management = st.slider("% Management femmes", 0, 100, 20)
        with col3:
            women_employees = st.slider("% Employées femmes", 0, 100, 30)
        with col4:
            benefits_women = st.checkbox("Produit pour femmes")
        
        two_x_data = {"women_ownership_pct": women_ownership, "women_management_pct": women_management, "women_employees_pct": women_employees, "benefits_women": benefits_women}
        two_x_result = calculate_2x_eligibility(two_x_data, sector)
        
        if two_x_result["eligible"]:
            st.success(f"✅ **Éligible 2X** ({two_x_result['criteria_met']}/4)")
        else:
            st.warning(f"❌ **Non éligible 2X** ({two_x_result['criteria_met']}/4)")
        
        st.markdown("---")
        submitted = st.form_submit_button("🚀 Créer le deal", use_container_width=True, type="primary")
    
    if submitted:
        if not company_name:
            st.error("❌ Veuillez entrer le nom de l'entreprise.")
        elif not description:
            st.error("❌ Veuillez décrire l'activité.")
        else:
            deal = Deal(
                id=Deal.generate_id(company_name),
                created_at=datetime.now(),
                updated_at=datetime.now(),
                company_name=company_name,
                country=country,
                sector=sector,
                subsector=subsector,
                description=description,
                employees=employees,
                revenue=revenue,
                target_market=target_market,
                risk_category=risk_cat,
                two_x_data=two_x_data,
                two_x_eligible=two_x_result["eligible"],
                two_x_criteria_met=two_x_result["criteria_met"],
                current_stage=DealStage.SCREENING
            )
            deal.stage_history[DealStage.SCREENING.value] = StageData(
                stage=DealStage.SCREENING,
                status=DealStatus.IN_PROGRESS,
                started_at=datetime.now()
            )
            if storage.save(deal):
                st.success(f"✅ Deal créé ! ID: **{deal.id}**")
                st.session_state['last_created_deal_id'] = deal.id
                st.rerun()

# =============================================================================
# TAB 2: Deals en screening
# =============================================================================
with tab2:
    st.header("Deals en screening")
    
    screening_deals = storage.get_by_stage(DealStage.SCREENING)
    
    if not screening_deals:
        st.info("📭 Aucun deal en screening.")
    else:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col1:
            status_filter = st.selectbox("Filtrer", ["Tous", "En cours", "En attente", "Approuvés"])
        with col3:
            llm_provider = st.selectbox(
                "Fournisseur IA",
                ["anthropic", "openai", "deepseek"],
                format_func=lambda x: {"anthropic": "Claude", "openai": "GPT-4", "deepseek": "DeepSeek"}[x]
            )
        
        if status_filter == "En cours":
            screening_deals = [d for d in screening_deals if d.get_current_stage_data() and d.get_current_stage_data().status == DealStatus.IN_PROGRESS]
        elif status_filter == "En attente":
            screening_deals = [d for d in screening_deals if d.get_current_stage_data() and d.get_current_stage_data().status == DealStatus.ON_HOLD]
        elif status_filter == "Approuvés":
            screening_deals = [d for d in screening_deals if d.get_current_stage_data() and d.get_current_stage_data().status == DealStatus.APPROVED]
        
        st.markdown(f"**{len(screening_deals)} deal(s)**")
        
        for deal in screening_deals:
            stage_data = deal.get_current_stage_data()
            status_icon = {DealStatus.IN_PROGRESS: "🔄", DealStatus.ON_HOLD: "⏸️", DealStatus.APPROVED: "✅"}.get(stage_data.status if stage_data else None, "❓")
            
            with st.expander(f"{status_icon} **{deal.company_name}** — {deal.country} — {deal.sector}"):
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.markdown(f"**ID:** `{deal.id}`")
                    st.markdown(f"**Créé:** {deal.created_at.strftime('%d/%m/%Y')}")
                with col2:
                    st.markdown(f"**Risque:** Cat. {deal.risk_category}")
                    st.markdown(f"**Employés:** {deal.employees}")
                with col3:
                    st.markdown(f"**2X:** {'✅' if deal.two_x_eligible else '❌'}")
                    st.markdown(f"**Critères:** {deal.two_x_criteria_met}/4")
                with col4:
                    st.markdown(f"**CA:** {deal.revenue}")
                
                st.markdown(f"**Description:** {deal.description[:200]}...")
                st.markdown("---")
                
                # =====================================================
                # SECTION ANALYSE IA
                # =====================================================
                if stage_data and stage_data.status == DealStatus.IN_PROGRESS:
                    
                    st.markdown("### 🤖 Analyse IA")
                    
                    if st.button(f"🤖 Générer l'analyse screening", key=f"ai_{deal.id}", type="secondary", use_container_width=True):
                        with st.spinner("🔄 Analyse en cours... (30-60 sec)"):
                            try:
                                llm_manager = get_llm_manager()
                                country_context = get_country_for_prompt(deal.country)
                                
                                prompt = format_screening_prompt(
                                    company_name=deal.company_name,
                                    country=deal.country,
                                    country_context=country_context,
                                    sector=deal.sector,
                                    subsector=deal.subsector,
                                    description=deal.description,
                                    employees=deal.employees,
                                    revenue=deal.revenue,
                                    risk_category=deal.risk_category,
                                    two_x_eligible=deal.two_x_eligible,
                                    two_x_criteria_met=deal.two_x_criteria_met,
                                    two_x_data=deal.two_x_data
                                )
                                
                                response = llm_manager.generate_response(
                                    prompt=prompt,
                                    system_prompt=SCREENING_SYSTEM_PROMPT,
                                    primary_provider=ProviderType(llm_provider),
                                    max_tokens=2500,
                                    temperature=0.3
                                )
                                
                                stage_data.analysis_result = response
                                storage.save(deal)
                                st.success("✅ Analyse générée !")
                                st.rerun()
                                
                            except Exception as e:
                                st.error(f"❌ Erreur : {str(e)}")
                    
                    if stage_data.analysis_result:
                        st.markdown("---")
                        st.markdown("### 📋 Résultat de l'analyse")
                        st.markdown(stage_data.analysis_result)
                        st.download_button(
                            "📥 Télécharger",
                            stage_data.analysis_result,
                            f"screening_{deal.id}.md",
                            key=f"dl_{deal.id}"
                        )
                    
                    st.markdown("---")
                    st.markdown("### 📋 Décision")
                    
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        if st.button("✅ GO", key=f"go_{deal.id}", type="primary"):
                            stage_data.decision = "GO"
                            stage_data.status = DealStatus.APPROVED
                            storage.save(deal)
                            st.rerun()
                    with col2:
                        if st.button("❌ NO-GO", key=f"nogo_{deal.id}"):
                            deal.reject("Rejeté")
                            storage.save(deal)
                            st.rerun()
                    with col3:
                        if st.button("⏸️ Attente", key=f"hold_{deal.id}"):
                            stage_data.status = DealStatus.ON_HOLD
                            storage.save(deal)
                            st.rerun()
                    with col4:
                        if st.button("🗑️ Supprimer", key=f"del_{deal.id}"):
                            storage.delete(deal.id)
                            st.rerun()
                
                elif stage_data and stage_data.status == DealStatus.APPROVED:
                    st.success("✅ Approuvé - Prêt pour DD")
                    if stage_data.analysis_result:
                        with st.expander("📋 Voir l'analyse"):
                            st.markdown(stage_data.analysis_result)
                    if st.button(f"🚀 Passer en DD", key=f"dd_{deal.id}", type="primary"):
                        try:
                            deal.advance_stage(DealStage.DUE_DILIGENCE)
                            storage.save(deal)
                            st.rerun()
                        except ValueError as e:
                            st.error(str(e))
                
                elif stage_data and stage_data.status == DealStatus.ON_HOLD:
                    st.warning("⏸️ En attente")
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("🔄 Reprendre", key=f"resume_{deal.id}"):
                            stage_data.status = DealStatus.IN_PROGRESS
                            storage.save(deal)
                            st.rerun()
                    with col2:
                        if st.button("❌ Rejeter", key=f"rej_{deal.id}"):
                            deal.reject("Rejeté")
                            storage.save(deal)
                            st.rerun()

st.markdown("---")
st.caption("ESG Analyzer v2.3 | Screening")
