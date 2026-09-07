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

# ------------------ CONFIGURACIÓN DE PÁGINA Y ESTILOS AVANZADOS ------------------
st.set_page_config(page_title="XPace Broker — Terminal", layout="wide", page_icon="📈")

# Inicialización de estado de cuenta demo
if "saldo_demo" not in st.session_state:
    st.session_state["saldo_demo"] = 13449.67

if "historial_trades" not in st.session_state:
    st.session_state["historial_trades"] = []

# CSS avanzado para replicar la interfaz oscura estilo IQ Option/Deriv
st.markdown("""
    <style>
    /* Fondo General y Reset de Espacios */
    .stApp {
        background-color: #0d1117;
        color: #e6edf3;
        margin: 0 !important;
        padding: 0 !important;
    }
    
    /* Eliminar paddings superiores molestos */
    .block-container {
        padding-top: 0rem !important;
        padding-bottom: 0rem !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
    }

    [data-testid="stHeader"] {background: rgba(0,0,0,0); padding-top: 2.5rem;}
    [data-testid="stSidebar"] {background-color: #12161c;}

    /* ---------------------------------------------------- */
    /* 1. Header Superior (Barra de Cuenta) */
    /* ---------------------------------------------------- */
    .broker-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        background-color: #161b22;
        padding: 10px 25px;
        border-radius: 8px;
        margin-top: 10px;
        margin-bottom: 10px;
        border: 1px solid #21262d;
    }
    .balance-title {
        color: #8b949e;
        font-size: 11px;
        font-weight: bold;
        text-transform: uppercase;
    }
    .balance-value {
        color: #f2a900;
        font-size: 26px;
        font-weight: 800;
    }
    
    /* Botón de Depósito */
    div.stButton > button[key="btn_deposit"] {
        background-color: #00c076 !important;
        color: #000000 !important;
        font-size: 14px !important;
        font-weight: 900 !important;
        height: 38px !important;
        border-radius: 6px !important;
        border: none !important;
        box-shadow: 0px 4px 10px rgba(0, 192, 118, 0.3);
    }
    div.stButton > button[key="btn_deposit"]:hover {
        background-color: #00e676 !important;
    }

    /* ---------------------------------------------------- */
    /* 2. Layout Principal: Gráfico + Panel Lado a Lado */
    /* ---------------------------------------------------- */
    .main-broker-layout {
        display: flex;
        flex-direction: row;
        width: 100%;
        margin-top: 10px;
    }
    
    .chart-container {
        flex: 3; /* 75% del ancho */
        padding-right: 15px;
    }
    
    .panel-container {
        flex: 1; /* 25% del ancho */
        background-color: #161b22;
        padding: 20px;
        border-radius: 8px;
        border-left: 1px solid #21262d;
        display: flex;
        flex-direction: column;
        justify-content: flex-start;
    }

    /* ---------------------------------------------------- */
    /* 3. Botones Gigantes de Operación Profesional */
    /* ---------------------------------------------------- */
    /* Estilo para los botones en Streamlit */
    div.stButton > button[key="btn_buy"] {
        background-color: #00e676 !important;
        color: #000000 !important;
        font-size: 18px !important;
        font-weight: 900 !important;
        height: 60px !important;
        border-radius: 8px !important;
        border: none !important;
        box-shadow: 0px 4px 15px rgba(0, 230, 118, 0.3);
    }
    div.stButton > button[key="btn_buy"]:hover {
        background-color: #00ff7f !important;
    }

    div.stButton > button[key="btn_sell"] {
        background-color: #ff1744 !important;
        color: #ffffff !important;
        font-size: 18px !important;
        font-weight: 900 !important;
        height: 60px !important;
        border-radius: 8px !important;
        border: none !important;
        box-shadow: 0px 4px 15px rgba(255, 23, 68, 0.3);
    }
    div.stButton > button[key="btn_sell"]:hover {
        background-color: #ff3b30 !important;
    }
    
    /* ---------------------------------------------------- */
    /* 4. Estilos de Inputs y Métricas */
    /* ---------------------------------------------------- */
    .stNumberInput > div > div > input {
        background-color: #0d1117 !important;
        color: #e6edf3 !important;
        border: 1px solid #30363d !important;
    }
    .stSelectbox > div > div > div {
        background-color: #0d1117 !important;
        color: #e6edf3 !important;
    }
    
    /* Estilos para el texto deSpread */
    .spread-label {
        text-align: center;
        color: #8b949e;
        font-size: 11px;
        margin-top: 8px;
    }
    </style>
""", unsafe_allow_html=True)

# ------------------ TOP BAR / HEADER BROKER ------------------
with st.container():
    col_h1, col_h2, col_h3 = st.columns([1.5, 2, 0.6])
    
    with col_h1:
        # Menú simulado de pestañas horizontales superiores
        st.markdown(f"""
            <div style="font-size: 14px; font-weight: bold;">
                <span style="color:#f2a900; border-bottom:2px solid #f2a900; padding-bottom:5px;">USD/JPY</span>&nbsp;&nbsp;&nbsp;
                <span style="color:#8b949e;">EUR/USD</span>&nbsp;&nbsp;&nbsp;
                <span style="color:#8b949e;">GBP/USD</span>&nbsp;&nbsp;&nbsp;
                <span style="color:#8b949e;">+</span>
            </div>
        """, unsafe_allow_html=True)

    with col_h2:
        st.markdown(f"""
            <div style="text-align: right;">
                <span class="balance-title">CUENTA DE PRÁCTICA</span><br>
                <span class="balance-value">${st.session_state['saldo_demo']:,.2f}</span>
            </div>
        """, unsafe_allow_html=True)

    with col_h3:
        if st.button("💵 +DEPÓSITO", type="primary", use_container_width=True, key="btn_deposit"):
            st.session_state["saldo_demo"] += 10000.0
            st.rerun()

st.write("---")

# ------------------ BARRA LATERAL (SELECTOR ACTIVO Y TEMPORALIDAD DE FORMA COMPACTA) ------------------
st.sidebar.header("🪙 Activo")
par_seleccionado = st.sidebar.selectbox("Seleccionar Activo", ["USD/JPY", "EUR/USD", "GBP/USD"])

# Carga de datos
df_datos, mensaje_estado = obtener_historico(par=par_seleccionado, temporalidad="1 Hora (H1)", cantidad=150)

if df_datos is not None and not df_datos.empty and "Close" in df_datos.columns:
    df_datos = calcular_indicadores(df_datos)
    df_datos = generar_senales(df_datos)

    p_act = float(df_datos["Close"].iloc[-1])
    col_rsi_name = "RSI_14" if "RSI_14" in df_datos.columns else ("RSI" if "RSI" in df_datos.columns else None)
    r_act = float(df_datos[col_rsi_name].iloc[-1]) if col_rsi_name else 50.0

    # ------------------ LAYOUT PRINCIPAL BROKER STYLE ------------------
    col_grafico, col_operativa = st.columns([3, 1])

    # COLUMNA IZQUIERDA: GRÁFICO TÉCNICO
    with col_grafico:
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
            fig.add_trace(go.Scatter(x=df_datos.index, y=df_datos['SMA_20'], line=dict(color='#29b6f6', width=1.5), name='SMA 20'))
        if "SMA_50" in df_datos.columns:
            fig.add_trace(go.Scatter(x=df_datos.index, y=df_datos['SMA_50'], line=dict(color='#ff9800', width=1.5), name='SMA 50'))

        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="#0d1117", plot_bgcolor="#161b22",
            height=600,
            xaxis_rangeslider_visible=False,
            margin=dict(l=10, r=10, t=10, b=10),
            yaxis=dict(side="right", gridcolor="#21262d"),
            xaxis=dict(gridcolor="#21262d")
        )

        st.plotly_chart(fig, use_container_width=True)


    # COLUMNA DERECHA: PANEL DE COMANDOS (REPLICANDO IQ OPTION)
    with col_operativa:
        st.subheader("ORDEN RÁPIDA")
        
        inversion = st.number_input("INVERSIÓN ($)", min_value=1.0, value=100.0, step=10.0)
        ipalancamiento = st.selectbox("APALANCAMIENTO", ["x100", "x500", "x1000"], index=2)
        
        # Métrica de spread simulada
        spread_sim = 0.00012
        st.markdown(f"""
            <div class="spread-label">SPREAD: <b>{spread_sim}</b></div>
            <div style="text-align:center; color:#f2a900; font-size:18px; font-weight:800; margin-top:10px;">{p_act:.5f}</div>
        """, unsafe_allow_html=True)
        st.write("")

        # Botón de Compra
        if st.button(f"↗ COMPRAR", key="btn_buy", use_container_width=True):
            if st.session_state["saldo_demo"] >= inversion:
                s20 = df_datos["SMA_20"].iloc[-1] if "SMA_20" in df_datos.columns else p_act
                
                # Simulación de resultado técnico
                es_ganador = p_act >= s20
                pnl = (inversion * 0.85) if es_ganador else (-inversion)
                
                st.session_state["saldo_demo"] += pnl
                st.session_state["historial_trades"].append({
                    "H": datetime.now().strftime("%H:%M"),
                    "Tipo": "BUY ↗",
                    "A": par_seleccionado,
                    "Pnl": f"{pnl:.2f}"
                })
                
                if es_ganador:
                    st.success(f"✅ Trade Exitoso: +${pnl:.2f} USD")
                else:
                    st.error(f"❌ Trade Fallido: -${abs(pnl):.2f} USD")
                st.rerun()
            else:
                st.warning("Saldo insuficiente.")

        st.write("")

        # Botón de Venta
        if st.button(f"↘ VENDER", key="btn_sell", use_container_width=True):
            if st.session_state["saldo_demo"] >= inversion:
                s20 = df_datos["SMA_20"].iloc[-1] if "SMA_20" in df_datos.columns else p_act
                es_ganador = p_act <= s20
                pnl = (inversion * 0.85) if es_ganador else (-inversion)
                
                st.session_state["saldo_demo"] += pnl
                st.session_state["historial_trades"].append({
                    "H": datetime.now().strftime("%H:%M"),
                    "Tipo": "SELL ↘",
                    "A": par_seleccionado,
                    "Pnl": f"{pnl:.2f}"
                })
                
                if es_ganador:
                    st.success(f"✅ Trade Exitoso: +${pnl:.2f} USD")
                else:
                    st.error(f"❌ Trade Fallido: -${abs(pnl):.2f} USD")
                st.rerun()
            else:
                st.warning("Saldo insuficiente.")
        
        # Selectores de temporalidad compactos debajo de botones de operación
        st.write("---")
        temporalidad_seleccionada = st.radio("Temporalidad Gráfico", ["M15", "H1", "H4"], index=1, horizontal=True)

        # ------------------ PESTAÑAS SECUNDARIAS COMPACTAS (IA & BACKTESTING) ------------------
        with st.expander("🤖 Diagnóstico IA & 🧪 Backtesting"):
            st.markdown("---")
            st.subheader("🧪 Pruebas Retrospectivas")
            cap_init = st.number_input("Capital Inicial ($)", value=10000.0, step=100.0, key="cap_b")
            if st.button("Ejecutar Test", type="primary", key="btn_b"):
                df_bt, resumen = ejecutar_backtesting(df_datos, capital_inicial=cap_init)
                mc1, mc2, mc3 = st.columns(3)
                mc1.metric("Final", resumen["Capital Final"])
                mc2.metric("Rend.", resumen["Rendimiento Total"])
                mc3.metric("Win%", resumen["Win Rate"])

            st.markdown("---")
            st.subheader("🤖 Diagnóstico IA")
            if st.button("Generar Informe", type="primary", key="btn_ia"):
                s20_act = float(df_datos["SMA_20"].iloc[-1]) if "SMA_20" in df_datos.columns else p_act
                s50_act = float(df_datos["SMA_50"].iloc[-1]) if "SMA_50" in df_datos.columns else p_act
                sen_act = int(df_datos["Senal"].iloc[-1]) if "Senal" in df_datos.columns else 0
                inf_ia = generar_informe_analista(par_seleccionado, temporalidad_seleccionada, p_act, r_act, s20_act, s50_act, sen_act, {})
                st.markdown(inf_ia)

else:
    st.error(f"Error al conectar con la fuente de datos: {mensaje_estado}")




