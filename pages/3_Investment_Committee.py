"""
Page Investment Committee - Préparation du mémo IC et décision finale d'investissement.
"""
import streamlit as st
from datetime import datetime, timedelta

from models.deal import Deal, DealStage, DealStatus, ESAPItem
from services.deal_storage import get_deal_storage
from prompts.memo_prompt import format_memo_prompt, MEMO_SYSTEM_PROMPT
from engine.llm_service import get_llm_manager, ProviderType
from config.two_x_challenge import get_threshold
from config.risk_classification import get_risk_display
from config.countries import get_country_for_prompt

st.set_page_config(
    page_title="Investment Committee - ESG Analyzer",
    page_icon="👥",
    layout="wide"
)

# Initialiser le storage
storage = get_deal_storage()

# Header
st.title("👥 Comité d'Investissement")
st.markdown("Préparation du mémo IC et décision finale d'investissement")

st.markdown("---")

# Récupérer les deals en IC
ic_deals = storage.get_by_stage(DealStage.INVESTMENT_COMMITTEE)

# Aussi récupérer les deals DD approuvés
dd_approved = storage.get_by_status(DealStage.DUE_DILIGENCE, DealStatus.APPROVED)

# Section: Deals prêts pour IC
if dd_approved:
    st.info(f"📥 **{len(dd_approved)} deal(s)** avec DD validée, prêts pour le Comité")
    
    with st.expander("Voir les deals prêts pour IC"):
        for deal in dd_approved:
            col1, col2, col3 = st.columns([3, 1, 1])
            
            with col1:
                st.markdown(f"**{deal.company_name}** — {deal.country}")
                dd_data = deal.get_stage_data(DealStage.DUE_DILIGENCE)
                if dd_data and dd_data.conditions:
                    st.caption(f"⚠️ {len(dd_data.conditions)} condition(s) préalable(s)")
            
            with col2:
                st.markdown(f"{'✅' if deal.two_x_eligible else '❌'} 2X")
            
            with col3:
                if st.button(f"▶️ Passer en IC", key=f"to_ic_{deal.id}"):
                    try:
                        deal.advance_stage(DealStage.INVESTMENT_COMMITTEE)
                        storage.save(deal)
                        st.success(f"Deal passé en IC")
                        st.rerun()
                    except ValueError as e:
                        st.error(f"Erreur : {e}")
    
    st.markdown("---")

# Vérifier s'il y a des deals en IC
if not ic_deals:
    st.warning("📭 Aucun deal au stade Comité d'Investissement actuellement.")
    st.info("💡 Validez des Due Diligence pour passer des deals en IC.")
    st.stop()

# Sélectionner un deal
st.subheader("Sélectionner un deal")

selected_id = st.selectbox(
    "Deal",
    options=[d.id for d in ic_deals],
    format_func=lambda x: f"{storage.get(x).company_name} ({x})",
    key="ic_deal_selector"
)

deal = storage.get(selected_id)

if not deal:
    st.error("Deal non trouvé")
    st.stop()

# Afficher les infos du deal
st.markdown("---")
st.header(f"👥 IC - {deal.company_name}")

# Résumé
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Pays", deal.country)
with col2:
    st.metric("Risque", f"Cat. {deal.risk_category}")
with col3:
    st.metric("2X", "✅ Éligible" if deal.two_x_eligible else "❌ Non éligible")
with col4:
    # Conditions de la DD
    dd_data = deal.get_stage_data(DealStage.DUE_DILIGENCE)
    n_conditions = len(dd_data.conditions) if dd_data and dd_data.conditions else 0
    st.metric("Conditions DD", n_conditions)

st.markdown("---")

# Tabs
tab1, tab2, tab3, tab4 = st.tabs(["📋 Mémo IC", "📊 ESAP", "📄 Conditions DD", "✅ Décision"])

# =============================================================================
# TAB 1: Mémo IC
# =============================================================================
with tab1:
    st.subheader("Section ESG du Mémo d'Investissement")
    
    # Configuration LLM
    col1, col2 = st.columns([1, 3])
    with col1:
        llm_provider = st.selectbox(
            "Fournisseur IA",
            ["openai", "anthropic"],
            format_func=lambda x: "OpenAI (GPT-4)" if x == "openai" else "Anthropic (Claude)"
        )
    
    # Bouton génération
    if st.button("🤖 Générer le mémo ESG", type="primary", use_container_width=True):
        with st.spinner("Génération en cours... (30-60 secondes)"):
            try:
                llm_manager = get_llm_manager()
                risk_info = get_risk_display(deal.risk_category)
                country_context = get_country_for_prompt(deal.country)
                
                prompt = format_memo_prompt(
                    company_name=deal.company_name,
                    country=deal.country,
                    country_context=country_context,
                    sector=deal.sector,
                    subsector=deal.subsector,
                    company_description=deal.description,
                    risk_category=deal.risk_category,
                    due_diligence_type=risk_info['due_diligence'],
                    applicable_standards=", ".join(deal.applicable_standards) if deal.applicable_standards else "PS1, PS2",
                    women_ownership=deal.two_x_data.get('women_ownership_pct', 0),
                    women_management=deal.two_x_data.get('women_management_pct', 0),
                    women_employees=deal.two_x_data.get('women_employees_pct', 0),
                    benefits_women=deal.two_x_data.get('benefits_women', False),
                    leadership_threshold=int(get_threshold('leadership', deal.sector) * 100),
                    employment_threshold=int(get_threshold('employment', deal.sector) * 100),
                    two_x_status="Éligible" if deal.two_x_eligible else "Non éligible",
                    two_x_criteria_met=deal.two_x_criteria_met,
                    date=datetime.now().strftime("%d/%m/%Y")
                )
                
                response = llm_manager.generate_response(
                    prompt=prompt,
                    primary_provider=ProviderType(llm_provider),
                    max_tokens=2500,
                    temperature=0.3
                )
                
                # Sauvegarder le résultat
                stage_data = deal.get_current_stage_data()
                stage_data.analysis_result = response
                storage.save(deal)
                
                st.success("✅ Mémo généré avec succès !")
                
            except Exception as e:
                st.error(f"❌ Erreur lors de la génération : {e}")
    
    # Afficher le mémo existant
    st.markdown("---")
    
    stage_data = deal.get_current_stage_data()
    if stage_data and stage_data.analysis_result:
        st.markdown("### 📄 Mémo ESG")
        st.markdown(stage_data.analysis_result)
        
        # Export
        st.download_button(
            "📥 Télécharger le mémo (Markdown)",
            stage_data.analysis_result,
            f"memo_ic_{deal.company_name.replace(' ', '_')}.md",
            mime="text/markdown"
        )
    else:
        st.info("📝 Cliquez sur 'Générer le mémo ESG' pour créer la section ESG du mémo IC.")

# =============================================================================
# TAB 2: ESAP
# =============================================================================
with tab2:
    st.subheader("Environmental & Social Action Plan (ESAP)")
    st.caption("Actions à mettre en œuvre post-investissement")
    
    # Formulaire ajout action
    with st.expander("➕ Ajouter une action ESAP", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            esap_category = st.selectbox(
                "Catégorie",
                ["E&S", "Gouvernance", "Genre/2X", "HSE", "Climat", "Social"],
                key="esap_category"
            )
            esap_action = st.text_area(
                "Action requise",
                placeholder="Décrivez l'action à mettre en place",
                key="esap_action"
            )
        
        with col2:
            esap_responsible = st.text_input(
                "Responsable",
                placeholder="Ex: DG, DRH, Responsable HSE",
                key="esap_responsible"
            )
            esap_deadline = st.date_input(
                "Échéance",
                value=datetime.now() + timedelta(days=90),
                key="esap_deadline"
            )
            esap_priority = st.selectbox(
                "Priorité",
                ["high", "medium", "low"],
                format_func=lambda x: {"high": "🔴 Haute", "medium": "🟠 Moyenne", "low": "🟢 Basse"}[x],
                key="esap_priority"
            )
            esap_kpi = st.text_input(
                "KPI de suivi (optionnel)",
                placeholder="Ex: Nombre de formations réalisées",
                key="esap_kpi"
            )
        
        if st.button("➕ Ajouter l'action"):
            if esap_action and esap_responsible:
                new_item = ESAPItem(
                    id=f"ESAP_{len(deal.esap_items)+1:03d}",
                    category=esap_category,
                    action=esap_action,
                    responsible=esap_responsible,
                    deadline=datetime.combine(esap_deadline, datetime.min.time()),
                    status="not_started",
                    priority=esap_priority,
                    kpi=esap_kpi if esap_kpi else None
                )
                deal.add_esap_item(new_item)
                storage.save(deal)
                st.success("✅ Action ESAP ajoutée")
                st.rerun()
            else:
                st.error("Veuillez remplir l'action et le responsable")
    
    st.markdown("---")
    
    # Liste des actions ESAP
    st.markdown("### 📋 Actions ESAP")
    
    if deal.esap_items:
        # Résumé
        esap_summary = deal.get_esap_summary()
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total", esap_summary['total'])
        with col2:
            st.metric("À faire", esap_summary['not_started'])
        with col3:
            st.metric("En cours", esap_summary['in_progress'])
        with col4:
            st.metric("Complétées", esap_summary['completed'])
        
        st.markdown("---")
        
        # Liste
        for item in deal.esap_items:
            priority_icon = {"high": "🔴", "medium": "🟠", "low": "🟢"}[item.priority]
            status_icon = {
                "not_started": "⏳",
                "in_progress": "🔄",
                "completed": "✅",
                "overdue": "⚠️"
            }.get(item.status, "❓")
            
            with st.expander(f"{priority_icon} {status_icon} **{item.id}** — {item.category}: {item.action[:50]}..."):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown(f"**Action:** {item.action}")
                    st.markdown(f"**Responsable:** {item.responsible}")
                    if item.kpi:
                        st.markdown(f"**KPI:** {item.kpi}")
                
                with col2:
                    st.markdown(f"**Échéance:** {item.deadline.strftime('%d/%m/%Y') if item.deadline else 'N/A'}")
                    st.markdown(f"**Priorité:** {priority_icon} {item.priority}")
                    st.markdown(f"**Statut:** {status_icon} {item.status}")
                
                # Actions
                col1, col2 = st.columns(2)
                with col1:
                    if st.button(f"🗑️ Supprimer", key=f"del_esap_{item.id}"):
                        deal.esap_items = [i for i in deal.esap_items if i.id != item.id]
                        storage.save(deal)
                        st.rerun()
    else:
        st.info("Aucune action ESAP définie. Ajoutez des actions ci-dessus.")

# =============================================================================
# TAB 3: Conditions DD
# =============================================================================
with tab3:
    st.subheader("Conditions préalables issues de la Due Diligence")
    
    dd_data = deal.get_stage_data(DealStage.DUE_DILIGENCE)
    
    if dd_data and dd_data.conditions:
        st.warning(f"⚠️ **{len(dd_data.conditions)} condition(s) préalable(s)** identifiée(s) lors de la DD")
        
        for i, condition in enumerate(dd_data.conditions, 1):
            st.markdown(f"**{i}.** {condition}")
        
        st.markdown("---")
        st.caption("Ces conditions doivent être levées ou intégrées à l'ESAP avant closing.")
    else:
        st.success("✅ Aucune condition préalable identifiée lors de la DD.")
    
    # Afficher la synthèse DD
    if dd_data and dd_data.decision_rationale:
        st.markdown("---")
        st.markdown("### 📝 Synthèse DD")
        st.markdown(dd_data.decision_rationale)

# =============================================================================
# TAB 4: Décision
# =============================================================================
with tab4:
    st.subheader("Décision du Comité d'Investissement")
    
    stage_data = deal.get_current_stage_data()
    
    # Vérifications pré-décision
    st.markdown("### ✅ Vérifications")
    
    checks = {
        "Mémo ESG généré": stage_data.analysis_result is not None,
        "ESAP défini": len(deal.esap_items) > 0,
        "Conditions DD traitées": True  # À personnaliser selon les besoins
    }
    
    for check, passed in checks.items():
        icon = "✅" if passed else "⚠️"
        st.markdown(f"{icon} {check}")
    
    st.markdown("---")
    
    # Décision
    st.markdown("### 📋 Décision IC")
    
    decision = st.radio(
        "Décision du Comité",
        [
            "APPROVED - Investissement approuvé",
            "APPROVED_WITH_CONDITIONS - Approuvé sous conditions",
            "REJECTED - Investissement rejeté"
        ],
        key="ic_decision"
    )
    
    rationale = st.text_area(
        "Commentaires du Comité",
        placeholder="Notes et observations du Comité d'Investissement",
        key="ic_rationale"
    )
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("✅ Enregistrer la décision", type="primary", use_container_width=True):
            stage_data = deal.get_current_stage_data()
            
            if "REJECTED" in decision:
                deal.reject(rationale)
                storage.save(deal)
                st.error("❌ Investissement rejeté par le Comité")
            else:
                stage_data.decision = "APPROVED" if "APPROVED -" in decision else "APPROVED_WITH_CONDITIONS"
                stage_data.decision_rationale = rationale
                stage_data.status = DealStatus.APPROVED
                stage_data.completed_at = datetime.now()
                storage.save(deal)
                st.success("✅ Décision enregistrée !")
                st.balloons()
    
    with col2:
        if stage_data and stage_data.status == DealStatus.APPROVED:
            if st.button("🚀 Passer en Monitoring", use_container_width=True):
                try:
                    deal.advance_stage(DealStage.MONITORING)
                    storage.save(deal)
                    st.success("✅ Deal passé en Monitoring !")
                    st.rerun()
                except ValueError as e:
                    st.error(f"Erreur : {e}")

# Footer
st.markdown("---")
st.caption("ESG Analyzer v2.3 | Investment Committee")
