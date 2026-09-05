import streamlit as st

# ============================================================
# XPACE TRADING IA - APLICACIÓN PRINCIPAL
# ============================================================

st.set_page_config(
    page_title="XPace Trading IA",
        page_icon="📈",
            layout="wide"
            )
st.title("📈 XPace Trading IA")

st.write("Plataforma de aprendizaje y análisis de Forex")

st.divider()

st.subheader("Mercado")
par = st.selectbox(
                "Selecciona el par",
                    [
                            "EUR/USD",
                                    "GBP/USD",
                                            "USD/JPY"
                                                ]
                                                )
st.write("Par seleccionado:", par)
if st.button("📥 Traer histórico"):
    st.info("Módulo histórico pendiente de conectar.")