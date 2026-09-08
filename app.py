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
        # 1.4 CONSTRUCCIÓN DEL LIENZO GRÁFICO (ZOOM HABILITADO)
        # ----------------------------------------------------------------------
        if df_datos is not None and not df_datos.empty:
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
                height=450,
                xaxis_rangeslider_visible=False,
                margin=dict(l=10, r=40, t=10, b=10),
                yaxis=dict(side="right", gridcolor="#1a202c", fixedrange=False),
                xaxis=dict(gridcolor="#1a202c", fixedrange=False), # Permite hacer Zoom horizontal
                hovermode="x"
            )

            # Permite hacer zoom táctil (Pinch-to-zoom)
            st.plotly_chart(
                fig, 
                use_container_width=True, 
                config={
                    'displayModeBar': False,
                    'scrollZoom': True
                }
            )

            # ------------------------------------------------------------------
            # 1.5 BOTÓN Y CAJA DE ANÁLISIS DEL PROFESOR IA (CLASE PRÁCTICA)
            # ------------------------------------------------------------------
            if st.button("💡 Analizar con Profesor IA", type="primary", use_container_width=True, key="1.5_btn_analisis"):
                
                # Extracción de datos de la última vela para la clase
                ultima_fecha = df_datos.index[-1].strftime('%d/%m/%Y %H:%M')
                cierre = float(df_datos['Close'].iloc[-1])
                apertura = float(df_datos['Open'].iloc[-1])
                maximo = float(df_datos['High'].iloc[-1])
                minimo = float(df_datos['Low'].iloc[-1])
                
                es_alcista = cierre >= apertura
                tipo_direccion = "ALCISTA 🟢 (Oportunidad de COMPRA)" if es_alcista else "BAJISTA 🔴 (Oportunidad de VENTA)"
                
                # Identificación simplificada del patrón de la vela
                cuerpo = abs(cierre - apertura)
                sombra_inferior = min(cierre, apertura) - minimo
                
                if sombra_inferior > (cuerpo * 2):
                    patron_vela = "Vela tipo **MARTILLO 🔨** (El precio cayó pero rebotó con mucha fuerza. Señal de cambio a subida)."
                elif es_alcista:
                    patron_vela = "Vela de **IMPULSO VERDE 🟢** (Los compradores tienen el control absoluto en esta hora)."
                else:
                    patron_vela = "Vela de **PRESIÓN ROJA 🔴** (Dominio de los vendedores empujando el precio hacia abajo)."

                analisis_html = f"""
                <div style="background-color: #f5f2eb; color: #1a1a1a; padding: 20px; border-radius: 8px; font-family: sans-serif; line-height: 1.6; border: 1px solid #dcd6cd;">
                    <h3 style="color: #000000; margin-top:0;">🗣️ Clase Didáctica del Profesor IA</h3>
                    <p style="margin-bottom: 5px;"><b>Par:</b> {par_sel} | <b>Intervalo:</b> {tf_sel}</p>
                    <hr style="border: 0.5px solid #ccc;">
                    
                    <p><b>1. 📍 Ubicación en el Gráfico (Eje X / Fecha y Hora):</b><br>
                    En la vela del día/hora <b>{ultima_fecha}</b>, la dirección principal del mercado es <b>{tipo_direccion}</b>.</p>
                    
                    <p><b>2. 🔍 ¿Qué tipo de vela tenemos aquí?:</b><br>
                    Analizando la figura de la vela: {patron_vela}</p>
                    
                    <p><b>3. 💡 Sugerencia de Indicadores para la Estrategia (RSI):</b><br>
                    • Si vas a configurar un indicador <b>RSI en periodo 14</b>:<br>
                    - Si el RSI está por debajo de <b>30</b>: Te confirma que el precio está demasiado barato (Sobrevendido). <i>¡Excelente momento para buscar COMPRAS!</i><br>
                    - Si el RSI está por encima de <b>70</b>: Te avisa que el precio está muy caro (Sobrecomprado). <i>¡Ideal para buscar VENTAS!</i></p>
                    
                    <p><b>4. 🎯 Plan de Acción Recomendado:</b><br>
                    • <b>Entrada sugerida:</b> Buscar posición { "Alcista (COMPRA)" if es_alcista else "Bajista (VENTA)" }.<br>
                    • <b>Tope de Pérdida (Stop Loss):</b> Colócalo en el nivel de <b>{minimo:.4f}</b> (debajo de la cola de la vela).<br>
                    • <b>Meta de Ganancia (Take Profit):</b> Apunta al objetivo en <b>{maximo:.4f}</b>.</p>
                </div>
                """
                st.markdown(analisis_html, unsafe_allow_html=True)
     
        

# ==============================================================================
# 2.0 PESTAÑA: BACKTESTING (PRÓXIMAMENTE)
# ==============================================================================
with tab2:
    st.info("2.0 — Pestaña en espera. Se activará tras validar la Pestaña 1.0.")


# ==============================================================================
# 3.0 PESTAÑA: EVALUACIÓN IA (PRÓXIMAMENTE)
# ==============================================================================
with tab3:
    st.info("3.0 — Pestaña en espera.")







