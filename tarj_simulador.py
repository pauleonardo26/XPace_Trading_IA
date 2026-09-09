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

    # Reglas lógicas de patrones
    es_doji = cuerpo <= (rango_total * 0.10)
    es_martillo = (mecha_inferior >= (cuerpo * 2)) & (mecha_superior <= (cuerpo * 0.5)) & (~es_doji)
    es_estrella_fugaz = (mecha_superior >= (cuerpo * 2)) & (mecha_inferior <= (cuerpo * 0.5)) & (~es_doji)
    es_marubozu = (cuerpo >= (rango_total * 0.85)) & (~es_doji)

    # Asignación de categorías
    df['Categoria'] = np.select(
        [es_doji, es_martillo, es_estrella_fugaz, es_marubozu],
        ['DOJI', 'MARTILLO', 'ESTRELLA_FUGAZ', 'MARUBOZU'],
        default=np.where(df['Close'] >= df['Open'], 'NORMAL_ALCISTA', 'NORMAL_BAJISTA')
    )
    
    return df

def construir_grafico_multicolor(df_procesado):
    """
    Crea las trazas de velas clasificadas por color para Plotly.
    """
    fig = go.Figure()
    
    CONFIG_COLORES = {
        'DOJI':            {'color': '#9C27B0', 'nombre': 'Doji (Indecisión)'},
        'MARTILLO':        {'color': '#00E676', 'nombre': 'Martillo (Rebote Alcista)'},
        'ESTRELLA_FUGAZ':  {'color': '#FF5252', 'nombre': 'Estrella Fugaz (Giro Bajista)'},
        'MARUBOZU':        {'color': '#29B6F6', 'nombre': 'Marubozu (Impulso Fuerte)'},
        'NORMAL_ALCISTA':  {'color': '#2E7D32', 'nombre': 'Alcista Normal'},
        'NORMAL_BAJISTA':  {'color': '#C62828', 'nombre': 'Bajista Normal'}
    }

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
            
    return fig

def render():
    st.write("### 🧪 Simulador de Toma de Decisiones a Ciegas")
    st.caption("Aplica tus herramientas de análisis técnico y patrones de velas para respaldar tu entrada.")

    col1, col2 = st.columns(2)
    with col1:
        par_bt = st.selectbox("Par a Simular", list(SIMBOLOS_FOREX.keys()), key="s_par")
    with col2:
        fecha_bt_defecto = date.today() - timedelta(days=10)
        fecha_bt = st.date_input("Fecha del Desafío", value=fecha_bt_defecto, max_value=date.today(), key="s_fecha", format="DD/MM/YYYY")

    if fecha_bt.weekday() >= 5:
        st.error("⚠️ Elige un día laborable (Lunes a Viernes).")
    else:
        ticker_bt = SIMBOLOS_FOREX[par_bt]
        with st.spinner("Preparando mercado a ciegas..."):
            try:
                df_bt = yf.download(tickers=ticker_bt, start=fecha_bt, end=fecha_bt + timedelta(days=1), interval="15m", progress=False)
                if isinstance(df_bt.columns, pd.MultiIndex):
                    df_bt.columns = df_bt.columns.get_level_values(0)
                df_bt = df_bt.dropna()
            except Exception:
                df_bt = None

        if df_bt is not None and len(df_bt) > 15:
            df_bt['Eje_X_Tiempo'] = df_bt.index.strftime('%H:%M')
            
            mitad = len(df_bt) // 2
            df_visible = df_bt.iloc[:mitad].copy()
            df_futuro = df_bt.iloc[mitad:].copy()

            # Cálculo de Indicadores
            df_visible['SMA20'] = df_visible['Close'].rolling(window=20, min_periods=1).mean()
            df_visible['STD20'] = df_visible['Close'].rolling(window=20, min_periods=1).std()
            df_visible['BB_Upper'] = df_visible['SMA20'] + (df_visible['STD20'] * 2)
            df_visible['BB_Lower'] = df_visible['SMA20'] - (df_visible['STD20'] * 2)

            delta = df_visible['Close'].diff()
            gain = delta.clip(lower=0)
            loss = -delta.clip(upper=0)
            avg_gain = gain.rolling(window=14, min_periods=1).mean()
            avg_loss = loss.rolling(window=14, min_periods=1).mean().replace(0, 0.00001)
            rs = avg_gain / avg_loss
            df_visible['RSI'] = 100 - (100 / (1 + rs))

            st.markdown("---")
            st.write("### 🛠️ Herramientas Técnicas")
            c1, c2, c3 = st.columns(3)
            with c1:
                ver_bollinger = st.checkbox("Bandas de Bollinger", value=False, key="chk_bb")
            with c2:
                ver_rsi = st.checkbox("Oscilador RSI (14)", value=False, key="chk_rsi")
            with c3:
                ver_niveles = st.checkbox("Soporte y Resistencia", value=False, key="chk_sr")

            # Procesar datos visibles con patrón cromático
            df_visible_proc = procesar_velas_pedagogicas(df_visible)
            fig_bt = construir_grafico_multicolor(df_visible_proc)

            if ver_bollinger:
                fig_bt.add_trace(go.Scatter(x=df_visible['Eje_X_Tiempo'], y=df_visible['BB_Upper'], line=dict(color='#ff9800', width=1, dash='dot'), name='Techo BB'))
                fig_bt.add_trace(go.Scatter(x=df_visible['Eje_X_Tiempo'], y=df_visible['SMA20'], line=dict(color='#2196f3', width=1), name='Media SMA20'))
                fig_bt.add_trace(go.Scatter(x=df_visible['Eje_X_Tiempo'], y=df_visible['BB_Lower'], line=dict(color='#ff9800', width=1, dash='dot'), name='Piso BB'))

            if ver_niveles:
                fig_bt.add_hline(y=float(df_visible['High'].max()), line_dash="dash", line_color="#ff1744", annotation_text="Techo")
                fig_bt.add_hline(y=float(df_visible['Low'].min()), line_dash="dash", line_color="#00e676", annotation_text="Piso")

            fig_bt.update_layout(
                template="plotly_dark", 
                height=420, 
                paper_bgcolor="#0b0e14", 
                plot_bgcolor="#0b0e14", 
                xaxis_rangeslider_visible=False,
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            st.plotly_chart(fig_bt, use_container_width=True)

            if ver_rsi:
                fig_rsi = go.Figure()
                fig_rsi.add_trace(go.Scatter(x=df_visible['Eje_X_Tiempo'], y=df_visible['RSI'], line=dict(color='#e040fb', width=2)))
                fig_rsi.add_hline(y=70, line_dash="dash", line_color="#ff1744")
                fig_rsi.add_hline(y=30, line_dash="dash", line_color="#00e676")
                fig_rsi.update_layout(template="plotly_dark", height=180, paper_bgcolor="#0b0e14", plot_bgcolor="#0b0e14")
                st.plotly_chart(fig_rsi, use_container_width=True)

            st.markdown("---")
            st.write("### 🎮 Toma de Decisión")
            op1, op2, op3 = st.columns(3)
            with op1:
                operacion = st.radio("Operación", ["🟢 COMPRAR", "🔴 VENDER"], key="sim_op")
            with op2:
                usar_sl = st.radio("Stop Loss", ["✅ SÍ", "❌ NO"], key="sim_sl")
            
            tiene_proteccion = "✅ SÍ" in usar_sl
            with op3:
                riesgo = st.slider("% Riesgo", 1, 10, 2, disabled=not tiene_proteccion, key="sim_risk")

            if st.button("🚀 Revelar Futuro y Ejecutar", type="primary", use_container_width=True):
                precio_entrada = float(df_visible['Close'].iloc[-1])
                precio_final = float(df_futuro['Close'].iloc[-1])
                hora_corte = df_visible['Eje_X_Tiempo'].iloc[-1]

                # Procesar mercado completo con patrón cromático para la revelación
                df_bt_proc = procesar_velas_pedagogicas(df_bt)
                fig_rev = construir_grafico_multicolor(df_bt_proc)
                
                fig_rev.add_shape(type="line", x0=hora_corte, x1=hora_corte, y0=0, y1=1, yref="paper", line=dict(color="#e040fb", width=2, dash="dash"))
                fig_rev.update_layout(
                    template="plotly_dark", 
                    height=420, 
                    paper_bgcolor="#0b0e14", 
                    plot_bgcolor="#0b0e14", 
                    xaxis_rangeslider_visible=False,
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
                )
                st.plotly_chart(fig_rev, use_container_width=True)

                es_compra = "COMPRAR" in operacion
                gane = (es_compra and precio_final > precio_entrada) or (not es_compra and precio_final < precio_entrada)

                if gane:
                    st.success(f"🎉 ¡Operación Exitosa! Entraste en `{precio_entrada:.4f}` y cerró en `{precio_final:.4f}`.")
                else:
                    if not tiene_proteccion:
                        st.error("🚨 Pérdida ilimitada por no usar Stop Loss. Cuenta en riesgo grave.")
                    else:
                        st.warning(f"📉 Pérdida controlada. Solo perdiste el `{riesgo}%` asignado.")
        else:
            st.error("No hay suficientes datos para simular en esta fecha.")
