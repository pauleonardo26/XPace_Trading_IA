import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import date, timedelta
import yfinance as yf

# ------------------------------------------------------------------------------
# CONFIGURACIÓN GENERAL
# ------------------------------------------------------------------------------
st.set_page_config(page_title="XPace — Escuela de Trading", layout="wide", page_icon="🎓")

st.markdown("""
    <style>
    .stApp { background-color: #0b0e14 !important; color: #e6edf3 !important; }
    .block-container { padding-top: 1rem !important; max-width: 100% !important; }
    </style>
""", unsafe_allow_html=True)

st.title("🎓 XPace — Escuela de Trading")
st.caption("Aprende la estructura del mercado con estrategias trazadas directamente en el gráfico")

# DICCIONARIOS Y CONSTANTES
SIMBOLOS_FOREX = {
    "EUR/USD (Euro / Dólar)": "EURUSD=X",
    "USD/JPY (Dólar / Yen)": "JPY=X",
    "GBP/USD (Libra / Dólar)": "GBPUSD=X",
    "EUR/JPY (Euro / Yen)": "EURJPY=X"
}

TEMPORALIDADES_YAHOO = {
    "15 Minutos (4 velas por hora)": "15m",
    "1 Hora (1 vela por hora)": "60m",
    "1 Día (1 vela por día)": "1d",
    "1 Semana (1 vela por semana)": "1wk"
}

# ------------------------------------------------------------------------------
# PESTAÑAS PRINCIPALES
# ------------------------------------------------------------------------------
tab1, tab2, tab3 = st.tabs(["📈 Histórico Educativo", "🧪 Backtesting", "🤖 Evaluación IA"])

# ==============================================================================
# PESTAÑA 1: HISTÓRICO EDUCATIVO
# ==============================================================================
with tab1:
    st.write("### 📌 Filtros de Mercado")
    
    # FILTROS DE MERCADO
    col1, col2 = st.columns(2)
    with col1:
        par_sel = st.selectbox("Par de Forex", list(SIMBOLOS_FOREX.keys()), key="1.1_par")
        tf_sel = st.selectbox("Temporalidad (Duración de vela)", list(TEMPORALIDADES_YAHOO.keys()), key="1.1_tf")
    with col2:
        fecha_defecto = date.today() - timedelta(days=7)
        fecha_sel = st.date_input("Fecha a Consultar", value=fecha_defecto, max_value=date.today(), key="1.1_fecha", format="DD/MM/YYYY")

    if fecha_sel.weekday() >= 5:
        st.error("⚠️ Los sábados y domingos el mercado Forex no genera datos. Elige un día de lunes a viernes.")
    else:
        ticker = SIMBOLOS_FOREX[par_sel]
        intervalo = TEMPORALIDADES_YAHOO[tf_sel]
        
        start_dt = fecha_sel
        end_dt = fecha_sel + timedelta(days=1)

        with st.spinner("Cargando mercado e indicadores..."):
            try:
                df_datos = yf.download(tickers=ticker, start=start_dt, end=end_dt, interval=intervalo, progress=False)
                if isinstance(df_datos.columns, pd.MultiIndex):
                    df_datos.columns = df_datos.columns.get_level_values(0)
                df_datos = df_datos.dropna()
            except Exception as e:
                df_datos = None
                st.error(f"Error al conectar con Yahoo Finance: {str(e)}")

        if df_datos is not None and not df_datos.empty:
            num_velas = len(df_datos)
            st.info(f"📊 **Estructura del día {fecha_sel.strftime('%d/%m/%Y')}:** Se generaron **{num_velas} velas** en total ({tf_sel.split(' ')[0]} {tf_sel.split(' ')[1]}).")

            # Formato de tiempo para el Eje X
            if intervalo in ["15m", "60m"]:
                df_datos['Eje_X_Tiempo'] = df_datos.index.strftime('%H:%M')
            else:
                df_datos['Eje_X_Tiempo'] = df_datos.index.strftime('%d/%m')

            # Valores para trazar la estrategia
            apertura_ref = float(df_datos['Open'].iloc[-1])
            cierre_ref = float(df_datos['Close'].iloc[-1])
            maximo_ref = float(df_datos['High'].max())
            minimo_ref = float(df_datos['Low'].min())

            # Dibuja un solo gráfico interactivo
            fig = go.Figure()

            # 1. VELAS JAPONESAS
            fig.add_trace(go.Candlestick(
                x=df_datos['Eje_X_Tiempo'],
                open=df_datos['Open'], high=df_datos['High'],
                low=df_datos['Low'], close=df_datos['Close'],
                name="Velas",
                increasing_line_color='#00e676', increasing_fillcolor='#00e676',
                decreasing_line_color='#ff1744', decreasing_fillcolor='#ff1744',
                hovertext=[
                    f"<b>⏰ Hora: {row['Eje_X_Tiempo']}</b><br>"
                    f"🟢 Apertura: {row['Open']:.4f}<br>"
                    f"⬆️ Máximo: {row['High']:.4f}<br>"
                    f"⬇️ Mínimo: {row['Low']:.4f}<br>"
                    f"🔴 Cierre: {row['Close']:.4f}"
                    for _, row in df_datos.iterrows()
                ],
                hoverinfo="text"
            ))

            # 2. LÍNEAS DE ESTRATEGIA SOBRE LAS VELAS
            # Línea Azul: Entrada/Apertura actual
            fig.add_hline(
                y=apertura_ref, line_dash="solid", line_color="#29b6f6", line_width=1.5,
                annotation_text="🔵 Precio de Entrada", annotation_position="top left",
                annotation_font_color="#29b6f6"
            )
            # Línea Verde: Nivel de Ganancia (Resistencia / Techo del Día)
            fig.add_hline(
                y=maximo_ref, line_dash="dash", line_color="#00e676", line_width=1.5,
                annotation_text="🎯 Take Profit (Techo Máximo)", annotation_position="top left",
                annotation_font_color="#00e676"
            )
            # Línea Roja: Nivel de Riesgo (Soporte / Piso del Día)
            fig.add_hline(
                y=minimo_ref, line_dash="dash", line_color="#ff1744", line_width=1.5,
                annotation_text="🛑 Stop Loss (Piso Mínimo)", annotation_position="bottom left",
                annotation_font_color="#ff1744"
            )

            fig.update_layout(
                template="plotly_dark",
                paper_bgcolor="#0b0e14",
                plot_bgcolor="#0b0e14",
                height=450,
                showlegend=False,
                xaxis_rangeslider_visible=False,
                margin=dict(l=10, r=40, t=20, b=30),
                dragmode="pan",
                yaxis=dict(
                    title="💵 Precio de Cotización", 
                    side="right", 
                    gridcolor="#1a202c", 
                    fixedrange=False
                ),
                xaxis=dict(
                    title="⏰ Tiempo (Hora / Minuto)", 
                    gridcolor="#1a202c", 
                    type="category", 
                    nticks=6,
                    fixedrange=False
                )
            )

            st.plotly_chart(
                fig, 
                use_container_width=True, 
                config={
                    'scrollZoom': True, 
                    'displayModeBar': True,
                    'modeBarButtonsToRemove': ['select2d', 'lasso2d', 'resetScale2d']
                }
            )

            # ANÁLISIS DEL PROFESOR IA
            if st.button("💡 Analizar Estrategia con Profesor IA", type="primary", use_container_width=True, key="1.5_btn_analisis"):
                ultima_fecha = df_datos.index[-1].strftime('%d/%m/%Y a las %H:%M hrs')
                
                st.markdown("---")
                st.markdown(f"## 📖 Lección Didáctica: Estrategia de Soporte y Resistencia ({par_sel})")
                st.caption(f"Registro analizado: **{ultima_fecha}** | Temporalidad: **{tf_sel}**")

                st.markdown(f"""
                ### 1. Guía de Lectura de la Estrategia en el Gráfico
                Para aprender a operar este escenario sin confundirte, observa las **3 líneas horizontales** trazadas directamente sobre las velas:

                * **🔵 Línea Azul ({apertura_ref:.4f}):** Representa el **Punto de Entrada**. Es la cotización donde la estrategia evalúa la oportunidad de compra o venta.
                * **🎯 Línea Verde ({maximo_ref:.4f}):** Es la **Meta de Ganancia (Take Profit)**. Coincide con el precio más alto alcanzado en la jornada (Techo / Resistencia). Si el precio toca este nivel, aseguras tus beneficios.
                * **🛑 Línea Roja ({minimo_ref:.4f}):** Es el **Límite de Riesgo (Stop Loss)**. Coincide con el precio más bajo de la jornada (Piso / Soporte). Si el mercado se regresa y toca este piso, la posición se cierra para proteger tu capital.

                ### 2. Lección Didáctica de Temporalidad
                * **¿Por qué la temporalidad de {tf_sel.split(' ')[0]} {tf_sel.split(' ')[1]} es útil aquí?**
                  Al analizar en esta temporalidad, se observa cómo el mercado respeta los rebotes entre la **Línea Roja (Piso)** y la **Línea Verde (Techo)**. Esta estructura clara le permite al alumno definir su plan de trading con un riesgo perfectamente controlado.
                """)
        else:
            st.error("No se encontraron datos de mercado para la fecha seleccionada.")

# ==============================================================================
# PESTAÑAS 2 Y 3 (EN DESARROLLO)
# ==============================================================================
with tab2:
    st.info("🚧 Pestaña de Backtesting en construcción.")

with tab3:
    st.info("🚧 Pestaña de Evaluación IA en construcción.")
