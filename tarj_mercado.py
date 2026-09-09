import streamlit as st
import pandas as pd
import numpy as np
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

def procesar_velas_pedagogicas(df):
    """
    Clasifica las velas según patrones técnicos clave y les asigna una categoría cromática.
    """
    df = df.copy()
    
    cuerpo = (df['Close'] - df['Open']).abs()
    rango_total = df['High'] - df['Low']
    rango_total = rango_total.replace(0, 0.00001)

    mecha_superior = df['High'] - df[['Open', 'Close']].max(axis=1)
    mecha_inferior = df[['Open', 'Close']].min(axis=1) - df['Low']

    # Reglas lógicas de identificación
    es_doji = cuerpo <= (rango_total * 0.10)
    es_martillo = (mecha_inferior >= (cuerpo * 2)) & (mecha_superior <= (cuerpo * 0.5)) & (~es_doji)
    es_estrella_fugaz = (mecha_superior >= (cuerpo * 2)) & (mecha_inferior <= (cuerpo * 0.5)) & (~es_doji)
    es_marubozu = (cuerpo >= (rango_total * 0.85)) & (~es_doji)

    # Asignación de categoría
    df['Categoria'] = np.select(
        [es_doji, es_martillo, es_estrella_fugaz, es_marubozu],
        ['DOJI', 'MARTILLO', 'ESTRELLA_FUGAZ', 'MARUBOZU'],
        default=np.where(df['Close'] >= df['Open'], 'NORMAL_ALCISTA', 'NORMAL_BAJISTA')
    )
    
    return df

def render():
    st.write("### 📌 Consulta Histórica de Mercado (Análisis Cromático)")
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
        
        with st.spinner("Cargando datos e identificando patrones de velas..."):
            try:
                df_datos = yf.download(tickers=ticker, start=fecha_sel, end=fecha_sel + timedelta(days=1), interval=intervalo, progress=False)
                if isinstance(df_datos.columns, pd.MultiIndex):
                    df_datos.columns = df_datos.columns.get_level_values(0)
                df_datos = df_datos.dropna()
            except Exception:
                df_datos = None

        if df_datos is not None and not df_datos.empty:
            df_datos['Eje_X_Tiempo'] = df_datos.index.strftime('%H:%M')
            df_procesado = procesar_velas_pedagogicas(df_datos)
            
            fig = go.Figure()

            # Configuración del mapa de colores
            CONFIG_COLORES = {
                'DOJI':            {'color': '#9C27B0', 'nombre': 'Doji (Indecisión)'},
                'MARTILLO':        {'color': '#00E676', 'nombre': 'Martillo (Rebote Alcista)'},
                'ESTRELLA_FUGAZ':  {'color': '#FF5252', 'nombre': 'Estrella Fugaz (Giro Bajista)'},
                'MARUBOZU':        {'color': '#29B6F6', 'nombre': 'Marubozu (Impulso Fuerte)'},
                'NORMAL_ALCISTA':  {'color': '#2E7D32', 'nombre': 'Alcista Normal'},
                'NORMAL_BAJISTA':  {'color': '#C62828', 'nombre': 'Bajista Normal'}
            }

            # Dibujar trazo por cada grupo de categoría
            for cat, cfg in CONFIG_COLORES.items():
                sub_df = df_procesado[df_procesado['Categoria'] == cat]
                if not sub_df.empty:
                    fig.add_trace(go.Candlestick(
                        x=sub_df['Eje_X_Tiempo'],
                        open=sub_df['Open'],
                        high=sub_df['High'],
                        low=sub_df['Low'],
                        close=sub_df['Close'],
                        name=cfg['nombre'],
                        increasing_line_color=cfg['color'],
                        decreasing_line_color=cfg['color'],
                        increasing_fillcolor=cfg['color'],
                        decreasing_fillcolor=cfg['color']
                    ))

            fig.update_layout(
                template="plotly_dark",
                height=480,
                paper_bgcolor="#0b0e14",
                plot_bgcolor="#0b0e14",
                xaxis_rangeslider_visible=False,
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            st.info("💡 **Leyenda de colores pedagógicos:** Las velas especiales se resaltarán automáticamente con tonos neón/brillantes, mientras que las velas comunes permanecerán en tonos opacos.")
        else:
            st.warning("No hay datos disponibles para la fecha seleccionada.")


