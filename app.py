# ==============================================================================
# 0.0 CONFIGURACIÓN GENERAL E IMPORTACIÓN DE LIBRERÍAS
# ==============================================================================
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, date, timedelta
import yfinance as yf

# ------------------------------------------------------------------------------
# 0.1 CONFIGURACIÓN DE PÁGINA Y ESTILOS
# ------------------------------------------------------------------------------
st.set_page_config(page_title="XPace — Escuela de Trading", layout="wide", page_icon="🎓")

st.markdown("""
    <style>
    .stApp { background-color: #0b0e14 !important; color: #e6edf3 !important; }
    .block-container { padding-top: 1rem !important; max-width: 100% !important; }
    
    /* Cajas de selección táctiles */
    .stSelectbox > div > div {
        background-color: #1a2230 !important;
        color: #ffffff !important;
        border-radius: 6px !important;
    }
    </style>
""", unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# 0.2 DICCIONARIOS Y CONSTANTES DE YAHOO FINANCE
# ------------------------------------------------------------------------------
SIMBOLOS_FOREX = {
    "EUR/USD (Euro / Dólar)": "EURUSD=X",
    "USD/JPY (Dólar / Yen)": "JPY=X",
    "GBP/USD (Libra / Dólar)": "GBPUSD=X",
    "EUR/JPY (Euro / Yen)": "EURJPY=X"
}

TEMPORALIDADES_YAHOO = {
    "15 Minutos (Últimos 60 días)": "15m",
    "1 Hora (Últimos 60 días)": "60m",
    "1 Día (Histórico Completo)": "1d",
    "1 Semana (Histórico Completo)": "1wk",
    "1 Mes (Histórico Completo)": "1mo"
}

# ------------------------------------------------------------------------------
# 0.3 ENCABEZADO PRINCIPAL DE LA APLICACIÓN
# ------------------------------------------------------------------------------
st.title("🎓 XPace — Escuela de Trading")
st.caption("Datos reales directo de Yahoo Finance con explicaciones pedagógicas de IA")

# ------------------------------------------------------------------------------
# 0.4 CREACIÓN DE PESTAÑAS
# ------------------------------------------------------------------------------
tab1, tab2, tab3 = st.tabs(["📈 Histórico Educativo", "🧪 Backtesting (Próximamente)", "🤖 Evaluación IA (Próximamente)"])


# ==============================================================================
# 1.0 PESTAÑA: HISTÓRICO EDUCATIVO
# ==============================================================================
with tab1:
    
    # --------------------------------------------------------------------------
    # 1.1 PANEL DE FILTROS DE MERCADO
    # --------------------------------------------------------------------------
    st.write("### 📌 Filtros de Mercado")
    
    par_sel = st.selectbox("Par de Forex", list(SIMBOLOS_FOREX.keys()), key="1.1_par")
    tf_sel = st.selectbox("Temporalidades Nativas de Yahoo", list(TEMPORALIDADES_YAHOO.keys()), key="1.1_tf")
    
    fecha_defecto = date.today() - timedelta(days=7)
    fecha_sel = st.date_input("Fecha a Consultar", value=fecha_defecto, max_value=date.today(), key="1.1_fecha")

    # --------------------------------------------------------------------------
    # 1.2 CONTROL DE DÍAS FESTIVOS / FIN DE SEMANA
    # --------------------------------------------------------------------------
    if fecha_sel.weekday() >= 5:
        st.error("⚠️ Los sábados y domingos el mercado Forex no genera datos. Elige un día de lunes a viernes.")
    else:
        
        # ----------------------------------------------------------------------
        # 1.3 DESCARGA DE DATOS DESDE YAHOO FINANCE
        # ----------------------------------------------------------------------
        ticker = SIMBOLOS_FOREX[par_sel]
        intervalo = TEMPORALIDADES_YAHOO[tf_sel]
        
        if intervalo in ["15m", "60m"]:
            hace_50_dias = date.today() - timedelta(days=50)
            if fecha_sel < hace_50_dias:
                fecha_sel = hace_50_dias
                st.warning("⚠️ Yahoo Finance solo provee datos de 15m y 1h para los últimos 50 días. Mostrando el límite máximo permitido.")
            start_dt = fecha_sel
            end_dt = fecha_sel + timedelta(days=5)
        else:
            start_dt = fecha_sel - timedelta(days=180)
            end_dt = fecha_sel + timedelta(days=5)

        with st.spinner("Conectando con Yahoo Finance..."):
            try:
                df_datos = yf.download(tickers=ticker, start=start_dt, end=end_dt, interval=intervalo, progress=False)
                if isinstance(df_datos.columns, pd.MultiIndex):
                    df_datos.columns = df_datos.columns.get_level_values(0)
                df_datos = df_datos.dropna()
            except Exception as e:
                df_datos = None
                st.error(f"Error directo de conexión con Yahoo: {str(e)}")
        

        # ----------------------------------------------------------------------
        # 1.4 CONSTRUCCIÓN DEL LIENZO GRÁFICO (ESTABLE CON EJE X DE DÍA Y HORA)
        # ----------------------------------------------------------------------
        if df_datos is not None and not df_datos.empty:
            
            # Filtrar exactamente el rango de datos para evitar amontonamiento
            fig = go.Figure()
            fig.add_trace(go.Candlestick(
                x=df_datos.index,
                open=df_datos['Open'],
                high=df_datos['High'],
                low=df_datos['Low'],
                close=df_datos['Close'],
                increasing_line_color='#00e676', increasing_fillcolor='#00e676',
                decreasing_line_color='#ff1744', decreasing_fillcolor='#ff1744'
            ))

            fig.update_layout(
                template="plotly_dark",
                paper_bgcolor="#0b0e14",
                plot_bgcolor="#0b0e14",
                height=420,
                xaxis_rangeslider_visible=False,
                margin=dict(l=10, r=40, t=10, b=10),
                # Eje Y estable para evitar saltos de cámara
                yaxis=dict(side="right", gridcolor="#1a202c", fixedrange=True),
                # Eje X configurado con formato claro de Hora y Día
                xaxis=dict(
                    gridcolor="#1a202c", 
                    tickformat="%d/%m %H:%M",
                    type="category" # Mantiene el espacio uniforme entre velas sin huecos
                ),
                hovermode="x unified"
            )

            # Desactivar gestos bruscos para controlar la pantalla táctil
            st.plotly_chart(
                fig, 
                use_container_width=True, 
                config={'displayModeBar': False}
            )

            # ------------------------------------------------------------------
            # 1.5 ANÁLISIS DETALLADO DEL PROFESOR IA (LECTURA FLUIDA)
            # ------------------------------------------------------------------
            if st.button("💡 Analizar con Profesor IA", type="primary", use_container_width=True, key="1.5_btn_analisis"):
                
                # Datos de la vela para el análisis
                ultima_fecha = df_datos.index[-1].strftime('%d/%m/%Y a las %H:%M hrs')
                cierre = float(df_datos['Close'].iloc[-1])
                apertura = float(df_datos['Open'].iloc[-1])
                maximo = float(df_datos['High'].iloc[-1])
                minimo = float(df_datos['Low'].iloc[-1])
                
                es_alcista = cierre >= apertura
                cuerpo = abs(cierre - apertura)
                sombra_inf = min(cierre, apertura) - minimo
                sombra_sup = maximo - max(cierre, apertura)

                st.markdown("---")
                st.markdown(f"## 📖 Lección Didáctica: Análisis del {par_sel}")
                st.caption(f"Registro analizado: **{ultima_fecha}** | Temporalidad: **{tf_sel}**")

                st.markdown(f"""
                ### 1. ¿Qué está sucediendo exactamente en esta hora o día?
                Si observamos el eje X en la parte inferior del gráfico, nos ubicamos en la vela correspondiente al **{ultima_fecha}**. En esta fracción de tiempo, el precio abrió en **{apertura:.4f}** y tuvo su cierre en **{cierre:.4f}**. 
                
                Dado que el precio de cierre fue {"superior" if es_alcista else "inferior"} al de apertura, la vela se pinta de color **{"VERDE 🟢" if es_alcista else "ROJO 🔴"}**. Esto nos indica que durante este periodo el mercado estuvo bajo el dominio principal de los **{"compradores empujando el precio hacia arriba" if es_alcista else "vendedores presionando la cotización a la baja"}**.

                ### 2. Anatomía de la Vela y lectura de fuerza
                Mirando en detalle los extremos superior e inferior de esta vela:
                * **El Techo (Máximo alcanzado):** Llegó hasta **{maximo:.4f}**. La pequeña mecha superior nos muestra el punto más alto donde los compradores intentaron llevar el precio antes de encontrar resistencia.
                * **El Piso (Mínimo alcanzado):** Cayó hasta **{minimo:.4f}**. 
                
                {"**Observación pedagógica:** Hay una cola o mecha inferior pronunciada. Esto significa que los vendedores intentaron tumbar el mercado, pero entraron compradores con fuerza a defender el precio en la zona baja. Este patrón se conoce como **Martillo** y suele anunciar rebotes a la subida." if sombra_inf > (cuerpo * 1.5) else "La estructura muestra un cuerpo sólido, lo que confirma que la tendencia de esta hora tiene continuidad y fuerza clara."}

                ### 3. Recomendación de Indicadores para aprender a operar (RSI)
                Para saber si es un buen momento de entrar y no comprar cuando el precio está en su punto más caro, podemos usar el indicador **RSI (Índice de Fuerza Relativa)** en periodo 14:
                * **Si el RSI marca menos de 30:** El precio se considera **"Sobrevendido"** (está regalado/barato). Es la zona idónea donde los profesionales buscan oportunidades de **COMPRA 🟢**.
                * **Si el RSI marca más de 70:** El precio se encuentra **"Sobrecomprado"** (demasiado inflado). Es la zona de peligro para comprar y la ideal para buscar **VENTAS 🔴**.

                ### 4. Estrategia Pedagógica y Plan de Riesgo
                Como alumnos de trading, nunca debemos entrar al mercado sin una protección en caso de que la vela cambie de rumbo:
                * **Dirección sugerida según el análisis:** **{"COMPRAR 🟢" if es_alcista else "VENDER 🔴"}**.
                * **Límite de Seguridad (Stop Loss):** Se debe colocar justo en **{minimo:.4f}**. Si el precio rompe este piso hacia abajo, el sistema cierra automáticamente tu posición para evitar pérdidas mayores.
                * **Meta de Ganancia (Take Profit):** Lo fijamos cerca de la resistencia en **{maximo:.4f}**, asegurando los beneficios en cuanto el precio alcance la cima de la vela.
                """)

        

# ==============================================================================
# 2.0 PESTAÑA: BACKTESTING (PRÓXIMAMENTE)
# ==============================================================================
#with tab2:
    st.info("2.0 — Pestaña en espera. Se activará tras validar la Pesta
# ==============================================================================
# 3.0 PESTAÑA: EVALUACIÓN IA (PRÓXIMAMENTE)
# ==============================================================================
with tab3:
    st.info("3.0 — Pestaña en espera.")







