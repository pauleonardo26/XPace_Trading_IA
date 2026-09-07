



import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from historico import obtener_historico
from indicadores import calcular_indicadores
from estrategias import generar_senales
from backtesting import ejecutar_backtesting
from riesgo import calcular_riesgo_operacion
from ia_analista import generar_informe_analista

# Configuración de página e inyección de tema oscuro estilo Terminal
st.set_page_config(page_title="XPace Trading IA", layout="wide", page_icon="📈")

st.markdown("""
    <style>
    .stApp {
        background-color: #0b0e14;
        color: #e1e3e6;
    }
    div[data-testid="stMetricValue"] {
        font-size: 20px;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

st.title("📈 XPace Trading IA — Terminal Cuantitativa")

# ------------------ BARRA LATERAL: CONFIGURACIÓN ------------------
st.sidebar.header("⚙️ Configuración del Mercado")
par_seleccionado = st.sidebar.selectbox("Par de Divisas", ["EUR/USD", "GBP/USD", "USD/JPY"])
temporalidad_seleccionada = st.sidebar.selectbox("Temporalidad", ["15 Minutos (M15)", "1 Hora (H1)", "4 Horas (H4)", "1 Día (D1)"])
cantidad_velas = st.sidebar.slider("Cantidad de Velas", min_value=50, max_value=1000, value=100, step=50)

# Carga e inicialización de datos
df_datos, mensaje_estado = obtener_historico(par=par_seleccionado, temporalidad=temporalidad_seleccionada, cantidad=cantidad_velas)

if df_datos is not None and not df_datos.empty and "Close" in df_datos.columns:
    df_datos = calcular_indicadores(df_datos)
    df_datos = generar_senales(df_datos)
    
    tab1, tab2, tab3, tab4 = st.tabs(["📈 Panel Interactivo", "🧪 Backtesting", "🛡️ Calculadora de Riesgo", "🤖 Analista IA"])
    
    # ------------------ PESTAÑA 1: TERMINAL VISUAL DE TRADING ------------------
    with tab1:
        st.subheader(f"Gráfico Interactivo en Tiempo Real — {par_seleccionado}")
        
        # Identificación defensiva de la columna RSI
        col_rsi_name = "RSI_14" if "RSI_14" in df_datos.columns else ("RSI" if "RSI" in df_datos.columns else None)
        
        p_act = float(df_datos["Close"].iloc[-1])
        r_act = float(df_datos[col_rsi_name].iloc[-1]) if col_rsi_name else 50.0
        s20_act = float(df_datos["SMA_20"].iloc[-1]) if "SMA_20" in df_datos.columns else p_act
        s50_act = float(df_datos["SMA_50"].iloc[-1]) if "SMA_50" in df_datos.columns else p_act
        
        col_m1, col_m2, col_m3, col_m4 = st.columns(4)
        col_m1.metric("Último Precio", f"{p_act:.5f}")
        col_m2.metric("RSI (14)", f"{r_act:.1f}")
        col_m3.metric("SMA 20", f"{s20_act:.5f}")
        col_m4.metric("SMA 50", f"{s50_act:.5f}")

        # Construcción del panel de Velas + RSI
        fig = make_subplots(
            rows=2, cols=1, 
            shared_xaxes=True, 
            vertical_spacing=0.03, 
            subplot_titles=(f"{par_seleccionado} ({temporalidad_seleccionada})", "Oscilador RSI (14)"),
            row_width=[0.25, 0.75]
        )

        # 1. Velas Japonesas
        fig.add_trace(go.Candlestick(
            x=df_datos.index,
            open=df_datos['Open'] if 'Open' in df_datos.columns else df_datos['Close'],
            high=df_datos['High'] if 'High' in df_datos.columns else df_datos['Close'],
            low=df_datos['Low'] if 'Low' in df_datos.columns else df_datos['Close'],
            close=df_datos['Close'],
            name='Precio',
            increasing_line_color='#00c076',
            decreasing_line_color='#ff3b30'
        ), row=1, col=1)

        # 2. Medias Móviles
        if "SMA_20" in df_datos.columns:
            fig.add_trace(go.Scatter(x=df_datos.index, y=df_datos['SMA_20'], line=dict(color='#29b6f6', width=1.5), name='SMA 20'), row=1, col=1)
        if "SMA_50" in df_datos.columns:
            fig.add_trace(go.Scatter(x=df_datos.index, y=df_datos['SMA_50'], line=dict(color='#ff9800', width=1.5), name='SMA 50'), row=1, col=1)

        # 3. Oscilador RSI
        if col_rsi_name:
            fig.add_trace(go.Scatter(x=df_datos.index, y=df_datos[col_rsi_name], line=dict(color='#ab47bc', width=1.5), name='RSI'), row=2, col=1)
            fig.add_hline(y=70, line_dash="dash", line_color="#ff3b30", row=2, col=1)
            fig.add_hline(y=30, line_dash="dash", line_color="#00c076", row=2, col=1)

        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="#0b0e14",
            plot_bgcolor="#131722",
            height=580,
            xaxis_rangeslider_visible=False,
            margin=dict(l=10, r=10, t=30, b=10)
        )

        st.plotly_chart(fig, use_container_width=True)

        st.write("---")
        st.subheader("📋 Últimas Velas del Histórico")
        st.dataframe(df_datos.tail(10), use_container_width=True)

    # ------------------ PESTAÑA 2: BACKTESTING ------------------
    with tab2:
        st.subheader("🧪 Simulador de Rendimiento de Estrategia")
        cap_init = st.number_input("Capital Inicial ($ USD)", value=10000.0, step=500.0)
        
        if st.button("Ejecutar Backtesting", type="primary"):
            df_bt, resumen = ejecutar_backtesting(df_datos, capital_inicial=cap_init)
            
            mc1, mc2, mc3, mc4 = st.columns(4)
            mc1.metric("Capital Final", resumen["Capital Final"])
            mc2.metric("Rendimiento Total", resumen["Rendimiento Total"])
            mc3.metric("Win Rate", resumen["Win Rate"])
            mc4.metric("Total Operaciones", resumen["Total Operaciones"])
            
            st.write("---")
            if "Evolucion_Capital" in df_bt.columns:
                st.subheader("📈 Curva de Rendimiento del Capital")
                st.line_chart(df_bt["Evolucion_Capital"])

            st.subheader("📊 Historial Detallado de Operaciones")
            if isinstance(resumen["Detalle Trades"], pd.DataFrame) and not resumen["Detalle Trades"].empty:
                st.dataframe(resumen["Detalle Trades"], use_container_width=True)
            else:
                st.info("No se registraron cambios de señal completos en este rango de velas.")

    # ------------------ PESTAÑA 3: CALCULADORA DE RIESGO ------------------
    with tab3:
        st.subheader("🛡️ Gestión Monetaria y Calculadora de Riesgo")
        col_r1, col_r2 = st.columns(2)
        with col_r1:
            c_riesgo = st.number_input("Capital de Cuenta ($)", value=10000.0)
            p_riesgo = st.slider("Riesgo por Operación (%)", 0.5, 5.0, 1.0, 0.5)
            precio_ref = float(df_datos["Close"].iloc[-1])
            st.info(f"Precio Actual de Referencia: **{precio_ref:.5f}**")
            
        with col_r2:
            pips_stop = st.number_input("Pips de Stop Loss", value=20, step=5)
            usar_tp_custom = st.checkbox("Ingresar Take Profit manualmente")
            
            tp_manual_val = None
            if usar_tp_custom:
                tp_manual_val = st.number_input("Precio Take Profit Deseado", value=precio_ref + 0.0040, format="%.5f")
            
        res_r, _ = calcular_riesgo_operacion(
            capital_total=c_riesgo, 
            porcentaje_riesgo=p_riesgo, 
            precio_entrada=precio_ref, 
            distancia_stop_loss_pips=pips_stop,
            relacion_rr=2.0,
            par=par_seleccionado,
            take_profit_manual=tp_manual_val
        )
        st.json(res_r)

    # ------------------ PESTAÑA 4: DIAGNÓSTICO DE IA ------------------
    with tab4:
        st.subheader("🤖 Diagnóstico Cuantitativo del Analista IA")
        if st.button("Generar Informe Completo", type="primary"):
            p_act = float(df_datos["Close"].iloc[-1])
            
            col_rsi_name = "RSI_14" if "RSI_14" in df_datos.columns else ("RSI" if "RSI" in df_datos.columns else None)
            r_act = float(df_datos[col_rsi_name].iloc[-1]) if col_rsi_name else 50.0
            
            s20_act = float(df_datos["SMA_20"].iloc[-1]) if "SMA_20" in df_datos.columns else p_act
            s50_act = float(df_datos["SMA_50"].iloc[-1]) if "SMA_50" in df_datos.columns else p_act
            sen_act = int(df_datos["Senal"].iloc[-1]) if "Senal" in df_datos.columns else 0
            
            res_r, _ = calcular_riesgo_operacion(
                capital_total=10000.0, 
                porcentaje_riesgo=1.0, 
                precio_entrada=p_act, 
                distancia_stop_loss_pips=20,
                relacion_rr=2.0,
                par=par_seleccionado
            )
            
            inf_ia = generar_informe_analista(par_seleccionado, temporalidad_seleccionada, p_act, r_act, s20_act, s50_act, sen_act, res_r)
            st.markdown(inf_ia)

else:
    st.error(f"Error al cargar los datos: {mensaje_estado}")
