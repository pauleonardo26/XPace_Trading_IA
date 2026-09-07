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

# Configuración inicial de la página
st.set_page_config(page_title="XPace Trading IA", layout="wide", page_icon="📈")

# Estilos CSS oscuros para interfaz estilo Terminal Profesional
st.markdown("""
    <style>
    .stApp {
        background-color: #0b0e14;
        color: #e1e3e6;
    }
    div[data-testid="stMetricValue"] {
        font-size: 22px;
        font-weight: bold;
    }
    .buy-card {
        background-color: #0e2a1f;
        border: 1px solid #00c076;
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 10px;
    }
    .sell-card {
        background-color: #2a0e12;
        border: 1px solid #ff3b30;
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 10px;
    }
    </style>
""", unsafe_allow_html=True)

st.title("📈 XPace Trading IA — Terminal Cuantitativa")

# ------------------ BARRA LATERAL ------------------
st.sidebar.header("⚙️ Configuración del Mercado")
par_seleccionado = st.sidebar.selectbox("Par de Divisas", ["EUR/USD", "GBP/USD", "USD/JPY"])
temporalidad_seleccionada = st.sidebar.selectbox("Temporalidad", ["15 Minutos (M15)", "1 Hora (H1)", "4 Horas (H4)", "1 Día (D1)"])
cantidad_velas = st.sidebar.slider("Cantidad de Velas", min_value=50, max_value=1000, value=150, step=50)

# Carga de datos
df_datos, mensaje_estado = obtener_historico(par=par_seleccionado, temporalidad=temporalidad_seleccionada, cantidad=cantidad_velas)

if df_datos is not None and not df_datos.empty and "Close" in df_datos.columns:
    df_datos = calcular_indicadores(df_datos)
    df_datos = generar_senales(df_datos)

    p_act = float(df_datos["Close"].iloc[-1])
    col_rsi_name = "RSI_14" if "RSI_14" in df_datos.columns else ("RSI" if "RSI" in df_datos.columns else None)
    r_act = float(df_datos[col_rsi_name].iloc[-1]) if col_rsi_name else 50.0

    # PESTAÑAS PRINCIPALES
    tab_terminal, tab_backtest, tab_ia = st.tabs(["📊 Terminal & Simulación", "🧪 Backtesting Historico", "🤖 Analista IA"])

    # ------------------ PESTAÑA 1: TERMINAL DE TRADING & SIMULACIÓN ------------------
    with tab_terminal:
        col_grafico, col_operativa = st.columns([2.5, 1])

        # COLUMNA IZQUIERDA: GRÁFICO TÉCNICO
        with col_grafico:
            st.subheader(f"Mercado: {par_seleccionado} ({temporalidad_seleccionada})")
            
            fig = make_subplots(
                rows=2, cols=1, 
                shared_xaxes=True, 
                vertical_spacing=0.03, 
                subplot_titles=(f"Precio {par_seleccionado}", "RSI (14)"),
                row_width=[0.25, 0.75]
            )

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

            if "SMA_20" in df_datos.columns:
                fig.add_trace(go.Scatter(x=df_datos.index, y=df_datos['SMA_20'], line=dict(color='#29b6f6', width=1.5), name='SMA 20'), row=1, col=1)
            if "SMA_50" in df_datos.columns:
                fig.add_trace(go.Scatter(x=df_datos.index, y=df_datos['SMA_50'], line=dict(color='#ff9800', width=1.5), name='SMA 50'), row=1, col=1)

            if col_rsi_name:
                fig.add_trace(go.Scatter(x=df_datos.index, y=df_datos[col_rsi_name], line=dict(color='#ab47bc', width=1.5), name='RSI'), row=2, col=1)
                fig.add_hline(y=70, line_dash="dash", line_color="#ff3b30", row=2, col=1)
                fig.add_hline(y=30, line_dash="dash", line_color="#00c076", row=2, col=1)

            fig.update_layout(
                template="plotly_dark",
                paper_bgcolor="#0b0e14",
                plot_bgcolor="#131722",
                height=550,
                xaxis_rangeslider_visible=False,
                margin=dict(l=10, r=10, t=30, b=10)
            )
            st.plotly_chart(fig, use_container_width=True)

        # COLUMNA DERECHA: DESPACHO DE ÓRDENES Y GESTIÓN DE RIESGO
        with col_operativa:
            st.subheader("⚡ Panel de Ejecución")
            st.metric("Precio Actual", f"{p_act:.5f}")

            st.write("---")
            st.markdown("##### 🛡️ Parámetros de Riesgo")
            cap_sim = st.number_input("Capital ($)", value=10000.0, step=1000.0)
            p_riesgo = st.slider("Riesgo por Trade (%)", 0.5, 3.0, 1.0, 0.5)
            sl_pips = st.number_input("Stop Loss (Pips)", value=20, step=5)

            # Cálculo interno de gestión de riesgo
            res_r, _ = calcular_riesgo_operacion(
                capital_total=cap_sim,
                porcentaje_riesgo=p_riesgo,
                precio_entrada=p_act,
                distancia_stop_loss_pips=sl_pips,
                relacion_rr=2.0,
                par=par_seleccionado
            )

            monto_riesgo = res_r.get("riesgo_monetario_usd", cap_sim * (p_riesgo / 100))
            lotes = res_r.get("tamano_posicion_lotes", 0.1)

            # Métrica estilizada (Reemplaza al formato JSON plano)
            m1, m2 = st.columns(2)
            m1.metric("Riesgo USD", f"${monto_riesgo:.2f}")
            m2.metric("Lotes", f"{lotes:.2f}")

            st.write("---")
            st.markdown("##### 🎯 Simulación Instantánea")
            
            btn_buy, btn_sell = st.columns(2)
            
            if btn_buy.button("🟢 COMPRAR", use_container_width=True):
                s20 = df_datos["SMA_20"].iloc[-1] if "SMA_20" in df_datos.columns else p_act
                # Lógica del resultado según tendencia
                if p_act >= s20 and r_act < 70:
                    ganancia = monto_riesgo * 2.0
                    st.success(f"✅ **¡Simulación Exitosa!** Entrada a favor de tendencia. Ganancia estimada: **+${ganancia:.2f} USD**.")
                else:
                    st.error(f"❌ **¡Stop Loss Alcanzado!** La entrada fue contra tendencia o con RSI sobrecomprado. Pérdida: **-${monto_riesgo:.2f} USD**.")

            if btn_sell.button("🔴 VENDER", use_container_width=True):
                s20 = df_datos["SMA_20"].iloc[-1] if "SMA_20" in df_datos.columns else p_act
                if p_act <= s20 and r_act > 30:
                    ganancia = monto_riesgo * 2.0
                    st.success(f"✅ **¡Simulación Exitosa!** Venta correcta en tendencia bajista. Ganancia estimada: **+${ganancia:.2f} USD**.")
                else:
                    st.error(f"❌ **¡Stop Loss Alcanzado!** Mercado rebotó en zona alcista. Pérdida: **-${monto_riesgo:.2f} USD**.")

    # ------------------ PESTAÑA 2: BACKTESTING ------------------
    with tab_backtest:
        st.subheader("🧪 Simulador de Rendimiento de Estrategia")
        cap_init = st.number_input("Capital Inicial ($ USD)", value=10000.0, step=500.0, key="bt_cap")
        
        if st.button("Ejecutar Backtesting", type="primary"):
            df_bt, resumen = ejecutar_backtesting(df_datos, capital_inicial=cap_init)
            
            mc1, mc2, mc3, mc4 = st.columns(4)
            mc1.metric("Capital Final", resumen["Capital Final"])
            mc2.metric("Rendimiento Total", resumen["Rendimiento Total"])
            mc3.metric("Win Rate", resumen["Win Rate"])
            mc4.metric("Total Operaciones", resumen["Total Operaciones"])
            
            st.write("---")
            if "Evolucion_Capital" in df_bt.columns:
                st.line_chart(df_bt["Evolucion_Capital"])

            if isinstance(resumen["Detalle Trades"], pd.DataFrame) and not resumen["Detalle Trades"].empty:
                st.dataframe(resumen["Detalle Trades"], use_container_width=True)

    # ------------------ PESTAÑA 3: ANALISTA IA ------------------
    with tab_ia:
        st.subheader("🤖 Diagnóstico Cuantitativo del Analista IA")
        if st.button("Generar Informe Completo", type="primary"):
            s20_act = float(df_datos["SMA_20"].iloc[-1]) if "SMA_20" in df_datos.columns else p_act
            s50_act = float(df_datos["SMA_50"].iloc[-1]) if "SMA_50" in df_datos.columns else p_act
            sen_act = int(df_datos["Senal"].iloc[-1]) if "Senal" in df_datos.columns else 0
            
            inf_ia = generar_informe_analista(par_seleccionado, temporalidad_seleccionada, p_act, r_act, s20_act, s50_act, sen_act, res_r)
            st.markdown(inf_ia)

else:
    st.error(f"Error al cargar datos: {mensaje_estado}")

