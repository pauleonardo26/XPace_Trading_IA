import streamlit as st
from conexion_oanda import conectar_oanda

# Configuración básica de la pantalla para celulares
st.set_page_config(page_title="XPace Trading IA", layout="centered")

# Título principal
st.title("📈 XPace Trading IA")
st.caption("Plataforma de aprendizaje y análisis de trading")

st.divider()

# Sección de Configuración y Conexión
st.subheader("1. Conexión con Broker (OANDA Demo)")

if st.button("Probar Conexión OANDA"):
    exito, mensaje = conectar_oanda()
    if exito:
        st.success(mensaje)
    else:
        st.warning(mensaje)

st.divider()

# Sección de Selección de Mercado
st.subheader("2. Selección de Mercado")
par = st.selectbox("Selecciona un Par de Divisas:", ["EUR/USD", "GBP/USD", "USD/JPY"])
temporalidad = st.selectbox("Selecciona la Temporalidad:", ["1 Hora (H1)", "4 Horas (H4)", "1 Día (D1)"])

st.info(f"Par seleccionado: {par} | Temporalidad: {temporalidad}")
