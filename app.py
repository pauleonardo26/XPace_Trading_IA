import streamlit as st
import tarj_academia
import tarj_mercado
import tarj_simulador
import tarj_analisis

st.set_page_config(page_title="XPace — Escuela de Trading", layout="wide", page_icon="🎓")

st.markdown("""
    <style>
    .stApp { background-color: #0b0e14 !important; color: #e6edf3 !important; }
    .block-container { padding-top: 1rem !important; max-width: 100% !important; }
    </style>
""", unsafe_allow_html=True)

st.title("🎓 XPace — Escuela de Trading")

tab1, tab2, tab3, tab4 = st.tabs([
    "📚 Academia & Curso", 
    "📈 Mercado & Histórico", 
    "🧪 Simulador Interactivo", 
    "🤖 Co-Piloto IA"
])

with tab1:
    tarj_academia.render()

with tab2:
    tarj_mercado.render()

with tab3:
    tarj_simulador.render()

with tab4:
    tarj_analisis.render()


