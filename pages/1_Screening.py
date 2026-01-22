"""
Page Screening - Première évaluation rapide des opportunités d'investissement.
"""
import streamlit as st
from datetime import datetime

from models.deal import Deal, DealStage, DealStatus, StageData
from services.deal_storage import get_deal_storage
from config.risk_classification import get_sectors, get_subsectors, get_risk_category, get_risk_display
from config.countries import IPAE3_COUNTRIES
from config.two_x_challenge import calculate_2x_eligibility, get_threshold

st.set_page_config(
    page_title="Screening - ESG Analyzer",
    page_icon="🔍",
    layout="wide"
)

# Initialiser le storage
storage = get_deal_storage()

# Header
st.title("🔍 Screening")
st.markdown("Évaluation rapide des nouvelles opportunités d'investissement")

st.markdown("---")

# Tabs : Nouveau deal / Deals en screening
tab1, tab2 = st.tabs(["➕ Nouveau deal", "📋 Deals en screening"])

# =============================================================================
# TAB 1: Nouveau deal
# =============================================================================
with tab1:
    st.header("Nouvelle opportunité")
    
    with st.form("screening_form"):
        # Row 1: Infos de base
        col1, col2, col3 = st.columns(3)
        
        with col1:
            company_name = st.text_input(
                "Nom de l'entreprise *",
                placeholder="Ex: AgroCorp SARL"
            )
        
        with col2:
            country = st.selectbox(
                "Pays *",
                options=list(IPAE3_COUNTRIES.keys()),
                index=0
            )
            # Afficher indicateurs pays
            ctx = IPAE3_COUNTRIES.get(country, {})
            if ctx and country != "Autre":
                indicators = []
                if ctx.get('ldc'):
                    indicators.append("🔸 PMA")
                if ctx.get('fragile'):
                    indicators.append("⚠️ Fragile")
                if indicators:
                    st.caption(f"📍 {ctx.get('region', '')} | {' '.join(indicators)}")
        
        with col3:
            sector = st.selectbox(
                "Secteur *",
                options=get_sectors()
            )
        
        # Row 2: Sous-secteur et risque
        col1, col2 = st.columns(2)
        
        with col1:
            subsector_options = get_subsectors(sector)
            subsector = st.selectbox(
                "Sous-secteur *",
                options=subsector_options if subsector_options else ["Non spécifié"]
            )
        
        with col2:
            risk_cat = get_risk_category(sector, subsector)
            risk_info = get_risk_display(risk_cat)
            
            st.markdown(f"""
            **Classification E&S préliminaire**
            
            {risk_info['color']} **Catégorie {risk_cat}** — {risk_info['name']}
            """)
        
        # Row 3: Description
        description = st.text_area(
            "Description de l'activité *",
            placeholder="Ex: Production et distribution de produits laitiers frais",
            height=80
        )
        
        # Row 4: Données quantitatives
        col1, col2, col3 = st.columns(3)
        
        with col1:
            employees = st.number_input("Nombre d'employés", min_value=1, max_value=50000, value=50)
        
        with col2:
            revenue = st.selectbox(
                "CA annuel (EUR)",
                ["< 500K", "500K - 2M", "2M - 5M", "5M - 10M", "10M - 50M", "> 50M"]
            )
        
        with col3:
            target_market = st.selectbox(
                "Marché cible",
                ["B2C - Particuliers", "B2B - Entreprises", "B2B2C - Les deux", "B2G - Institutions"]
            )
        
        st.markdown("---")
        
        # Row 5: Évaluation 2X Challenge rapide
        st.subheader("🎯 Évaluation 2X Challenge rapide")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            women_ownership = st.slider(
                "% Détention femmes",
                min_value=0,
                max_value=100,
                value=0,
                help="Pourcentage du capital détenu par des femmes"
            )
        
        with col2:
            women_management = st.slider(
                "% Management femmes",
                min_value=0,
                max_value=100,
                value=20,
                help="Pourcentage de femmes au management"
            )
        
        with col3:
            women_employees = st.slider(
                "% Employées femmes",
                min_value=0,
                max_value=100,
                value=30,
                help="Pourcentage de femmes dans l'effectif"
            )
        
        with col4:
            benefits_women = st.checkbox(
                "Produit pour femmes",
                help="Le produit/service bénéficie spécifiquement aux femmes"
            )
        
        # Calcul 2X en temps réel
        two_x_data = {
            "women_ownership_pct": women_ownership,
            "women_management_pct": women_management,
            "women_employees_pct": women_employees,
            "benefits_women": benefits_women
        }
        two_x_result = calculate_2x_eligibility(two_x_data, sector)
        
        # Afficher résultat 2X
        if two_x_result["eligible"]:
            st.success(f"✅ **Éligible 2X Challenge** ({two_x_result['criteria_met']}/4 critères)")
        else:
            st.warning(f"❌ **Non éligible 2X** (0/4 critères)")
            if two_x_result.get("recommendations"):
                rec = two_x_result["recommendations"][0]
                st.caption(f"💡 Action prioritaire : {rec['action']} ({rec['gap']})")
        
        st.markdown("---")
        
        # Submit
        submitted = st.form_submit_button(
            "🚀 Créer le deal",
            use_container_width=True,
            type="primary"
        )
    
    # Traitement du formulaire
    if submitted:
        if not company_name:
            st.error("❌ Veuillez entrer le nom de l'entreprise.")
        elif not description:
            st.error("❌ Veuillez décrire l'activité.")
        else:
            # Créer le deal
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
            
            # Créer le stage data initial
            deal.stage_history[DealStage.SCREENING.value] = StageData(
                stage=DealStage.SCREENING,
                status=DealStatus.IN_PROGRESS,
                started_at=datetime.now()
            )
            
            # Sauvegarder
            if storage.save(deal):
                st.success(f"✅ Deal créé avec succès ! ID: **{deal.id}**")
                
                # Afficher résumé
                st.markdown("### 📋 Résumé")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Classification E&S", f"Cat. {deal.risk_category}")
                with col2:
                    st.metric("2X Challenge", "✅ Éligible" if deal.two_x_eligible else "❌ Non éligible")
                with col3:
                    st.metric("Critères 2X", f"{deal.two_x_criteria_met}/4")
                
                # Section décision
                st.markdown("---")
                st.markdown("### 📋 Décision Screening")
                
                decision = st.radio(
                    "Recommandation",
                    ["GO - Passer en Due Diligence", "NO-GO - Rejeter l'opportunité", "ON HOLD - À revoir ultérieurement"],
                    horizontal=True
                )
                
                rationale = st.text_area("Justification de la décision")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.button("✅ Valider la décision", type="primary", use_container_width=True):
                        stage_data = deal.get_current_stage_data()
                        
                        if "GO -" in decision:
                            stage_data.decision = "GO"
                            stage_data.status = DealStatus.APPROVED
                            stage_data.decision_rationale = rationale
                            storage.save(deal)
                            st.success("✅ Deal approuvé pour Due Diligence !")
                            st.balloons()
                        
                        elif "NO-GO" in decision:
                            deal.reject(rationale)
                            storage.save(deal)
                            st.error("❌ Deal rejeté")
                        
                        else:  # ON HOLD
                            stage_data.status = DealStatus.ON_HOLD
                            stage_data.decision = "ON_HOLD"
                            stage_data.decision_rationale = rationale
                            storage.save(deal)
                            st.warning("⏸️ Deal mis en attente")
            else:
                st.error("❌ Erreur lors de la sauvegarde du deal.")

# =============================================================================
# TAB 2: Deals en screening
# =============================================================================
with tab2:
    st.header("Deals en screening")
    
    # Récupérer les deals en screening
    screening_deals = storage.get_by_stage(DealStage.SCREENING)
    
    if not screening_deals:
        st.info("📭 Aucun deal en screening actuellement.")
    else:
        # Filtres
        col1, col2 = st.columns([1, 3])
        with col1:
            status_filter = st.selectbox(
                "Filtrer par statut",
                ["Tous", "En cours", "En attente", "Approuvés"],
                index=0
            )
        
        # Filtrer
        if status_filter == "En cours":
            screening_deals = [d for d in screening_deals if d.get_current_stage_data() and d.get_current_stage_data().status == DealStatus.IN_PROGRESS]
        elif status_filter == "En attente":
            screening_deals = [d for d in screening_deals if d.get_current_stage_data() and d.get_current_stage_data().status == DealStatus.ON_HOLD]
        elif status_filter == "Approuvés":
            screening_deals = [d for d in screening_deals if d.get_current_stage_data() and d.get_current_stage_data().status == DealStatus.APPROVED]
        
        st.markdown(f"**{len(screening_deals)} deal(s) trouvé(s)**")
        
        # Afficher les deals
        for deal in screening_deals:
            stage_data = deal.get_current_stage_data()
            status_icon = {
                DealStatus.IN_PROGRESS: "🔄",
                DealStatus.ON_HOLD: "⏸️",
                DealStatus.APPROVED: "✅",
                DealStatus.PENDING_REVIEW: "👀"
            }.get(stage_data.status if stage_data else None, "❓")
            
            with st.expander(f"{status_icon} **{deal.company_name}** — {deal.country} — {deal.sector}"):
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.markdown(f"**ID:** `{deal.id}`")
                    st.markdown(f"**Créé le:** {deal.created_at.strftime('%d/%m/%Y')}")
                
                with col2:
                    st.markdown(f"**Risque:** Cat. {deal.risk_category}")
                    st.markdown(f"**Employés:** {deal.employees}")
                
                with col3:
                    st.markdown(f"**2X:** {'✅ Éligible' if deal.two_x_eligible else '❌ Non éligible'}")
                    st.markdown(f"**Critères:** {deal.two_x_criteria_met}/4")
                
                with col4:
                    st.markdown(f"**CA:** {deal.revenue}")
                    st.markdown(f"**Marché:** {deal.target_market}")
                
                st.markdown(f"**Description:** {deal.description[:200]}...")
                
                # Actions
                st.markdown("---")
                
                if stage_data and stage_data.status == DealStatus.APPROVED:
                    st.success("✅ Ce deal est approuvé et prêt pour la Due Diligence.")
                    
                    if st.button(f"🚀 Passer en DD", key=f"advance_{deal.id}"):
                        try:
                            deal.advance_stage(DealStage.DUE_DILIGENCE)
                            storage.save(deal)
                            st.success("Deal avancé en Due Diligence !")
                            st.rerun()
                        except ValueError as e:
                            st.error(f"Erreur : {e}")
                
                elif stage_data and stage_data.status == DealStatus.IN_PROGRESS:
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        if st.button("✅ Approuver (GO)", key=f"approve_{deal.id}"):
                            stage_data.decision = "GO"
                            stage_data.status = DealStatus.APPROVED
                            storage.save(deal)
                            st.rerun()
                    
                    with col2:
                        if st.button("❌ Rejeter (NO-GO)", key=f"reject_{deal.id}"):
                            deal.reject("Rejeté depuis la liste")
                            storage.save(deal)
                            st.rerun()
                    
                    with col3:
                        if st.button("⏸️ Mettre en attente", key=f"hold_{deal.id}"):
                            stage_data.status = DealStatus.ON_HOLD
                            storage.save(deal)
                            st.rerun()

# Footer
st.markdown("---")
st.caption("ESG Analyzer v2.3 | Screening")
