"""
Composant Streamlit pour l'upload et l'extraction automatique de documents.
Permet de pré-remplir le formulaire à partir d'un business plan ou pitch deck.
"""

import streamlit as st
from typing import Optional, Dict, Tuple
from loguru import logger

from utils.document_extractor import (
    extract_text,
    detect_document_type,
    DocumentType,
    ExtractedData,
    prepare_extraction_prompt,
    get_extraction_system_prompt,
    parse_llm_extraction_response
)


def render_document_upload_widget(
    llm_manager,
    llm_provider: str,
    key_prefix: str = "doc_upload"
) -> Optional[ExtractedData]:
    """
    Affiche le widget d'upload de document et gère l'extraction.
    
    Args:
        llm_manager: Instance du gestionnaire LLM
        llm_provider: Provider LLM à utiliser (openai, anthropic, etc.)
        key_prefix: Préfixe pour les clés Streamlit
    
    Returns:
        ExtractedData si extraction réussie, None sinon
    """
    
    st.markdown("### 📄 Import de document (optionnel)")
    st.caption(
        "Glissez un business plan, pitch deck ou présentation pour pré-remplir automatiquement le formulaire."
    )
    
    # File uploader
    uploaded_file = st.file_uploader(
        "Choisir un document",
        type=["pdf", "docx", "pptx", "txt"],
        help="Formats acceptés : PDF, Word (.docx), PowerPoint (.pptx), Texte (.txt)",
        key=f"{key_prefix}_uploader"
    )
    
    if uploaded_file is None:
        # Retourner les données déjà extraites si présentes
        return st.session_state.get(f'{key_prefix}_extracted_data')
    
    # Afficher les infos du fichier
    doc_type = detect_document_type(uploaded_file.name)
    file_size_kb = len(uploaded_file.getvalue()) / 1024
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"**📁 Fichier:** {uploaded_file.name}")
    with col2:
        type_icons = {
            DocumentType.PDF: "📕 PDF",
            DocumentType.DOCX: "📘 Word",
            DocumentType.PPTX: "📙 PowerPoint",
            DocumentType.TXT: "📄 Texte",
        }
        st.markdown(f"**Type:** {type_icons.get(doc_type, '❓ Inconnu')}")
    with col3:
        st.markdown(f"**Taille:** {file_size_kb:.1f} KB")
    
    # Bouton d'extraction
    col1, col2 = st.columns([1, 3])
    
    with col1:
        extract_button = st.button(
            "🔍 Extraire les données",
            key=f"{key_prefix}_extract_btn",
            type="secondary",
            use_container_width=True
        )
    
    with col2:
        st.caption("L'extraction utilise l'IA pour identifier automatiquement les informations clés.")
    
    # Extraction
    if extract_button:
        extracted = _perform_extraction(
            uploaded_file,
            llm_manager,
            llm_provider,
            key_prefix
        )
        
        if extracted:
            st.session_state[f'{key_prefix}_extracted_data'] = extracted
            return extracted
    
    # Afficher les données déjà extraites
    existing_data = st.session_state.get(f'{key_prefix}_extracted_data')
    if existing_data and existing_data.source_filename == uploaded_file.name:
        _display_extraction_results(existing_data)
        return existing_data
    
    return None


def _perform_extraction(
    uploaded_file,
    llm_manager,
    llm_provider: str,
    key_prefix: str
) -> Optional[ExtractedData]:
    """
    Effectue l'extraction des données du document.
    """
    with st.spinner("🔄 Extraction en cours... (peut prendre 10-30 secondes)"):
        try:
            # 1. Extraire le texte
            file_bytes = uploaded_file.getvalue()
            raw_text = extract_text(file_bytes, uploaded_file.name)
            
            if not raw_text or len(raw_text.strip()) < 100:
                st.error("❌ Le document semble vide ou trop court pour l'extraction.")
                return None
            
            # Afficher un aperçu du texte extrait
            with st.expander("👁️ Aperçu du texte extrait"):
                preview = raw_text[:2000] + ("..." if len(raw_text) > 2000 else "")
                st.text(preview)
            
            # 2. Préparer le prompt
            extraction_prompt = prepare_extraction_prompt(raw_text, max_chars=15000)
            system_prompt = get_extraction_system_prompt()
            
            # Info si document tronqué
            if len(raw_text) > 15000:
                st.warning("⚠️ Document volumineux, texte tronqué pour l'analyse.")
            
            # 3. Appeler le LLM
            from engine.llm_service import ProviderType
            
            response = llm_manager.generate_response(
                prompt=extraction_prompt,
                system_prompt=system_prompt,
                primary_provider=ProviderType(llm_provider),
                max_tokens=2000,
                temperature=0.1  # Basse température pour extraction précise
            )
            
            # 4. Parser la réponse
            extracted = parse_llm_extraction_response(response)
            extracted.raw_text = raw_text
            extracted.source_filename = uploaded_file.name
            
            # 5. Afficher les résultats
            _display_extraction_results(extracted)
            
            return extracted
            
        except Exception as e:
            logger.error(f"Extraction failed: {e}")
            st.error(f"❌ Erreur lors de l'extraction : {str(e)}")
            return None


def _display_extraction_results(extracted: ExtractedData):
    """
    Affiche les résultats de l'extraction de manière formatée.
    """
    # Badge de confiance
    if extracted.confidence >= 70:
        st.success(f"✅ Extraction réussie (confiance: {extracted.confidence:.0f}%)")
    elif extracted.confidence >= 40:
        st.warning(f"⚠️ Extraction partielle (confiance: {extracted.confidence:.0f}%)")
    else:
        st.error(f"❌ Extraction limitée (confiance: {extracted.confidence:.0f}%)")
    
    # Données extraites
    with st.expander("📋 Données extraites", expanded=True):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Informations générales**")
            _display_field("Entreprise", extracted.company_name)
            _display_field("Pays", extracted.country)
            _display_field("Secteur", extracted.sector)
            _display_field("Sous-secteur", extracted.subsector)
            _display_field("Employés", extracted.employees)
            _display_field("CA", extracted.revenue)
            _display_field("Année création", extracted.year_founded)
            _display_field("Marché cible", extracted.target_market)
        
        with col2:
            st.markdown("**Données 2X Challenge**")
            _display_field("% Détention femmes", extracted.women_ownership_pct, suffix="%")
            _display_field("% Management femmes", extracted.women_management_pct, suffix="%")
            _display_field("% Employées femmes", extracted.women_employees_pct, suffix="%")
            _display_field("Bénéficie aux femmes", "Oui" if extracted.benefits_women else ("Non" if extracted.benefits_women is False else None))
            
            st.markdown("**Activité**")
            if extracted.business_description:
                st.markdown(f"_{extracted.business_description[:200]}{'...' if len(extracted.business_description or '') > 200 else ''}_")
        
        # Notes d'extraction
        if extracted.extraction_notes:
            st.markdown("**⚠️ Notes d'extraction :**")
            for note in extracted.extraction_notes:
                st.markdown(f"- {note}")


def _display_field(label: str, value, suffix: str = ""):
    """Affiche un champ extrait."""
    if value is not None:
        st.markdown(f"- **{label}:** {value}{suffix}")
    else:
        st.markdown(f"- **{label}:** _non trouvé_")


def apply_extracted_data_to_form(extracted: ExtractedData) -> Dict:
    """
    Convertit les données extraites en valeurs pour pré-remplir le formulaire.
    
    Args:
        extracted: Données extraites du document
    
    Returns:
        Dict avec les valeurs à utiliser comme defaults dans le formulaire
    """
    defaults = {}
    
    if extracted.company_name:
        defaults['company_name'] = extracted.company_name
    
    if extracted.country:
        defaults['country'] = extracted.country
    
    if extracted.sector:
        defaults['sector'] = extracted.sector
    
    if extracted.subsector:
        defaults['subsector'] = extracted.subsector
    
    if extracted.business_description:
        defaults['business_model'] = extracted.business_description
    
    if extracted.employees:
        defaults['employees'] = int(extracted.employees)
    
    if extracted.revenue:
        defaults['revenue'] = extracted.revenue
    
    if extracted.year_founded:
        defaults['years_operation'] = 2025 - int(extracted.year_founded)
    
    if extracted.target_market:
        defaults['target_market'] = extracted.target_market
    
    if extracted.geographic_scope:
        defaults['geographic_scope'] = extracted.geographic_scope
    
    # Données 2X
    if extracted.women_ownership_pct is not None:
        defaults['women_ownership_pct'] = int(extracted.women_ownership_pct)
    
    if extracted.women_management_pct is not None:
        defaults['women_management_pct'] = int(extracted.women_management_pct)
    
    if extracted.women_employees_pct is not None:
        defaults['women_employees_pct'] = int(extracted.women_employees_pct)
    
    if extracted.benefits_women is not None:
        defaults['benefits_women'] = extracted.benefits_women
    
    return defaults


def get_extraction_status_badge(extracted: Optional[ExtractedData]) -> str:
    """
    Retourne un badge HTML pour le statut d'extraction.
    """
    if not extracted:
        return ""
    
    filled = extracted.get_filled_fields_count()
    total = 18  # Nombre approximatif de champs
    
    if extracted.confidence >= 70:
        color = "#28a745"
        status = "Extraction réussie"
    elif extracted.confidence >= 40:
        color = "#ffc107"
        status = "Extraction partielle"
    else:
        color = "#dc3545"
        status = "Extraction limitée"
    
    return f"""
    <div style="background-color: {color}20; border-left: 4px solid {color}; 
                padding: 8px 12px; border-radius: 4px; margin: 10px 0;">
        <strong>{status}</strong> — {filled} champs remplis | Confiance: {extracted.confidence:.0f}%
    </div>
    """
