"""
Page Due Diligence - Analyse terrain approfondie et vérification des points de contrôle.
"""
import streamlit as st
from datetime import datetime

from models.deal import Deal, DealStage, DealStatus
from services.deal_storage import get_deal_storage
from config.dd_checklists import generate_dd_checklist, get_checklist_summary
from config.countries import IPAE3_COUNTRIES
from formatters.checklist_formatter import export_checklist_to_excel

st.set_page_config(
    page_title="Due Diligence - ESG Analyzer",
    page_icon="📋",
    layout="wide"
)

# Initialiser le storage
storage = get_deal_storage()

# Header
st.title("📋 Due Diligence")
st.markdown("Analyse terrain et vérification des points de contrôle ESG")

st.markdown("---")

# Récupérer les deals en DD
dd_deals = storage.get_by_stage(DealStage.DUE_DILIGENCE)

# Aussi récupérer les deals screening approuvés qui peuvent passer en DD
screening_approved = storage.get_by_status(DealStage.SCREENING, DealStatus.APPROVED)

# Section: Deals prêts à passer en DD
if screening_approved:
    st.info(f"📥 **{len(screening_approved)} deal(s)** approuvé(s) au screening, prêts pour la DD")
    
    with st.expander("Voir les deals prêts pour DD"):
        for deal in screening_approved:
            col1, col2, col3 = st.columns([3, 1, 1])
            
            with col1:
                st.markdown(f"**{deal.company_name}** — {deal.country} — {deal.sector}")
            
            with col2:
                st.markdown(f"Cat. {deal.risk_category}")
            
            with col3:
                if st.button(f"▶️ Démarrer DD", key=f"start_dd_{deal.id}"):
                    try:
                        deal.advance_stage(DealStage.DUE_DILIGENCE)
                        storage.save(deal)
                        st.success(f"DD démarrée pour {deal.company_name}")
                        st.rerun()
                    except ValueError as e:
                        st.error(f"Erreur : {e}")
    
    st.markdown("---")

# Vérifier s'il y a des deals en DD
if not dd_deals:
    st.warning("📭 Aucun deal en Due Diligence actuellement.")
    st.info("💡 Approuvez des deals au Screening pour les passer en DD.")
    st.stop()

# Sélectionner un deal
st.subheader("Sélectionner un deal")

selected_deal_id = st.selectbox(
    "Deal",
    options=[d.id for d in dd_deals],
    format_func=lambda x: f"{storage.get(x).company_name} ({x})",
    key="dd_deal_selector"
)

deal = storage.get(selected_deal_id)

if not deal:
    st.error("Deal non trouvé")
    st.stop()

# Afficher les infos du deal
st.markdown("---")
st.header(f"📋 DD - {deal.company_name}")

# Info résumé
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Pays", deal.country)
with col2:
    st.metric("Secteur", deal.sector)
with col3:
    risk_info_color = {"A": "🔴", "B+": "🟠", "B-": "🟡", "C": "🟢"}.get(deal.risk_category, "⚪")
    st.metric("Risque", f"{risk_info_color} Cat. {deal.risk_category}")
with col4:
    st.metric("2X", "✅" if deal.two_x_eligible else "❌")

st.markdown("---")

# Tabs pour la DD
tab1, tab2, tab3, tab4 = st.tabs(["📋 Checklist", "📄 Documents", "📝 Notes", "✅ Validation"])

# =============================================================================
# TAB 1: Checklist DD
# =============================================================================
with tab1:
    st.subheader("Checklist Due Diligence")
    
    # Générer la checklist personnalisée
    country_info = IPAE3_COUNTRIES.get(deal.country, {})
    
    # Récupérer les gaps 2X pour ajouter des questions
    two_x_gaps = []
    if not deal.two_x_eligible:
        from config.two_x_challenge import calculate_2x_eligibility
        result = calculate_2x_eligibility(deal.two_x_data, deal.sector)
        two_x_gaps = result.get("recommendations", [])
    
    checklist = generate_dd_checklist(
        sector=deal.sector,
        risk_category=deal.risk_category,
        country_fragile=country_info.get('fragile', False),
        country_ldc=country_info.get('ldc', False),
        two_x_gaps=two_x_gaps
    )
    
    summary = get_checklist_summary(checklist)
    
    # Métriques checklist
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total points", summary['total'])
    with col2:
        st.metric("Haute priorité", summary['high_priority_count'])
    with col3:
        st.metric("Catégories", len(summary['by_category']))
    with col4:
        # Export Excel
        excel_buffer = export_checklist_to_excel(
            checklist, deal.company_name, deal.sector, 
            deal.risk_category, deal.country
        )
        st.download_button(
            "📥 Export Excel",
            excel_buffer,
            f"checklist_dd_{deal.id}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    
    st.markdown("---")
    
    # Récupérer ou initialiser le statut de la checklist
    stage_data = deal.get_current_stage_data()
    if not stage_data.checklist_status:
        stage_data.checklist_status = {item['id']: 'pending' for item in checklist}
    
    # Afficher la checklist par catégorie
    categories = {}
    for item in checklist:
        cat = item['category']
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(item)
    
    for cat_name, items in categories.items():
        with st.expander(f"**{cat_name}** ({len(items)} points)", expanded=True):
            for item in items:
                col1, col2, col3 = st.columns([4, 1, 1])
                
                with col1:
                    priority_icon = {"high": "🔴", "medium": "🟠", "low": "🟢"}.get(item['priority'], "")
                    st.markdown(f"{priority_icon} **{item['question']}**")
                    st.caption(f"📎 Documents: {', '.join(item['documents'][:2])}{'...' if len(item['documents']) > 2 else ''}")
                
                with col2:
                    current_status = stage_data.checklist_status.get(item['id'], 'pending')
                    status_options = ["pending", "conforme", "partiel", "non_conforme", "na"]
                    status_labels = {
                        "pending": "⏳ À vérifier",
                        "conforme": "✅ Conforme",
                        "partiel": "⚠️ Partiel",
                        "non_conforme": "❌ Non conforme",
                        "na": "➖ N/A"
                    }
                    
                    new_status = st.selectbox(
                        "Statut",
                        options=status_options,
                        index=status_options.index(current_status),
                        format_func=lambda x: status_labels[x],
                        key=f"status_{item['id']}",
                        label_visibility="collapsed"
                    )
                    
                    if new_status != current_status:
                        stage_data.checklist_status[item['id']] = new_status
                
                with col3:
                    st.caption(f"PS{item.get('ifc_standard', 'N/A')}")
    
    # Bouton sauvegarder
    if st.button("💾 Sauvegarder la progression", type="primary", use_container_width=True):
        storage.save(deal)
        st.success("✅ Progression sauvegardée !")
    
    # Statistiques de complétion
    st.markdown("---")
    st.markdown("### 📊 Progression")
    
    total_items = len(stage_data.checklist_status)
    completed_items = sum(1 for v in stage_data.checklist_status.values() if v in ['conforme', 'na'])
    progress = completed_items / total_items if total_items > 0 else 0
    
    st.progress(progress)
    st.caption(f"{completed_items}/{total_items} points traités ({progress*100:.0f}%)")

# =============================================================================
# TAB 2: Documents
# =============================================================================
with tab2:
    st.subheader("Documents collectés")
    
    # Upload de documents
    uploaded_files = st.file_uploader(
        "Ajouter des documents",
        accept_multiple_files=True,
        type=["pdf", "docx", "xlsx", "jpg", "png"],
        key="dd_doc_upload"
    )
    
    if uploaded_files:
        for f in uploaded_files:
            # Vérifier si le document existe déjà
            existing = [d for d in deal.uploaded_documents if d.get('name') == f.name]
            if not existing:
                deal.uploaded_documents.append({
                    "name": f.name,
                    "uploaded_at": datetime.now().isoformat(),
                    "size": len(f.getvalue()),
                    "stage": "due_diligence"
                })
        
        storage.save(deal)
        st.success(f"✅ {len(uploaded_files)} document(s) ajouté(s)")
    
    # Liste des documents
    st.markdown("---")
    st.markdown("### Documents enregistrés")
    
    if deal.uploaded_documents:
        for doc in deal.uploaded_documents:
            col1, col2, col3 = st.columns([3, 1, 1])
            
            with col1:
                st.markdown(f"📄 **{doc['name']}**")
            with col2:
                st.caption(f"Ajouté le {doc.get('uploaded_at', 'N/A')[:10]}")
            with col3:
                st.caption(f"Stage: {doc.get('stage', 'N/A')}")
    else:
        st.info("Aucun document enregistré pour ce deal.")

# =============================================================================
# TAB 3: Notes
# =============================================================================
with tab3:
    st.subheader("Notes et observations")
    
    # Ajouter une note
    new_comment = st.text_area(
        "Nouvelle note",
        placeholder="Ajoutez vos observations de la visite terrain, points d'attention, etc.",
        key="dd_new_note"
    )
    
    if st.button("💬 Ajouter la note") and new_comment:
        deal.add_comment(new_comment, "Analyste DD")
        storage.save(deal)
        st.success("Note ajoutée !")
        st.rerun()
    
    # Afficher les notes existantes
    st.markdown("---")
    st.markdown("### Historique des notes")
    
    stage_data = deal.get_current_stage_data()
    if stage_data and stage_data.comments:
        for comment in reversed(stage_data.comments):
            st.markdown(f"""
            **{comment.get('author', 'Anonyme')}** — {comment.get('timestamp', 'N/A')[:16]}
            
            {comment.get('text', '')}
            
            ---
            """)
    else:
        st.info("Aucune note pour ce deal.")

# =============================================================================
# TAB 4: Validation
# =============================================================================
with tab4:
    st.subheader("Validation Due Diligence")
    
    stage_data = deal.get_current_stage_data()
    
    # Résumé de la checklist
    if stage_data.checklist_status:
        st.markdown("### 📊 Résumé checklist")
        
        total = len(stage_data.checklist_status)
        conformes = sum(1 for v in stage_data.checklist_status.values() if v == 'conforme')
        partiels = sum(1 for v in stage_data.checklist_status.values() if v == 'partiel')
        non_conformes = sum(1 for v in stage_data.checklist_status.values() if v == 'non_conforme')
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Conformes", conformes, delta=None)
        with col2:
            st.metric("Partiels", partiels, delta=None)
        with col3:
            st.metric("Non conformes", non_conformes, delta=None)
        with col4:
            rate = (conformes / total * 100) if total > 0 else 0
            st.metric("Taux conformité", f"{rate:.0f}%")
    
    st.markdown("---")
    
    # Décision
    st.markdown("### 📋 Décision DD")
    
    decision = st.radio(
        "Recommandation",
        [
            "GO - Passer au Comité d'Investissement",
            "GO avec conditions - Conditions préalables requises",
            "NO-GO - Rejeter l'opportunité"
        ],
        key="dd_decision"
    )
    
    # Conditions si applicable
    conditions_text = ""
    if "conditions" in decision.lower():
        st.markdown("**Conditions préalables à l'investissement :**")
        conditions_text = st.text_area(
            "Liste des conditions (une par ligne)",
            placeholder="Ex:\n- Mise en place d'une politique HSE\n- Formation du personnel\n- Obtention du permis environnemental",
            key="dd_conditions"
        )
    
    rationale = st.text_area(
        "Synthèse et justification",
        placeholder="Résumez les points clés de la DD et justifiez votre recommandation",
        key="dd_rationale"
    )
    
    st.markdown("---")
    
    # Boutons d'action
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("✅ Valider la DD", type="primary", use_container_width=True):
            stage_data = deal.get_current_stage_data()
            
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
                st.success("✅ Due Diligence validée !")
                st.balloons()
    
    with col2:
        # Vérifier si on peut avancer
        if stage_data and stage_data.status == DealStatus.APPROVED:
            if st.button("🚀 Passer au Comité d'Investissement", use_container_width=True):
                try:
                    deal.advance_stage(DealStage.INVESTMENT_COMMITTEE)
                    storage.save(deal)
                    st.success("Deal avancé au Comité d'Investissement !")
                    st.rerun()
                except ValueError as e:
                    st.error(f"Erreur : {e}")

# Footer
st.markdown("---")
st.caption("ESG Analyzer v2.3 | Due Diligence")
