"""Composants UI partages ECOSYS."""

import streamlit as st


def carte_kpi(libelle, valeur, suffixe="", sous_texte=None):
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-label">{libelle}</div>
            <div class="kpi-value">{valeur}<span class="kpi-suffix"> {suffixe}</span></div>
            {f'<div style="font-size:0.85rem;color:#78909C;margin-top:0.2rem;">{sous_texte}</div>' if sous_texte else ''}
        </div>
        """,
        unsafe_allow_html=True,
    )
