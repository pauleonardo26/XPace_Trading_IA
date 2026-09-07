import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

from historico import obtener_historico
from indicadores import calcular_indicadores
from estrategias import generar_senales
from backtesting import ejecutar_backtesting
from ia_analista import generar_informe_analista

# ------------------ CONFIGURACIÓN PANTALLA COMPLETA ------------------
st.set_page_config(
    page_title="XPace — IQ Option Interface",
    layout="wide",
    initial_sidebar_state="collapsed",
    page_icon="📈"
)

# Estados Globales
if "saldo_demo" not in st.session_state:
    st.session_state["saldo_demo"] = 13449.67

if "historial_trades" not in st.session_state:
    st.session_state["historial_trades"] = []

if "activo_actual" not in st.session_state:
    st.session_state["activo_actual"] = "BTC/USD"

if "tf_actual" not in st.session_state:
    st.session_state["tf_actual"] = "1D"

# ------------------ CSS INYECTADO: LIMPIEZA ABSOLUTA DE STREAMLIT ------------------
st.markdown("""
    <style>
    /* 1. Eliminar absolutamente todos los márgenes y cabeceras de Streamlit */
    [data-testid="stSidebar"] { display: none !important; }
    [data-testid="stHeader"] { display: none !important; }
    footer { display: none !important; }
    #MainMenu { visibility: hidden; }
    
    /* 2. Fondo general ultra oscuro estilo IQ Option */
    .stApp {
        background-color: #0b0e14 !important;
        color: #e6edf3 !important;
    }
    
    .block-container {
        padding: 0px 8px 0px 8px !important;
        max-width: 100% !important;
    }

    /* 3. Top Bar Minimalista */
    .iq-topbar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        background-color: #12161f;
        padding: 4px 12px;
        border-bottom: 1px solid #1a202c;
    }
    .iq-tab-active {
        background-color: #1a2230;
        padding: 4px 12px;
        border-radius: 4px 4px 0 0;
        color: #ffffff;
        font-weight: bold;
        font-size: 12px;
        border-top: 2px solid #ff9800;
        display: inline-block;
    }
    .iq-tab-inactive {
        padding: 4px 10px;
        color: #5c697d;
        font-size: 12px;
        display: inline-block;
    }
    .iq-balance-title {
        font-size: 9px;
        color: #5c697d;
        font-weight: 700;
        text-align: right;
    }
    .iq-balance-value {
        color: #ffb300;
        font-size: 18px;
        font-weight: 800;
    }

    /* 4. Panel Operativo Derecho */
    .iq-panel {
        background-color: #12161f;
        padding: 10px;
        border-radius: 6px;
        border: 1px solid #1a202c;
    }
    
    /* Reducir tamaño de inputs */
    .stNumberInput > div > div > input {
        background-color: #0b0e14 !important;
        color: #ffffff !important;
        border: 1px solid #232d3f !important;
        font-weight: bold !important;
        text-align: right !important;
    }

    /* 5. Botones Gigantes IQ Option COMPRA / VENTA */
    div.stButton > button[key="btn_buy"] {
        background: linear-gradient(180deg, #00e676 0%, #00b0ff 100%) !important;
        background-color: #00e676 !important;
        color: #000000 !important;
        font-size: 16px !important;
        font-weight: 900 !important;
        height: 60px !important;
        border-radius: 6px !important;
        border: none !important;
        box-shadow: 0 4px 12px rgba(0, 230, 118, 0.2) !important;
    }
    
    div.stButton > button[key="btn_sell"] {
        background: linear-gradient(180deg, #ff1744 0%, #d50000 100%) !important;
        background-color: #ff1744 !important;
        color: #ffffff !important;
        font-size: 16px !important;
        font-weight: 900 !important;
        height: 60px !important;
        border-radius: 6px !important;
        border: none !important;
        box-shadow: 0 4px 12px rgba(255, 23, 68, 0.2) !important;
    }

    div.stButton > button[key="btn_depo"] {
        background-color: #00c076 !important;
        color: #000000 !important;
        font-weight: 800 !important;
        height: 32px !important;
        border: none !important;
        border-radius: 4px !important;
        font-size: 12px !important;
    }
    
    /* Ocultar etiquetas de Streamlit molestas */
    label { color: #8b949e !important; font-size: 11px !important; }
    </style>
""", unsafe_allow_html=True)

# ------------------ BARRA SUPERIOR LIMPIA ------------------
st.markdown(f"""
    <div class="iq-topbar">
        <div>
            <span style="font-size: 16px; color:#ff9800; font-weight:bold; margin-right:10px;">≡ &nbsp; +</span>
            <span class="iq-tab-active">🟧 {st.session_state['activo_actual']}</span>
            <span class="iq-tab-inactive">🇦🇺 AUD/USD</span>
            <span class="iq-tab-inactive">🇪🇺 EUR/USD</span>
            <span class="iq-tab-inactive">🇺🇸 US 500</span>
        </div>
        <div>
            <div class="iq-balance-title">CUENTA DE PRÁCTICA</div>
            <div class="iq-balance-value">${st.session_state['saldo_demo']:,.2f}</div>
        </div>
    </div>
""", unsafe_allow_html=True)

# Depósito alineado a la derecha
_, c_dep = st.columns([9, 1])
with c_dep:
    if st.button("+DEPÓSITO", key="btn_depo", use_container_width=True):
        st.session_state["saldo_demo"] += 10000.0
        st.rerun()

# ------------------ CARGA Y PREPARACIÓN DE DATOS ------------------
tf_map = {"1D": "1 Día (D1)", "1H": "1 Hora (H1)", "1M": "15 Minutos (M15)"}
tf_sel = tf_map.get(st.session_state["tf_actual"], "1 Día (D1)")

df_datos, mensaje_estado = obtener_historico(par="USD/JPY", temporalidad=tf_sel, cantidad=80)

if df_datos is not None and not df_datos.empty and "Close" in df_datos.columns:
    df_datos = calcular_indicadores(df_datos)
    df_datos = generar_senales(df_datos)

    p_act = float(df_datos["Close"].iloc[-1])
    p_max = float(df_datos["High"].max()) if "High" in df_datos.columns else p_act
    p_min = float(df_datos["Low"].min()) if "Low" in df_datos.columns else p_act

    # ------------------ LAYOUT 85% GRÁFICO / 15% PANEL ------------------
    col_chart, col_panel = st.columns([4.5, 1])

    # --- COLUMNA 1: GRÁFICO LIMPIO DE VELAS ---
    with col_chart:
        fig = go.Figure()

        # Velas Japonesas Nitidas
        fig.add_trace(go.Candlestick(
            x=df_datos.index,
            open=df_datos['Open'] if 'Open' in df_datos.columns else df_datos['Close'],
            high=df_datos['High'] if 'High' in df_datos.columns else df_datos['Close'],
            low=df_datos['Low'] if 'Low' in df_datos.columns else df_datos['Close'],
            close=df_datos['Close'],
            increasing_line_color='#00e676', increasing_fillcolor='#00e676',
            decreasing_line_color='#ff1744', decreasing_fillcolor='#ff1744',
            whiskerwidth=0.4
        ))

        # Configuración para que NO SALTE al tocar la pantalla
        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="#0b0e14",
            plot_bgcolor="#0b0e14",
            height=480,
            xaxis_rangeslider_visible=False,
            margin=dict(l=0, r=40, t=10, b=0),
            yaxis=dict(
                side="right",
                gridcolor="#151a23",
                zeroline=False,
                showline=False,
                tickfont=dict(color="#5c697d", size=10)
            ),
            xaxis=dict(
                gridcolor="#151a23",
                zeroline=False,
                showline=False,
                tickfont=dict(color="#5c697d", size=10)
            ),
            hovermode=False # Desactiva popups molestos al tocar la pantalla
        )

        # Render sin barra de herramientas flotante
        st.plotly_chart(
            fig, 
            use_container_width=True, 
            config={
                'displayModeBar': False,
                'scrollZoom': False,
                'doubleClick': False
            }
        )

        # Barra de temporalidad limpia e inferior
        b1, b2, b3, _, b_time = st.columns([0.8, 0.8, 0.8, 4, 2])
        if b1.button("1D", key="t_1d"):
            st.session_state["tf_actual"] = "1D"
            st.rerun()
        if b2.button("1H", key="t_1h"):
            st.session_state["tf_actual"] = "1H"
            st.rerun()
        if b3.button("1M", key="t_1m"):
            st.session_state["tf_actual"] = "1M"
            st.rerun()
        b_time.markdown(f"<div style='text-align:right; color:#5c697d; font-size:11px;'>{datetime.now().strftime('%d %b %H:%M:%S')}</div>", unsafe_allow_html=True)

    # --- COLUMNA 2: PANEL DE CONTROL IQ OPTION ---
    with col_panel:
        st.markdown('<div class="iq-panel">', unsafe_allow_html=True)
        
        inversion = st.number_input("INVERSIÓN", min_value=1.0, value=1.0, step=1.0)
        
        st.markdown("""
            <div style="display:flex; justify-content:space-between; margin-top:8px; font-size:11px; color:#8b949e;">
                <span>APALANCAMIENTO</span><b style="color:#ffffff;">×1000</b>
            </div>
            <div style="font-size:10px; color:#5c697d; margin-top:4px;">PRECIO MERCADO</div>
        """, unsafe_allow_html=True)
        
        st.write("")

        # BOTÓN DE COMPRA
        if st.button(f"↗ COMPRAR\n{p_act:.2f}", key="btn_buy", use_container_width=True):
            if st.session_state["saldo_demo"] >= inversion:
                s20 = df_datos["SMA_20"].iloc[-1] if "SMA_20" in df_datos.columns else p_act
                pnl = (inversion * 0.85) if p_act >= s20 else (-inversion)
                st.session_state["saldo_demo"] += pnl
                st.session_state["historial_trades"].append({"Tipo": "BUY", "PnL": pnl, "Hora": datetime.now().strftime("%H:%M")})
                st.rerun()

        st.markdown("<div style='text-align:center; font-size:10px; color:#5c697d; margin: 6px 0;'>SPREAD &nbsp; 14.100</div>", unsafe_allow_html=True)

        # BOTÓN DE VENTA
        if st.button(f"↘ VENDER\n{p_act:.2f}", key="btn_sell", use_container_width=True):
            if st.session_state["saldo_demo"] >= inversion:
                s20 = df_datos["SMA_20"].iloc[-1] if "SMA_20" in df_datos.columns else p_act
                pnl = (inversion * 0.85) if p_act <= s20 else (-inversion)
                st.session_state["saldo_demo"] += pnl
                st.session_state["historial_trades"].append({"Tipo": "SELL", "PnL": pnl, "Hora": datetime.now().strftime("%H:%M")})
                st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

    # ------------------ HERRAMIENTAS ADICIONALES GUARDADAS ABAJO ------------------
    st.write("")
    with st.expander("⚙️ Herramientas de Análisis IA & Historial"):
        t_hist, t_bt, t_ia = st.tabs(["📋 Historial", "🧪 Backtesting", "🤖 Analista IA"])
        
        with t_hist:
            if st.session_state["historial_trades"]:
                st.dataframe(pd.DataFrame(st.session_state["historial_trades"]), use_container_width=True)
            else:
                st.info("Sin operaciones registradas.")
                
        with t_bt:
            if st.button("Ejecutar Test de Estrategia"):
                _, res = ejecutar_backtesting(df_datos, capital_inicial=10000.0)
                st.json(res)
                
        with t_ia:
            if st.button("Generar Diagnóstico IA"):
                s20_act = float(df_datos["SMA_20"].iloc[-1]) if "SMA_20" in df_datos.columns else p_act
                s50_act = float(df_datos["SMA_50"].iloc[-1]) if "SMA_50" in df_datos.columns else p_act
                r_act = float(df_datos["RSI_14"].iloc[-1]) if "RSI_14" in df_datos.columns else 50.0
                st.markdown(generar_informe_analista("BTC/USD", tf_sel, p_act, r_act, s20_act, s50_act, 1, {}))

else:
    st.error(f"Error al conectar con el servidor de datos: {mensaje_estado}")





