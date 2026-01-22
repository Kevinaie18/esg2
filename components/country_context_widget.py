"""
Widget Streamlit pour afficher le contexte pays enrichi.
Affiche les informations réglementaires, climat, genre et macro-économiques.
"""

import streamlit as st
from typing import Dict, Optional


def render_country_context_widget(country: str, countries_data: Dict):
    """
    Affiche le widget de contexte pays avec onglets.
    
    Args:
        country: Nom du pays sélectionné
        countries_data: Dictionnaire des données pays (depuis config/countries.py)
    """
    ctx = countries_data.get(country, {})
    
    if not ctx or country == "Autre":
        st.info(f"ℹ️ Contexte détaillé non disponible pour {country}")
        return
    
    st.markdown(f"### 🌍 Contexte pays : {country}")
    
    # Indicateurs clés en haut
    _render_key_indicators(ctx, country)
    
    st.markdown("")
    
    # Onglets détaillés
    if any([ctx.get("regulatory_context"), ctx.get("climate_risks"), 
            ctx.get("gender_context"), ctx.get("macro_indicators")]):
        
        tabs = st.tabs(["📋 Réglementation", "🌡️ Climat", "👩 Genre", "📈 Macro"])
        
        with tabs[0]:
            _render_regulatory_tab(ctx.get("regulatory_context", {}))
        
        with tabs[1]:
            _render_climate_tab(ctx.get("climate_risks", {}))
        
        with tabs[2]:
            _render_gender_tab(ctx.get("gender_context", {}))
        
        with tabs[3]:
            _render_macro_tab(ctx.get("macro_indicators", {}))
        
        # Contexte sécurité si pays fragile
        if ctx.get("security_context"):
            with st.expander("⚠️ Contexte sécuritaire", expanded=False):
                _render_security_context(ctx["security_context"])


def _render_key_indicators(ctx: Dict, country: str):
    """Affiche les indicateurs clés en haut du widget."""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if ctx.get("ldc"):
            st.markdown("🔸 **PMA**")
            st.caption("Pays Moins Avancé")
        else:
            st.markdown("✅ **Non-PMA**")
    
    with col2:
        if ctx.get("fragile"):
            st.markdown("⚠️ **État fragile**")
            st.caption("Vigilance renforcée")
        else:
            st.markdown("✅ **Stable**")
    
    with col3:
        climate = ctx.get("climate_risks", {})
        exposure = climate.get("exposure", "N/A")
        color_map = {
            "Très élevé": "🔴",
            "Élevé": "🟠", 
            "Moyen": "🟡",
            "Faible": "🟢"
        }
        icon = color_map.get(exposure, "⚪")
        st.markdown(f"{icon} **Risque climat**")
        st.caption(exposure)
    
    with col4:
        macro = ctx.get("macro_indicators", {})
        rank = macro.get("ease_of_business_rank", "N/A")
        st.markdown(f"📊 **Doing Business**")
        st.caption(f"Rang #{rank}")


def _render_regulatory_tab(reg: Dict):
    """Affiche l'onglet réglementation."""
    if not reg:
        st.info("Données réglementaires non disponibles")
        return
    
    st.markdown(f"""
    **Agence environnementale :** {reg.get('environmental_agency', 'N/A')}
    
    **Étude d'impact environnemental (EIE) :**
    - Obligatoire : {'✅ Oui' if reg.get('eie_required') else '❌ Non'}
    - Seuil : {reg.get('eie_threshold', 'N/A')}
    """)
    
    st.markdown("---")
    
    st.markdown(f"""
    **Droit du travail :**
    - Code : {reg.get('labor_code', 'N/A')}
    - Salaire minimum : {reg.get('minimum_wage', 'N/A')}
    - Sécurité sociale : {reg.get('social_security', 'N/A')}
    """)
    
    if reg.get('key_regulations'):
        st.markdown("---")
        st.markdown("**Réglementations clés :**")
        for r in reg['key_regulations']:
            st.markdown(f"- 📜 {r}")


def _render_climate_tab(climate: Dict):
    """Affiche l'onglet climat."""
    if not climate:
        st.info("Données climatiques non disponibles")
        return
    
    exposure = climate.get('exposure', 'N/A')
    exposure_colors = {
        "Très élevé": "#dc3545",
        "Élevé": "#fd7e14",
        "Moyen": "#ffc107",
        "Faible": "#28a745"
    }
    color = exposure_colors.get(exposure, "#6c757d")
    
    st.markdown(f"""
    <div style="background-color: {color}20; border-left: 4px solid {color}; 
                padding: 10px; border-radius: 4px; margin-bottom: 15px;">
        <strong>Niveau d'exposition : {exposure}</strong>
    </div>
    """, unsafe_allow_html=True)
    
    if climate.get('main_risks'):
        st.markdown("**Risques principaux :**")
        for risk in climate['main_risks']:
            st.markdown(f"- 🔶 {risk}")
    
    if climate.get('vulnerable_sectors'):
        st.markdown("")
        st.markdown("**Secteurs vulnérables :**")
        for sector in climate['vulnerable_sectors']:
            st.markdown(f"- {sector}")
    
    if climate.get('ndc_target'):
        st.markdown("")
        st.markdown(f"**🎯 Objectif NDC :** {climate['ndc_target']}")


def _render_gender_tab(gender: Dict):
    """Affiche l'onglet genre."""
    if not gender:
        st.info("Données genre non disponibles")
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        participation = gender.get('women_labor_participation', 'N/A')
        st.metric("Participation femmes au marché du travail", participation)
    
    with col2:
        rank = gender.get('gender_gap_index_rank', 'N/A')
        st.metric("Classement Gender Gap Index", f"#{rank}")
    
    st.markdown("---")
    
    if gender.get('key_challenges'):
        st.markdown("**⚠️ Défis principaux :**")
        for challenge in gender['key_challenges']:
            st.markdown(f"- {challenge}")
    
    if gender.get('positive_factors'):
        st.markdown("")
        st.markdown("**✅ Facteurs positifs :**")
        for factor in gender['positive_factors']:
            st.markdown(f"- {factor}")


def _render_macro_tab(macro: Dict):
    """Affiche l'onglet macro-économique."""
    if not macro:
        st.info("Données macro-économiques non disponibles")
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
        **📊 Indicateurs clés**
        
        - **Population :** {macro.get('population', 'N/A')}
        - **Croissance PIB :** {macro.get('gdp_growth_2023', 'N/A')}
        - **Inflation :** {macro.get('inflation_2023', 'N/A')}
        """)
    
    with col2:
        st.markdown(f"""
        **💼 Environnement business**
        
        - **Monnaie :** {macro.get('currency', 'N/A')}
        - **Doing Business :** #{macro.get('ease_of_business_rank', 'N/A')}
        """)
    
    if macro.get('main_exports'):
        st.markdown("")
        st.markdown(f"**📦 Exports principaux :** {', '.join(macro['main_exports'])}")


def _render_security_context(security: Dict):
    """Affiche le contexte sécuritaire pour les pays fragiles."""
    risk_level = security.get('risk_level', 'N/A')
    
    risk_colors = {
        "Très élevé": "#dc3545",
        "Élevé": "#fd7e14",
        "Modéré": "#ffc107"
    }
    color = risk_colors.get(risk_level, "#6c757d")
    
    st.markdown(f"""
    <div style="background-color: {color}20; border-left: 4px solid {color}; 
                padding: 10px; border-radius: 4px;">
        <strong>⚠️ Niveau de risque sécuritaire : {risk_level}</strong>
    </div>
    """, unsafe_allow_html=True)
    
    if security.get('affected_regions'):
        st.markdown("")
        st.markdown(f"**Régions affectées :** {', '.join(security['affected_regions'])}")
    
    if security.get('recommendations'):
        st.markdown("")
        st.markdown("**Recommandations DD :**")
        for rec in security['recommendations']:
            st.markdown(f"- 📌 {rec}")


def render_country_context_summary(country: str, countries_data: Dict) -> str:
    """
    Génère un résumé textuel du contexte pays pour injection dans les prompts.
    
    Returns:
        String formaté avec le contexte pays
    """
    ctx = countries_data.get(country, {})
    
    if not ctx or country == "Autre":
        return f"Pays : {country} (contexte détaillé non disponible)"
    
    parts = []
    
    # En-tête
    parts.append(f"CONTEXTE PAYS - {country}")
    parts.append(f"Région : {ctx.get('region', 'N/A')}")
    
    indicators = []
    if ctx.get('ldc'):
        indicators.append("Pays Moins Avancé (PMA)")
    if ctx.get('fragile'):
        indicators.append("État fragile")
    if indicators:
        parts.append(f"Statut : {', '.join(indicators)}")
    
    # Réglementation
    reg = ctx.get('regulatory_context', {})
    if reg:
        parts.append("")
        parts.append("RÉGLEMENTATION :")
        parts.append(f"- Agence environnementale : {reg.get('environmental_agency', 'N/A')}")
        parts.append(f"- EIE obligatoire : {'Oui' if reg.get('eie_required') else 'Non'}")
        parts.append(f"- Code du travail : {reg.get('labor_code', 'N/A')}")
        parts.append(f"- Salaire minimum : {reg.get('minimum_wage', 'N/A')}")
    
    # Climat
    climate = ctx.get('climate_risks', {})
    if climate:
        parts.append("")
        parts.append("RISQUES CLIMAT :")
        parts.append(f"- Exposition : {climate.get('exposure', 'N/A')}")
        if climate.get('main_risks'):
            parts.append(f"- Risques : {', '.join(climate['main_risks'])}")
        if climate.get('ndc_target'):
            parts.append(f"- Objectif NDC : {climate['ndc_target']}")
    
    # Genre
    gender = ctx.get('gender_context', {})
    if gender:
        parts.append("")
        parts.append("CONTEXTE GENRE :")
        parts.append(f"- Participation femmes au travail : {gender.get('women_labor_participation', 'N/A')}")
        parts.append(f"- Rang Gender Gap Index : {gender.get('gender_gap_index_rank', 'N/A')}")
    
    # Sécurité
    security = ctx.get('security_context', {})
    if security:
        parts.append("")
        parts.append("CONTEXTE SÉCURITAIRE :")
        parts.append(f"- Niveau de risque : {security.get('risk_level', 'N/A')}")
        if security.get('affected_regions'):
            parts.append(f"- Régions affectées : {', '.join(security['affected_regions'])}")
    
    return "\n".join(parts)


def render_country_mini_badge(country: str, countries_data: Dict):
    """
    Affiche un mini badge avec les indicateurs clés du pays.
    À utiliser à côté du dropdown de sélection de pays.
    """
    ctx = countries_data.get(country, {})
    
    if not ctx or country == "Autre":
        return
    
    badges = []
    
    if ctx.get('ldc'):
        badges.append("🔸 PMA")
    
    if ctx.get('fragile'):
        badges.append("⚠️ Fragile")
    
    region = ctx.get('region', '')
    if region:
        badges.insert(0, f"📍 {region}")
    
    if badges:
        st.caption(" | ".join(badges))
