import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

from historico import obtener_historico
from indicadores import calcular_indicadores
from estrategias import generar_senales
from backtesting import ejecutar_backtesting
from riesgo import calcular_riesgo_operacion
from ia_analista import generar_informe_analista

# ------------------ CONFIGURACIÓN DE PÁGINA BROKER PROFESIONAL ------------------
st.set_page_config(page_title="XPace Terminal", layout="wide", page_icon="📈")

# Inicialización de estado de cuenta demo
if "saldo_demo" not in st.session_state:
    st.session_state["saldo_demo"] = 13449.67

if "historial_trades" not in st.session_state:
    st.session_state["historial_trades"] = []

# --- CSS AVANZADO: ELIMINACIÓN DE ESPACIOS Y LAYOUT PROFESIONAL (FOCALIZADO EN MÓVIL) ---
st.markdown("""
    <style>
    /* 1. Reset General de Espacios en Streamlit */
    .stApp {
        background-color: #0d1117;
        color: #e6edf3;
        margin: 0 !important;
        padding: 0 !important;
    }
    
    /* Eliminar paddings superiores e inferiores molestos en móvil */
    .block-container {
        padding-top: 0rem !important;
        padding-bottom: 0rem !important;
        padding-left: 0.5rem !important;
        padding-right: 0.5rem !important;
    }
    
    /* Ocultar elementos innecesarios */
    [data-testid="stHeader"] {background: rgba(0,0,0,0); padding-top: 2rem;}
    [data-testid="stSidebar"] {background-color: #161b22;}

    /* 2. Diseño del Header Compacto */
    .header-compact {
        display: flex;
        justify-content: space-between;
        align-items: center;
        background-color: #161b22;
        padding: 5px 15px;
        border-radius: 4px;
        margin-top: 10px;
        margin-bottom: 5px;
        border: 1px solid #21262d;
    }
    .balance-title {
        color: #8b949e;
        font-size: 10px;
        font-weight: bold;
        text-transform: uppercase;
    }
    .balance-value {
        color: #f2a900;
        font-size: 18px;
        font-weight: 800;
    }
    
    /* 3. Reingeniería del Layout OPERAR: Gráfico + Panel Lado a Lado */
    /* Este contenedor força el diseño en móvil */
    .broker-layout-container {
        display: flex;
        flex-direction: row !important; /* Fuerza Lado a Lado en Móvil */
        width: 100%;
        height: calc(100vh - 120px); /* Ocupa el alto restante */
        margin: 0;
        padding: 0;
    }
    
    .chart-section {
        flex: 2.5; /* 70% del ancho */
        height: 100%;
        padding-right: 5px;
    }
    
    .panel-section {
        flex: 1; /* 30% del ancho */
        height: 100%;
        background-color: #161b22;
        padding: 10px;
        border-left: 1px solid #21262d;
        border-radius: 4px;
        display: flex;
        flex-direction: column;
        justify-content: flex-start;
    }

    /* 4. Estilos de los Botones de Operación */
    div.stButton > button[key="btn_buy"] {
        background-color: #00e676 !important;
        color: #000000 !important;
        font-size: 16px !important;
        font-weight: 900 !important;
        height: 50px !important;
        border-radius: 6px !important;
        border: none !important;
    }
    div.stButton > button[key="btn_sell"] {
        background-color: #ff1744 !important;
        color: #ffffff !important;
        font-size: 16px !important;
        font-weight: 900 !important;
        height: 50px !important;
        border-radius: 6px !important;
        border: none !important;
    }
    
    /* Estilos paraInputs compactos */
    .stNumberInput, .stSelectbox {
        margin-bottom: 5px !important;
    }
    .stNumberInput > div > div > input {
        background-color: #0d1117 !important;
        color: #e6edf3 !important;
        border: 1px solid #30363d !important;
    }
    </style>
""", unsafe_allow_html=True)

# ------------------ TOP BAR / HEADER BROKER COMPACTO ------------------
with st.container():
    st.markdown(f"""
        <div class="header-compact">
            <div style="font-size: 14px; font-weight: bold;">XPace Terminal</div>
            <div style="text-align: right;">
                <span class="balance-title">CUENTA DEMO</span><br>
                <span class="balance-value">${st.session_state['saldo_demo']:,.2f}</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

# ------------------ BARRA LATERAL (SELECTOR ACTIVO) ------------------
# Mantenemos la sidebar para no amontonar el header
par_seleccionado = st.sidebar.selectbox("🪙 Activo", ["EUR/USD", "GBP/USD", "USD/JPY"], index=0)
temporalidad_seleccionada = st.sidebar.selectbox("Temporalidad", ["15 Minutos (M15)", "1 Hora (H1)", "4 Horas (H4)", "1 Día (D1)"], index=1)
cantidad_velas = st.sidebar.slider("Velas", 50, 500, 150)

# Carga de datos
df_datos, mensaje_estado = obtener_historico(par=par_seleccionado, temporalidad=temporalidad_seleccionada, cantidad=cantidad_velas)

if df_datos is not None and not df_datos.empty and "Close" in df_datos.columns:
    df_datos = calcular_indicadores(df_datos)
    df_datos = generar_senales(df_datos)

    p_act = float(df_datos["Close"].iloc[-1])
    col_rsi_name = "RSI_14" if "RSI_14" in df_datos.columns else ("RSI" if "RSI" in df_datos.columns else None)
    r_act = float(df_datos[col_rsi_name].iloc[-1]) if col_rsi_name else 50.0

    # NAVEGACIÓN COMPACTA
    tabs = st.tabs(["📊 OPERAR", "📋 HISTORIAL", "🧪 TESTS", "🤖 IA"])

    # ------------------ PESTAÑA 1: TERMINAL OPERATIVA (REINGENIERÍA LAYOUT) ------------------
    with tabs[0]:
        # Creamos el contenedor principal con la clase CSS para forzar el diseño lado a lado
        with st.container():
            st.markdown('<div class="broker-layout-container">', unsafe_allow_html=True)
            
            # --- SECCIÓN DEL GRÁFICO (CENTRO) ---
            st.markdown('<div class="chart-section">', unsafe_allow_html=True)
            
            # Subtitle compacto
            st.markdown(f"<div style='font-size:12px; color:#8b949e; padding-bottom:2px;'>{par_seleccionado} ({temporalidad_seleccionada})</div>", unsafe_allow_html=True)
            
            fig = go.Figure()

            # Velas Japonesas Profesionales
            fig.add_trace(go.Candlestick(
                x=df_datos.index,
                open=df_datos['Open'] if 'Open' in df_datos.columns else df_datos['Close'],
                high=df_datos['High'] if 'High' in df_datos.columns else df_datos['Close'],
                low=df_datos['Low'] if 'Low' in df_datos.columns else df_datos['Close'],
                close=df_datos['Close'],
                increasing_line_color='#00e676', decreasing_line_color='#ff1744',
                increasing_fillcolor='#00e676', decreasing_fillcolor='#ff1744'
            ))

            if "SMA_20" in df_datos.columns:
                fig.add_trace(go.Scatter(x=df_datos.index, y=df_datos['SMA_20'], line=dict(color='#29b6f6', width=1)))
            if "SMA_50" in df_datos.columns:
                fig.add_trace(go.Scatter(x=df_datos.index, y=df_datos['SMA_50'], line=dict(color='#ff9800', width=1)))

            fig.update_layout(
                template="plotly_dark",
                paper_bgcolor="#0d1117", plot_bgcolor="#161b22",
                height=580, # Aumentado para móvil
                xaxis_rangeslider_visible=False,
                margin=dict(l=5, r=5, t=5, b=5),
                yaxis=dict(side="right", gridcolor="#21262d", font=dict(size=10)),
                xaxis=dict(gridcolor="#21262d", font=dict(size=10))
            )
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
            
            st.markdown('</div>', unsafe_allow_html=True) # Cierre chart-section
            
            
            # --- SECCIÓN DEL PANEL OPERATIVO (DERECHA) ---
            st.markdown('<div class="panel-section">', unsafe_allow_html=True)
            
            st.markdown(f"<div style='text-align:center; color:#f2a900; font-size:16px; font-weight:800;'>{p_act:.5f}</div>", unsafe_allow_html=True)
            
            inversion = st.number_input("INVERSIÓN ($)", min_value=1.0, value=10.0, step=10.0, key="inv_m")
            ipalancamiento = st.selectbox("APAL.", ["x100", "x500", "x1000"], index=2, key="apa_m")
            
            st.markdown(f"<div style='text-align:center; color:#8b949e; font-size:10px; margin-top:5px;'>SPREAD: 0.00012</div>", unsafe_allow_html=True)
            st.write("")

            # Botones de Operación
            if st.button("↗ COMPRA", key="btn_buy", use_container_width=True):
                s20 = df_datos["SMA_20"].iloc[-1] if "SMA_20" in df_datos.columns else p_act
                ganancia = inversion * 0.85
                pnl = ganancia if p_act >= s20 else -inversion
                
                st.session_state["saldo_demo"] += pnl
                st.session_state["historial_trades"].append({
                    "H": datetime.now().strftime("%H:%M"),
                    "T": "BUY ↗",
                    "A": par_seleccionado,
                    "Pnl": f"{pnl:.2f}"
                })
                st.rerun()

            st.write("")

            if st.button("↘ VENTA", key="btn_sell", use_container_width=True):
                s20 = df_datos["SMA_20"].iloc[-1] if "SMA_20" in df_datos.columns else p_act
                ganancia = inversion * 0.85
                pnl = ganancia if p_act <= s20 else -inversion
                
                st.session_state["saldo_demo"] += pnl
                st.session_state["historial_trades"].append({
                    "H": datetime.now().strftime("%H:%M"),
                    "T": "SELL ↘",
                    "A": par_seleccionado,
                    "Pnl": f"{pnl:.2f}"
                })
                st.rerun()
            
            st.markdown('</div>', unsafe_allow_html=True) # Cierre panel-section
            st.markdown('</div>', unsafe_allow_html=True) # Cierre broker-layout-container

    # ------------------ PESTAÑA 2: HISTORIAL ------------------
    with tabs[1]:
        st.subheader("📋 Últimos Trades")
        if st.session_state["historial_trades"]:
            df_trades = pd.DataFrame(st.session_state["historial_trades"])
            st.dataframe(df_trades.tail(10), use_container_width=True)
        else:
            st.info("No hay operaciones.")

    # ------------------ PESTAÑA 3: BACKTESTING ------------------
    with tabs[2]:
        st.subheader("🧪 Pruebas Retrospectivas")
        cap_init = st.number_input("Capital ($)", value=10000.0, step=100.0, key="cap_b")
        if st.button("Ejecutar", type="primary", key="btn_b"):
            df_bt, resumen = ejecutar_backtesting(df_datos, capital_inicial=cap_init)
            c1, c2, c3 = st.columns(3)
            c1.metric("Final", resumen["Capital Final"])
            c2.metric("Rend.", resumen["Rendimiento Total"])
            c3.metric("Win%", resumen["Win Rate"])

    # ------------------ PESTAÑA 4: IA ------------------
    with tabs[3]:
        st.subheader("🤖 Diagnóstico IA")
        if st.button("Generar", type="primary", key="btn_ia"):
            s20_act = float(df_datos["SMA_20"].iloc[-1]) if "SMA_20" in df_datos.columns else p_act
            s50_act = float(df_datos["SMA_50"].iloc[-1]) if "SMA_50" in df_datos.columns else p_act
            sen_act = int(df_datos["Senal"].iloc[-1]) if "Senal" in df_datos.columns else 0
            inf_ia = generar_informe_analista(par_seleccionado, temporalidad_seleccionada, p_act, r_act, s20_act, s50_act, sen_act, {})
            st.markdown(inf_ia)

else:
    st.error(f"Error: {mensaje_estado}")



