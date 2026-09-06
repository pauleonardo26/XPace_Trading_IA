# ============================================================
# XPACE TRADING IA - APLICACIÓN PRINCIPAL
# ============================================================


import streamlit as st
import pandas as pd
from historico import obtener_historico
from indicadores import calcular_indicadores
from estrategias import generar_senales
from backtesting import ejecutar_backtesting
from riesgo import calcular_gestion_riesgo
from ia_analista import generar_informe_analista


st.set_page_config(page_title="XPace Trading IA", layout="wide", page_icon="📈")

st.title("📈 XPace Trading IA — Plataforma Cuantitativa")
st.caption("Sistema modular de análisis técnico, backtesting y gestión de riesgo con datos de Yahoo Finance.")

# Barra lateral para parámetros globales
st.sidebar.header("⚙️ Configuración del Mercado")
par_seleccionado = st.sidebar.selectbox("Par de Divisas", ["EUR/USD", "GBP/USD", "USD/JPY"])
temporalidad_seleccionada = st.sidebar.selectbox("Temporalidad", ["15 Minutos (M15)", "1 Hora (H1)", "4 Horas (H4)", "1 Día (D1)"])
cantidad_velas = st.sidebar.slider("Cantidad de Velas", min_value=50, max_value=1000, value=100, step=50)

# Carga de datos
df_datos, mensaje_estado = obtener_historico(par=par_seleccionado, temporalidad=temporalidad_seleccionada, cantidad=cantidad_velas)

if df_datos is not None and not df_datos.empty:
    df_datos = calcular_indicadores(df_datos)
    df_datos = generar_senales(df_datos)
    
    # Crear pestañas de navegación
    tab1, tab2, tab3, tab4 = st.tabs(["📈 Panel Principal", "🧪 Backtesting", "🛡️ Calculadora de Riesgo", "🤖 Analista IA"])
    
    # PESTAÑA 1: PANEL PRINCIPAL
    with tab1:
        st.subheader(f"Datos Históricos de {par_seleccionado} ({temporalidad_seleccionada})")
        st.dataframe(df_datos.tail(15), use_container_width=True)
        
        precio_actual = df_datos["Close"].iloc[-1]
        rsi_actual = df_datos["RSI"].iloc[-1]
        sma20_actual = df_datos["SMA_20"].iloc[-1]
        sma50_actual = df_datos["SMA_50"].iloc[-1]
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Precio Cierre", f"{precio_actual:.5f}")
        col2.metric("RSI (14)", f"{rsi_actual:.1f}")
        col3.metric("SMA 20", f"{sma20_actual:.5f}")
        col4.metric("SMA 50", f"{sma50_actual:.5f}")

    # PESTAÑA 2: BACKTESTING
    with tab2:
        st.subheader("🧪 Simulador de Rendimiento de Estrategia")
        capital_inicial = st.number_input("Capital Inicial ($ USD)", value=10000.0, step=500.0)
        
        if st.button("Ejecutar Backtesting", type="primary"):
            df_backtest, rendimiento, ganadoras, perdedoras, win_rate, total_ops, capital_final = ejecutar_backtest(df_datos, capital_inicial=capital_inicial)
            
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Capital Final", f"${capital_final:,.2f}")
            c2.metric("Rendimiento Total", f"{rendimiento:.2f}%")
            c3.metric("Win Rate", f"{win_rate:.2f}%")
            c4.metric("Cambios de Señal", total_ops)
            
            # Texto preparado para copiar con un solo toque
            resumen_copia = f"""📊 RESUMEN DE BACKTESTING — XPace Trading IA
-------------------------------------------
Activo: {par_seleccionado} | Temporalidad: {temporalidad_seleccionada}
Velas analizadas: {cantidad_velas}

• Capital Inicial: ${capital_inicial:,.2f} USD
• Capital Final: ${capital_final:,.2f} USD
• Rendimiento Total: {rendimiento:.2f}%
• Señales Totales: {total_ops}

📈 ESTADÍSTICAS:
• Operaciones Ganadoras: {ganadoras}
• Operaciones Perdedoras: {perdedoras}
• Tasa de Acierto (Win Rate): {win_rate:.2f}%"""
            
            st.write("---")
            st.subheader("📋 Copiar Resumen de Resultados")
            st.code(resumen_copia, language="text")

    # PESTAÑA 3: CALCULADORA DE RIESGO
    with tab3:
        st.subheader("🛡️ Gestión Monetaria y Tamaño de Lote (Ratio 1:2)")
        col_r1, col_r2 = st.columns(2)
        with col_r1:
            cap_riesgo = st.number_input("Capital de Cuenta ($)", value=10000.0)
            pct_riesgo = st.slider("Riesgo por Operación (%)", 0.5, 5.0, 1.0, 0.5)
        with col_r2:
            precio_ref = df_datos["Close"].iloc[-1]
            pips_stop = st.number_input("Pips de Stop Loss", value=20, step=5)
            
        resumen_r = calcular_gestion_riesgo(capital=cap_riesgo, porcentaje_riesgo=pct_riesgo, precio_entrada=precio_ref, ratio_rr=2.0, pips_sl=pips_stop)
        
        st.json(resumen_r)

    # PESTAÑA 4: ANALISTA IA
    with tab4:
        st.subheader("🤖 Diagnóstico Cuantitativo del Analista IA")
        if st.button("Generar Informe Completo", type="primary"):
            p_actual = df_datos["Close"].iloc[-1]
            r_actual = df_datos["RSI"].iloc[-1]
            s20_actual = df_datos["SMA_20"].iloc[-1]
            s50_actual = df_datos["SMA_50"].iloc[-1]
            sen_actual = df_datos["Senal"].iloc[-1]
            
            res_riesgo = calcular_gestion_riesgo(capital=10000.0, porcentaje_riesgo=1.0, precio_entrada=p_actual, ratio_rr=2.0, pips_sl=20)
            
            informe_ia = generar_informe_analista(
                par=par_seleccionado,
                temporalidad=temporalidad_seleccionada,
                precio_actual=p_actual,
                rsi=r_actual,
                sma_20=s20_actual,
                sma_50=s50_actual,
                senal=sen_actual,
                resumen_riesgo=res_riesgo
            )
            
            st.markdown(informe_ia)
            st.write("---")
            st.subheader("📋 Copiar Informe de IA")
            st.code(informe_ia, language="text")

else:
    st.error(f"Error al cargar los datos: {mensaje_estado}")



