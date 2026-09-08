import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import yfinance as yf
from datetime import date, timedelta

SIMBOLOS_FOREX = {
    "EUR/USD (Euro / Dólar)": "EURUSD=X",
    "USD/JPY (Dólar / Yen)": "JPY=X",
    "GBP/USD (Libra / Dólar)": "GBPUSD=X",
    "EUR/JPY (Euro / Yen)": "EURJPY=X"
}

TEMPORALIDADES_YAHOO = {
    "15 Minutos": "15m",
    "1 Hora": "60m"
}

def render():
    st.write("### 📌 Consulta Histórica de Mercado")
    col1, col2 = st.columns(2)
    with col1:
        par_sel = st.selectbox("Par de Forex", list(SIMBOLOS_FOREX.keys()), key="m_par")
        tf_sel = st.selectbox("Temporalidad", list(TEMPORALIDADES_YAHOO.keys()), key="m_tf")
    with col2:
        fecha_defecto = date.today() - timedelta(days=7)
        fecha_sel = st.date_input("Fecha a Consultar", value=fecha_defecto, max_value=date.today(), key="m_fecha", format="DD/MM/YYYY")

    if fecha_sel.weekday() >= 5:
        st.error("⚠️ Los fines de semana Forex no opera. Elige un día de Lunes a Viernes.")
    else:
        ticker = SIMBOLOS_FOREX[par_sel]
        intervalo = TEMPORALIDADES_YAHOO[tf_sel]
        
        with st.spinner("Cargando datos históricos..."):
            try:
                df_datos = yf.download(tickers=ticker, start=fecha_sel, end=fecha_sel + timedelta(days=1), interval=intervalo, progress=False)
                if isinstance(df_datos.columns, pd.MultiIndex):
                    df_datos.columns = df_datos.columns.get_level_values(0)
                df_datos = df_datos.dropna()
            except Exception:
                df_datos = None

        if df_datos is not None and not df_datos.empty:
            df_datos['Eje_X_Tiempo'] = df_datos.index.strftime('%H:%M')
            fig = go.Figure(data=[go.Candlestick(
                x=df_datos['Eje_X_Tiempo'], open=df_datos['Open'], high=df_datos['High'],
                low=df_datos['Low'], close=df_datos['Close'],
                increasing_line_color='#00e676', decreasing_line_color='#ff1744'
            )])
            fig.update_layout(template="plotly_dark", height=420, paper_bgcolor="#0b0e14", plot_bgcolor="#0b0e14", xaxis_rangeslider_visible=False)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No hay datos disponibles para la fecha seleccionada.")

