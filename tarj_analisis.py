import streamlit as st
import ia_analista

def render():
    st.write("### 🤖 Co-Piloto & Evaluador IA")
    st.caption("Obtén un informe avanzado del estado actual del mercado generado por el motor de IA.")

    col1, col2 = st.columns(2)
    with col1:
        par = st.selectbox("Par de Forex", ["EUR/USD", "USD/JPY", "GBP/USD"], key="ia_par")
        tf = st.selectbox("Temporalidad", ["15m", "1h"], key="ia_tf")
    with col2:
        precio = st.number_input("Precio Actual", value=1.0850, format="%.4f")
        rsi = st.slider("RSI Actual", 0.0, 100.0, 55.0)

    if st.button("🧠 Generar Informe de IA", type="primary", use_container_width=True):
        informe = ia_analista.generar_informe_analista(
            par=par,
            temporalidad=tf,
            precio_actual=precio,
            rsi=rsi,
            sma_20=precio * 1.001,
            sma_50=precio * 0.999,
            senal=1 if rsi > 50 else -1
        )
        st.markdown(informe)

