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

# ------------------ CONFIGURACIÓN DE PÁGINA Y ESTILOS IQ OPTION ------------------
st.set_page_config(page_title="XPace Broker — Terminal", layout="wide", page_icon="📈")

# Inicialización de estado de cuenta demo
if "saldo_demo" not in st.session_state:
    st.session_state["saldo_demo"] = 13449.67

if "historial_trades" not in st.session_state:
    st.session_state["historial_trades"] = []

# CSS avanzado para replicar la interfaz oscura estilo IQ Option
st.markdown("""
    <style>
    /* Fondo General estilo Broker */
    .stApp {
        background-color: #0d1117;
        color: #e6edf3;
    }
    
    /* Header Superior de Cuenta */
    .header-container {
        display: flex;
        justify-content: space-between;
        align-items: center;
        background-color: #161b22;
        padding: 10px 20px;
        border-radius: 8px;
        margin-bottom: 15px;
        border: 1px solid #21262d;
    }
    .balance-title {
        color: #8b949e;
        font-size: 12px;
        font-weight: bold;
        text-transform: uppercase;
    }
    .balance-value {
        color: #f2a900;
        font-size: 24px;
        font-weight: 800;
    }
    
    /* Botones de Operación Profesionales */
    div.stButton > button[key="btn_buy"] {
        background-color: #00e676 !important;
        color: #000000 !important;
        font-size: 20px !important;
        font-weight: 900 !important;
        height: 65px !important;
        border-radius: 8px !important;
        border: none !important;
        box-shadow: 0px 4px 15px rgba(0, 230, 118, 0.3);
    }
    div.stButton > button[key="btn_sell"] {
        background-color: #ff1744 !important;
        color: #ffffff !important;
        font-size: 20px !important;
        font-weight: 900 !important;
        height: 65px !important;
        border-radius: 8px !important;
        border: none !important;
        box-shadow: 0px 4px 15px rgba(255, 23, 68, 0.3);
    }
    
    /* Cajas de métricas */
    .stat-box {
        background-color: #161b22;
        border: 1px solid #30363d;
        border-radius: 6px;
        padding: 10px;
        text-align: center;
    }
    </style>
""", unsafe_allow_html=True)

# ------------------ TOP BAR / HEADER BROKER ------------------
col_h1, col_h2, col_h3 = st.columns([2, 2, 1])

with col_h1:
    st.markdown("### 📈 **XPace Terminal**")

with col_h2:
    st.markdown(f"""
        <div style="text-align: right;">
            <span class="balance-title">CUENTA DE PRÁCTICA</span><br>
            <span class="balance-value">${st.session_state['saldo_demo']:,.2f}</span>
        </div>
    """, unsafe_allow_html=True)

with col_h3:
    if st.button("💵 +DEPÓSITO", type="primary", use_container_width=True):
        st.session_state["saldo_demo"] += 10000.0
        st.rerun()

st.write("---")

# ------------------ BARRA LATERAL (SELECCIÓN) ------------------
st.sidebar.header("🪙 Activo & Temporalidad")
par_seleccionado = st.sidebar.selectbox("Seleccionar Activo", ["EUR/USD", "GBP/USD", "USD/JPY"])
temporalidad_seleccionada = st.sidebar.selectbox("Temporalidad", ["15 Minutos (M15)", "1 Hora (H1)", "4 Horas (H4)", "1 Día (D1)"])
cantidad_velas = st.sidebar.slider("Velas en pantalla", 50, 500, 150)

# Carga de datos
df_datos, mensaje_estado = obtener_historico(par=par_seleccionado, temporalidad=temporalidad_seleccionada, cantidad=cantidad_velas)

if df_datos is not None and not df_datos.empty and "Close" in df_datos.columns:
    df_datos = calcular_indicadores(df_datos)
    df_datos = generar_senales(df_datos)

    p_act = float(df_datos["Close"].iloc[-1])
    p_max = float(df_datos["High"].max()) if "High" in df_datos.columns else p_act
    p_min = float(df_datos["Low"].min()) if "Low" in df_datos.columns else p_act
    col_rsi_name = "RSI_14" if "RSI_14" in df_datos.columns else ("RSI" if "RSI" in df_datos.columns else None)
    r_act = float(df_datos[col_rsi_name].iloc[-1]) if col_rsi_name else 50.0

    # PESTAÑAS PRINCIPALES DE NAVEGACIÓN
    tab_trade, tab_historial, tab_backtest, tab_ia = st.tabs(["📊 OPERAR (DEMO)", "📋 POSICIONES", "🧪 BACKTESTING", "🤖 ANALISTA IA"])

    # ------------------ PESTAÑA 1: TERMINAL DE OPERACIÓN ESTILO BROKER ------------------
    with tab_trade:
        col_chart, col_panel = st.columns([3, 1])

        # CENTRO: GRÁFICO TIPO IQ OPTION
        with col_chart:
            fig = go.Figure()

            # Velas Japonesas
            fig.add_trace(go.Candlestick(
                x=df_datos.index,
                open=df_datos['Open'] if 'Open' in df_datos.columns else df_datos['Close'],
                high=df_datos['High'] if 'High' in df_datos.columns else df_datos['Close'],
                low=df_datos['Low'] if 'Low' in df_datos.columns else df_datos['Close'],
                close=df_datos['Close'],
                name=par_seleccionado,
                increasing_line_color='#00e676',
                decreasing_line_color='#ff1744',
                increasing_fillcolor='#00e676',
                decreasing_fillcolor='#ff1744'
            ))

            # Medias móviles
            if "SMA_20" in df_datos.columns:
                fig.add_trace(go.Scatter(x=df_datos.index, y=df_datos['SMA_20'], line=dict(color='#29b6f6', width=1.5), name='SMA 20'))
            if "SMA_50" in df_datos.columns:
                fig.add_trace(go.Scatter(x=df_datos.index, y=df_datos['SMA_50'], line=dict(color='#ff9800', width=1.5), name='SMA 50'))

            # Anotaciones Estilo IQ Option (Máximo y Mínimo en gráfico)
            fig.add_annotation(x=df_datos.index[-10], y=p_max, text=f"Máx. {p_max:.5f}", showarrow=True, arrowhead=2, arrowcolor="#00e676", font=dict(color="#00e676", size=12))
            fig.add_annotation(x=df_datos.index[10], y=p_min, text=f"Mín. {p_min:.5f}", showarrow=True, arrowhead=2, arrowcolor="#ff1744", font=dict(color="#ff1744", size=12))

            fig.update_layout(
                template="plotly_dark",
                paper_bgcolor="#0d1117",
                plot_bgcolor="#161b22",
                height=600,
                xaxis_rangeslider_visible=False,
                margin=dict(l=5, r=5, t=10, b=5),
                yaxis=dict(side="right", gridcolor="#21262d"),
                xaxis=dict(gridcolor="#21262d")
            )

            st.plotly_chart(fig, use_container_width=True)

        # DERECHA: DESPACHO DE ÓRDENES ESTILO BROKER
        with col_panel:
            st.markdown("#### **ORDEN RÁPIDA**")
            
            inversion = st.number_input("INVERSIÓN ($)", min_value=1.0, value=100.0, step=10.0)
            apalancamiento = st.selectbox("APALANCAMIENTO", ["x100", "x200", "x500", "x1000"], index=3)
            
            spread_sim = 0.00012
            st.markdown(f"<div style='text-align:center; color:#8b949e;'>SPREAD: <b>{spread_sim}</b></div>", unsafe_allow_html=True)
            st.write("")

            # Botón de Compra
            if st.button(f"↗ COMPRAR\n{p_act:.5f}", key="btn_buy", use_container_width=True):
                if st.session_state["saldo_demo"] >= inversion:
                    # Simulación de resultado técnico
                    s20 = df_datos["SMA_20"].iloc[-1] if "SMA_20" in df_datos.columns else p_act
                    es_ganador = p_act >= s20
                    pnl = (inversion * 0.85) if es_ganador else (-inversion)
                    
                    st.session_state["saldo_demo"] += pnl
                    st.session_state["historial_trades"].append({
                        "Fecha": datetime.now().strftime("%H:%M:%S"),
                        "Tipo": "COMPRA ↗",
                        "Activo": par_seleccionado,
                        "Inversión": f"${inversion:.2f}",
                        "Precio": f"{p_act:.5f}",
                        "Resultado": f"+${pnl:.2f}" if pnl > 0 else f"-${abs(pnl):.2f}"
                    })
                    
                    if es_ganador:
                        st.success(f"✅ Trade Exitoso: +${pnl:.2f} USD")
                    else:
                        st.error(f"❌ Trade Fallido: -${abs(pnl):.2f} USD")
                    st.rerun()
                else:
                    st.warning("Saldo insuficiente en la Cuenta Demo.")

            st.write("")

            # Botón de Venta
            if st.button(f"↘ VENDER\n{p_act:.5f}", key="btn_sell", use_container_width=True):
                if st.session_state["saldo_demo"] >= inversion:
                    s20 = df_datos["SMA_20"].iloc[-1] if "SMA_20" in df_datos.columns else p_act
                    es_ganador = p_act <= s20
                    pnl = (inversion * 0.85) if es_ganador else (-inversion)
                    
                    st.session_state["saldo_demo"] += pnl
                    st.session_state["historial_trades"].append({
                        "Fecha": datetime.now().strftime("%H:%M:%S"),
                        "Tipo": "VENTA ↘",
                        "Activo": par_seleccionado,
                        "Inversión": f"${inversion:.2f}",
                        "Precio": f"{p_act:.5f}",
                        "Resultado": f"+${pnl:.2f}" if pnl > 0 else f"-${abs(pnl):.2f}"
                    })
                    
                    if es_ganador:
                        st.success(f"✅ Trade Exitoso: +${pnl:.2f} USD")
                    else:
                        st.error(f"❌ Trade Fallido: -${abs(pnl):.2f} USD")
                    st.rerun()
                else:
                    st.warning("Saldo insuficiente en la Cuenta Demo.")

    # ------------------ PESTAÑA 2: POSICIONES Y HISTORIAL ------------------
    with tab_historial:
        st.subheader("📋 Historial de Operaciones en Demo")
        if st.session_state["historial_trades"]:
            df_trades = pd.DataFrame(st.session_state["historial_trades"])
            st.dataframe(df_trades, use_container_width=True)
        else:
            st.info("Aún no has ejecutado operaciones en la sesión actual.")

    # ------------------ PESTAÑA 3: BACKTESTING ------------------
    with tab_backtest:
        st.subheader("🧪 Simulador Cuantitativo de Estrategia")
        cap_init = st.number_input("Capital Inicial para Simulación ($)", value=10000.0, step=500.0)
        
        if st.button("Ejecutar Test Histórico", type="primary"):
            df_bt, resumen = ejecutar_backtesting(df_datos, capital_inicial=cap_init)
            
            mc1, mc2, mc3, mc4 = st.columns(4)
            mc1.metric("Capital Final", resumen["Capital Final"])
            mc2.metric("Rendimiento", resumen["Rendimiento Total"])
            mc3.metric("Win Rate", resumen["Win Rate"])
            mc4.metric("Total Trades", resumen["Total Operaciones"])
            
            if "Evolucion_Capital" in df_bt.columns:
                st.line_chart(df_bt["Evolucion_Capital"])

    # ------------------ PESTAÑA 4: ANALISTA IA ------------------
    with tab_ia:
        st.subheader("🤖 Diagnóstico en Vivo de la Inteligencia Artificial")
        if st.button("Generar Diagnóstico del Activo", type="primary"):
            s20_act = float(df_datos["SMA_20"].iloc[-1]) if "SMA_20" in df_datos.columns else p_act
            s50_act = float(df_datos["SMA_50"].iloc[-1]) if "SMA_50" in df_datos.columns else p_act
            sen_act = int(df_datos["Senal"].iloc[-1]) if "Senal" in df_datos.columns else 0
            
            res_r, _ = calcular_riesgo_operacion(
                capital_total=st.session_state["saldo_demo"],
                porcentaje_riesgo=1.0,
                precio_entrada=p_act,
                distancia_stop_loss_pips=20,
                relacion_rr=2.0,
                par=par_seleccionado
            )
            
            inf_ia = generar_informe_analista(par_seleccionado, temporalidad_seleccionada, p_act, r_act, s20_act, s50_act, sen_act, res_r)
            st.markdown(inf_ia)

else:
    st.error(f"Error al conectar con la fuente de datos: {mensaje_estado}")


