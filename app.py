# ============================================================
# XPACE TRADING IA - APLICACIÓN PRINCIPAL
# ============================================================

import streamlit as st
import pandas as pd


from historico import obtener_historico
from indicadores import calcular_indicadores
from estrategias import evaluar_estrategia_cruces
from backtesting import ejecutar_backtesting
from riesgo import calcular_riesgo_operacion
from ia_analista import generar_informe_analista

st.set_page_config(page_title="XPace Trading IA", layout="centered")

st.title("📈 XPace Trading IA")
st.caption("Plataforma cuantitativa y analítica de trading")

st.divider()

# --- SECCIÓN 1: ESTADO DE CONEXIÓN ---
st.subheader("1. Conexión Broker (OANDA Demo)")
if st.button("🔌 Probar Conexión OANDA"):
    exito, mensaje = probar_conexion_oanda()
    if exito:
        st.success(mensaje)
    else:
        st.warning(mensaje)

st.divider()

# --- SECCIÓN 2: PARÁMETROS DEL MERCADO ---
st.subheader("2. Configuración de Mercado")
col1, col2 = st.columns(2)

with col1:
    par = st.selectbox("Par de Divisas:", ["EUR/USD", "GBP/USD", "USD/JPY"])
    estilo = st.selectbox("Estilo de Trading:", ["Swing Trading", "Day Trading"])

with col2:
    temporalidad = st.selectbox("Temporalidad:", ["15 Minutos (M15)", "1 Hora (H1)", "4 Horas (H4)", "1 Día (D1)"])
    cantidad_velas = st.slider("Cantidad de Velas:", min_value=50, max_value=300, value=100, step=10)

st.info(f"Configuración: **{par}** | **{temporalidad}** | Modo: **{estilo}**")

# --- BOTÓN PRINCIPAL DE ANÁLISIS ---
if st.button("📥 CARGAR DATOS Y EJECUTAR ANÁLISIS", type="primary"):
    with st.spinner("Descargando datos y procesando indicadores..."):
        df, msg = obtener_historico(par=par, temporalidad=temporalidad, cantidad=cantidad_velas)
        
        if df is not None and not df.empty:
            df = calcular_indicadores(df)
            df = evaluar_estrategia_cruces(df)
            st.session_state["df_actual"] = df
            st.success(f"¡Datos procesados correctamente! ({msg})")
        else:
            st.error(f"No se pudieron obtener datos: {msg}")

# --- SECCIÓN 3: PESTAÑAS DE TRABAJO ---
if "df_actual" in st.session_state and st.session_state["df_actual"] is not None:
    df = st.session_state["df_actual"]
    
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Datos & Señales", "🧪 Backtesting", "🛡️ Riesgo", "🤖 Analista IA"])
    
    # PESTAÑA 1: DATOS E INDICADORES
    with tab1:
        st.markdown("### Tabla de Precios e Indicadores")
        st.dataframe(df.tail(20), use_container_width=True)
        
        ultima_vela = df.iloc[-1]
        st.markdown("#### Última Vela Cerrada:")
        c1, c2, c3 = st.columns(3)
        c1.metric("Cierre", f"{ultima_vela['Close']:.5f}")
        c2.metric("SMA 20", f"{ultima_vela['SMA_20']:.5f}" if pd.notnull(ultima_vela['SMA_20']) else "N/A")
        c3.metric("RSI (14)", f"{ultima_vela['RSI_14']:.2f}" if pd.notnull(ultima_vela['RSI_14']) else "N/A")
        
    # PESTAÑA 2: BACKTESTING
    with tab2:
        st.markdown("### Resultados de Backtesting")
        capital_inicial = st.number_input("Capital Inicial ($USD):", value=10000.0, step=1000.0)
        
        df_bt, resumen_bt = ejecutar_backtesting(df, capital_inicial=capital_inicial)
        if resumen_bt and isinstance(resumen_bt, dict):
            for k, v in resumen_bt.items():
                st.write(f"**{k}:** {v}")
            st.line_chart(df_bt["Evolucion_Capital"])
            
    # PESTAÑA 3: GESTIÓN DE RIESGO
    with tab3:
        st.markdown("### Calculadora de Posición y Riesgo")
        precio_ref = float(df.iloc[-1]["Close"])
        
        col_r1, col_r2 = st.columns(2)
        with col_r1:
            capital_riesgo = st.number_input("Capital Total ($USD):", value=10000.0, key="cap_r")
            pct_riesgo = st.slider("Riesgo por Operación (%):", 0.5, 5.0, 1.0, 0.5)
            dist_sl = st.number_input("Distancia SL (Pips):", value=30.0, step=5.0)
        with col_r2:
            rel_rr = st.number_input("Relación R:R (1:X):", value=2.0, step=0.5)
            tipo_orden = st.radio("Dirección:", ["Compra", "Venta"])
            
        res_riesgo, msg_r = calcular_riesgo_operacion(
            capital_total=capital_riesgo,
            porcentaje_riesgo=pct_riesgo,
            precio_entrada=precio_ref,
            distancia_stop_loss_pips=dist_sl,
            direccion=tipo_orden.lower(),
            relacion_rr=rel_rr,
            par=par
        )
        
        if res_riesgo:
            st.session_state["resumen_riesgo"] = res_riesgo
            for k, v in res_riesgo.items():
                st.write(f"**{k}:** {v}")

    # PESTAÑA 4: IA ANALISTA
    with tab4:
        st.markdown("### Informe del Analista IA")
        u_vela = df.iloc[-1]
        res_r = st.session_state.get("resumen_riesgo", None)
        
        informe = generar_informe_analista(
            par=par,
            temporalidad=temporalidad,
            precio_actual=float(u_vela["Close"]),
            rsi=float(u_vela["RSI_14"]) if pd.notnull(u_vela["RSI_14"]) else 50.0,
            sma_20=float(u_vela["SMA_20"]) if pd.notnull(u_vela["SMA_20"]) else float(u_vela["Close"]),
            sma_50=float(u_vela["SMA_50"]) if pd.notnull(u_vela["SMA_50"]) else float(u_vela["Close"]),
            senal=int(u_vela["Senal"]),
            resumen_riesgo=res_r
        )
        st.markdown(informe)







