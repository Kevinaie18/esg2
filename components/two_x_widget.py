"""
Widget Streamlit interactif pour le scoring 2X Challenge.
Affiche les 4 critères avec évaluation en temps réel.
"""
import streamlit as st
from typing import Dict, Tuple

from config.two_x_challenge import (
    TWO_X_CRITERIA,
    calculate_2x_eligibility,
    get_threshold,
    get_threshold_display,
    get_2x_action_plan
)


def render_2x_challenge_widget(sector: str, key_prefix: str = "2x") -> Dict:
    """
    Affiche le widget 2X Challenge et retourne les données collectées.
    
    Args:
        sector: Secteur de l'entreprise (pour les seuils adaptés)
        key_prefix: Préfixe pour les clés Streamlit (évite les conflits)
    
    Returns:
        {
            "data": {données collectées},
            "result": {résultat du calcul d'éligibilité}
        }
    """
    st.markdown("### 🎯 Évaluation 2X Challenge")
    st.caption(
        "Le 2X Challenge mesure l'impact genre de l'investissement. "
        "**1 critère validé = éligible.** Les seuils varient selon le secteur."
    )
    
    data = {}
    
    # Container pour les critères
    st.markdown("---")
    
    # =========================================================================
    # Critère 1: Entrepreneuriat
    # =========================================================================
    st.markdown(f"**{TWO_X_CRITERIA['entrepreneurship']['icon']} 1. Entrepreneuriat** — Fondatrice/Propriétaire femme")
    
    col1, col2, col3 = st.columns([2, 2, 1])
    
    with col1:
        women_ownership = st.slider(
            "Détention du capital par des femmes (%)",
            min_value=0,
            max_value=100,
            value=0,
            key=f"{key_prefix}_ownership",
            help=TWO_X_CRITERIA["entrepreneurship"]["help"]
        )
    
    with col2:
        threshold = get_threshold("entrepreneurship", sector)
        threshold_pct = int(threshold * 100)
        st.caption(f"Seuil requis : **≥{threshold_pct}%**")
        
        # Barre de progression visuelle
        progress = min(women_ownership / threshold_pct, 1.0) if threshold_pct > 0 else 0
        st.progress(progress)
    
    with col3:
        if women_ownership >= threshold_pct:
            st.success("✅ Validé")
        else:
            gap = threshold_pct - women_ownership
            st.error(f"❌ -{gap}%")
    
    data["women_ownership_pct"] = women_ownership
    
    # =========================================================================
    # Critère 2: Leadership
    # =========================================================================
    st.markdown("")
    st.markdown(f"**{TWO_X_CRITERIA['leadership']['icon']} 2. Leadership** — Femmes dans le senior management")
    
    col1, col2, col3 = st.columns([2, 2, 1])
    
    with col1:
        women_management = st.slider(
            "Femmes au management (%)",
            min_value=0,
            max_value=100,
            value=20,
            key=f"{key_prefix}_management",
            help=TWO_X_CRITERIA["leadership"]["help"]
        )
    
    with col2:
        threshold = get_threshold("leadership", sector)
        threshold_pct = int(threshold * 100)
        st.caption(f"Seuil requis ({sector}) : **≥{threshold_pct}%**")
        
        progress = min(women_management / threshold_pct, 1.0) if threshold_pct > 0 else 0
        st.progress(progress)
    
    with col3:
        if women_management >= threshold_pct:
            st.success("✅ Validé")
        else:
            gap = threshold_pct - women_management
            st.error(f"❌ -{gap}%")
    
    data["women_management_pct"] = women_management
    
    # =========================================================================
    # Critère 3: Emploi
    # =========================================================================
    st.markdown("")
    st.markdown(f"**{TWO_X_CRITERIA['employment']['icon']} 3. Emploi** — Femmes dans l'effectif total")
    
    col1, col2, col3 = st.columns([2, 2, 1])
    
    with col1:
        women_employees = st.slider(
            "Femmes employées (%)",
            min_value=0,
            max_value=100,
            value=30,
            key=f"{key_prefix}_employees",
            help=TWO_X_CRITERIA["employment"]["help"]
        )
    
    with col2:
        threshold = get_threshold("employment", sector)
        threshold_pct = int(threshold * 100)
        st.caption(f"Seuil requis ({sector}) : **≥{threshold_pct}%**")
        
        progress = min(women_employees / threshold_pct, 1.0) if threshold_pct > 0 else 0
        st.progress(progress)
    
    with col3:
        if women_employees >= threshold_pct:
            st.success("✅ Validé")
        else:
            gap = threshold_pct - women_employees
            st.error(f"❌ -{gap}%")
    
    data["women_employees_pct"] = women_employees
    
    # =========================================================================
    # Critère 4: Consommation
    # =========================================================================
    st.markdown("")
    st.markdown(f"**{TWO_X_CRITERIA['consumption']['icon']} 4. Consommation** — Produit/service bénéficiant aux femmes")
    
    col1, col2, col3 = st.columns([2, 2, 1])
    
    with col1:
        benefits_women = st.checkbox(
            "Le produit/service bénéficie spécifiquement aux femmes",
            key=f"{key_prefix}_consumption",
            help=TWO_X_CRITERIA["consumption"]["help"]
        )
        
        if benefits_women:
            consumption_detail = st.text_input(
                "Précisez comment",
                placeholder="Ex: Produits de santé maternelle, services financiers pour femmes entrepreneures...",
                key=f"{key_prefix}_consumption_detail"
            )
    
    with col2:
        st.caption("Critère qualitatif")
        if benefits_women:
            st.caption("✓ Le produit/service cible les femmes")
    
    with col3:
        if benefits_women:
            st.success("✅ Validé")
        else:
            st.info("➖ Non")
    
    data["benefits_women"] = benefits_women
    
    # =========================================================================
    # Résultat global
    # =========================================================================
    st.markdown("---")
    
    result = calculate_2x_eligibility(data, sector)
    
    # Affichage du résultat
    if result["eligible"]:
        st.success(f"""
        ## ✅ ÉLIGIBLE 2X Challenge
        
        **{result['criteria_met']}/{result['criteria_total']} critère(s) validé(s)** : {', '.join(result['criteria_met_names'])}
        
        L'entreprise répond aux exigences du 2X Challenge et contribue à l'autonomisation économique des femmes.
        """)
    else:
        st.error(f"""
        ## ❌ NON ÉLIGIBLE 2X Challenge
        
        **0/{result['criteria_total']} critère validé**
        
        L'entreprise ne répond actuellement à aucun des critères 2X Challenge.
        """)
        
        # Afficher les recommandations
        if result["recommendations"]:
            st.markdown("### 📋 Actions recommandées pour devenir éligible")
            
            for i, rec in enumerate(result["recommendations"], 1):
                priority_color = "🔴" if rec["priority"] == "high" else "🟠"
                st.markdown(f"""
                {priority_color} **{i}. {rec['criterion']}**
                - Action : {rec['action']}
                - Actuel : {rec['current']} → Cible : {rec['target']}
                - Écart : {rec['gap']}
                """)
    
    # Tableau récapitulatif
    with st.expander("📊 Voir le détail par critère"):
        cols = st.columns(4)
        for i, (key, detail) in enumerate(result["criteria_details"].items()):
            with cols[i]:
                status = "✅" if detail["met"] else "❌"
                st.markdown(f"""
                **{detail['icon']} {detail['short_name']}**
                
                {status} {'Validé' if detail['met'] else 'Non validé'}
                
                Valeur : {detail['value']:.0f}%
                
                Seuil : {detail['threshold']:.0f}% 
                """ if detail['threshold'] else f"""
                **{detail['icon']} {detail['short_name']}**
                
                {status} {'Validé' if detail['met'] else 'Non validé'}
                
                Qualitatif
                """)
    
    return {
        "data": data,
        "result": result
    }


def render_2x_summary_badge(result: Dict) -> None:
    """
    Affiche un badge résumé 2X Challenge compact.
    À utiliser dans d'autres parties de l'interface.
    """
    if result["eligible"]:
        st.markdown(f"""
        <div style="background-color: #d4edda; padding: 10px; border-radius: 5px; text-align: center;">
            <strong>✅ 2X Challenge : ÉLIGIBLE</strong><br/>
            <small>{result['criteria_met']}/4 critères ({', '.join(result['criteria_met_names'])})</small>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div style="background-color: #f8d7da; padding: 10px; border-radius: 5px; text-align: center;">
            <strong>❌ 2X Challenge : NON ÉLIGIBLE</strong><br/>
            <small>0/4 critères validés</small>
        </div>
        """, unsafe_allow_html=True)
