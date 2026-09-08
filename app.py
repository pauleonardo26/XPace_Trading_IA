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
# PESTAÑA 2: BACKTESTING INTERACTIVO CON ESTRATEGIAS Y ANÁLISIS TÉCNICO
# ==============================================================================
with tab2:
    st.write("### 🧪 Simulador de Toma de Decisiones y Estrategias Técnicas")
    st.caption("Aplica tus herramientas de análisis (RSI, Bollinger, Soporte/Resistencia) sobre el gráfico a ciegas para respaldar tu estrategia.")

    col1, col2 = st.columns(2)
    with col1:
        par_bt = st.selectbox("Par a Simular", list(SIMBOLOS_FOREX.keys()), key="2_par")
    with col2:
        fecha_bt_defecto = date.today() - timedelta(days=10)
        fecha_bt = st.date_input("Fecha del Desafío", value=fecha_bt_defecto, max_value=date.today(), key="2_fecha", format="DD/MM/YYYY")

    if fecha_bt.weekday() >= 5:
        st.error("⚠️ Elige un día laborable (Lunes a Viernes).")
    else:
        ticker_bt = SIMBOLOS_FOREX[par_bt]
        with st.spinner("Cargando mercado y generando datos técnicos..."):
            try:
                df_bt = yf.download(tickers=ticker_bt, start=fecha_bt, end=fecha_bt + timedelta(days=1), interval="15m", progress=False)
                if isinstance(df_bt.columns, pd.MultiIndex):
                    df_bt.columns = df_bt.columns.get_level_values(0)
                df_bt = df_bt.dropna()
            except Exception:
                df_bt = None

        if df_bt is not None and len(df_bt) > 15:
            df_bt['Eje_X_Tiempo'] = df_bt.index.strftime('%H:%M')
            
            # CORTAR EL MERCADO A LA MITAD DEL DÍA
            mitad = len(df_bt) // 2
            df_visible = df_bt.iloc[:mitad].copy()
            df_futuro = df_bt.iloc[mitad:].copy()

            # ------------------------------------------------------------------
            # CÁLCULO DE INDICADORES TÉCNICOS SOBRE LOS DATOS VISIBLES
            # ------------------------------------------------------------------
            # 1. Bandas de Bollinger (Periodo 20, 2 Desviaciones Estándar)
            df_visible['SMA20'] = df_visible['Close'].rolling(window=20, min_periods=1).mean()
            df_visible['STD20'] = df_visible['Close'].rolling(window=20, min_periods=1).std()
            df_visible['BB_Upper'] = df_visible['SMA20'] + (df_visible['STD20'] * 2)
            df_visible['BB_Lower'] = df_visible['SMA20'] - (df_visible['STD20'] * 2)

            # 2. RSI (Relative Strength Index - 14 periodos)
            delta = df_visible['Close'].diff()
            gain = delta.clip(lower=0)
            loss = -delta.clip(upper=0)
            avg_gain = gain.rolling(window=14, min_periods=1).mean()
            avg_loss = loss.rolling(window=14, min_periods=1).mean().replace(0, 0.00001)
            rs = avg_gain / avg_loss
            df_visible['RSI'] = 100 - (100 / (1 + rs))

            # ------------------------------------------------------------------
            # HERRAMIENTAS Y ESTRATEGIAS EN EL PANEL DEL ALUMNO
            # ------------------------------------------------------------------
            st.markdown("---")
            st.write("### 🛠️ Herramientas de Análisis Técnico (Tu Estrategia)")
            
            col_ind1, col_ind2, col_ind3 = st.columns(3)
            with col_ind1:
                ver_bollinger = st.checkbox("🟢/🔴 Bandas de Bollinger", value=False, help="Muestra el techo y piso estocástico del precio.")
            with col_ind2:
                ver_rsi = st.checkbox("📊 Oscilador RSI (14)", value=False, help="Muestra zonas de Sobrecompra (>70) y Sobrevenda (<30).")
            with col_ind3:
                ver_niveles = st.checkbox("📐 Soporte y Resistencia", value=False, help="Dibuja automáticamente el máximo y mínimo visible como referencia.")

            # DIBUJAR GRÁFICO VISIBLE SEGÚN SELECCIÓN DE HERRAMIENTAS
            fig_bt = go.Figure()

            # Velas Japonesas
            fig_bt.add_trace(go.Candlestick(
                x=df_visible['Eje_X_Tiempo'], open=df_visible['Open'], high=df_visible['High'],
                low=df_visible['Low'], close=df_visible['Close'], name="Velas Visibles",
                increasing_line_color='#00e676', decreasing_line_color='#ff1744'
            ))

            # Capa: Bandas de Bollinger
            if ver_bollinger:
                fig_bt.add_trace(go.Scatter(x=df_visible['Eje_X_Tiempo'], y=df_visible['BB_Upper'], line=dict(color='#ff9800', width=1, dash='dot'), name='Banda Sup (Techo)'))
                fig_bt.add_trace(go.Scatter(x=df_visible['Eje_X_Tiempo'], y=df_visible['SMA20'], line=dict(color='#2196f3', width=1), name='Media Central (SMA 20)'))
                fig_bt.add_trace(go.Scatter(x=df_visible['Eje_X_Tiempo'], y=df_visible['BB_Lower'], line=dict(color='#ff9800', width=1, dash='dot'), name='Banda Inf (Piso)'))

            # Capa: Soporte y Resistencia
            if ver_niveles:
                max_v = float(df_visible['High'].max())
                min_v = float(df_visible['Low'].min())
                fig_bt.add_hline(y=max_v, line_dash="dash", line_color="#ff1744", annotation_text="Techo (Resistencia)", annotation_position="top left")
                fig_bt.add_hline(y=min_v, line_dash="dash", line_color="#00e676", annotation_text="Piso (Soporte)", annotation_position="bottom left")

            fig_bt.update_layout(
                template="plotly_dark", paper_bgcolor="#0b0e14", plot_bgcolor="#0b0e14",
                height=380, showlegend=ver_bollinger, xaxis_rangeslider_visible=False,
                margin=dict(l=10, r=40, t=10, b=20),
                yaxis=dict(title="💵 Precio", side="right", gridcolor="#1a202c"),
                xaxis=dict(title="⏰ Tiempo Revelado Parcial", gridcolor="#1a202c", type="category")
            )
            st.plotly_chart(fig_bt, use_container_width=True)

            # Capa: Sub-Gráfico RSI
            if ver_rsi:
                fig_rsi = go.Figure()
                fig_rsi.add_trace(go.Scatter(x=df_visible['Eje_X_Tiempo'], y=df_visible['RSI'], line=dict(color='#e040fb', width=2), name="RSI"))
                fig_rsi.add_hline(y=70, line_dash="dash", line_color="#ff1744", annotation_text="Sobrecompra (70)", annotation_position="top left")
                fig_rsi.add_hline(y=30, line_dash="dash", line_color="#00e676", annotation_text="Sobrevenda (30)", annotation_position="bottom left")
                fig_rsi.update_layout(
                    template="plotly_dark", paper_bgcolor="#0b0e14", plot_bgcolor="#0b0e14",
                    height=180, showlegend=False, margin=dict(l=10, r=40, t=10, b=20),
                    yaxis=dict(title="RSI", side="right", range=[0, 100], gridcolor="#1a202c"),
                    xaxis=dict(gridcolor="#1a202c", type="category")
                )
                st.plotly_chart(fig_rsi, use_container_width=True)

            # FORMULARIO DE DECISIÓN DEL ALUMNO
            st.markdown("---")
            st.write("### 🎮 Panel de Control del Alumno")
            
            c1, c2, c3 = st.columns(3)
            with c1:
                operacion = st.radio("1. ¿Qué decisión tomas?", ["🟢 COMPRAR", "🔴 VENDER"], key="bt_op")
            with c2:
                usar_sl = st.radio("2. ¿Colocas Stop Loss (Protección)?", ["✅ SÍ (Usar Límite de Riesgo)", "❌ NO (Sin Límite)"], key="bt_sl")
            
            # CONTROL DINÁMICO DEL SLIDER SEGÚN LA SELECCIÓN
            tiene_proteccion = "✅ SÍ" in usar_sl
            
            with c3:
                riesgo_porcentaje = st.slider(
                    "3. % de Cuenta a Arriesgar", 
                    min_value=1, 
                    max_value=10, 
                    value=2, 
                    disabled=not tiene_proteccion, # Desactivado en gris si marca "NO"
                    key="bt_risk"
                )
                if not tiene_proteccion:
                    st.caption("⚠️ **Riesgo Ilimitado:** Desactivado por no usar Stop Loss.")

            btn_simular = st.button("🚀 Revelar Futuro y Ejecutar Simulación", type="primary", use_container_width=True)

            if btn_simular:
                st.markdown("---")
                st.write("### 📜 Resultado de la Simulación")

                # CÁLCULOS DEL MERCADO REVELADO
                precio_entrada = float(df_visible['Close'].iloc[-1])
                precio_final = float(df_futuro['Close'].iloc[-1])
                hora_corte = df_visible['Eje_X_Tiempo'].iloc[-1]

                # DIBUJAR MERCADO COMPLETO REVELADO
                fig_revelado = go.Figure()
                fig_revelado.add_trace(go.Candlestick(
                    x=df_bt['Eje_X_Tiempo'], open=df_bt['Open'], high=df_bt['High'],
                    low=df_bt['Low'], close=df_bt['Close'], name="Velas Completas",
                    increasing_line_color='#00e676', decreasing_line_color='#ff1744'
                ))
                
                fig_revelado.add_shape(
                    type="line", x0=hora_corte, x1=hora_corte, y0=0, y1=1, yref="paper",
                    line=dict(color="#e040fb", width=2, dash="dash")
                )
                
                fig_revelado.add_annotation(
                    x=hora_corte, y=precio_entrada, text="📍 Tu Decisión",
                    showarrow=True, arrowhead=2, arrowcolor="#e040fb",
                    font=dict(color="#e040fb", size=12), bgcolor="#0b0e14"
                )
                
                fig_revelado.update_layout(
                    template="plotly_dark", paper_bgcolor="#0b0e14", plot_bgcolor="#0b0e14",
                    height=400, showlegend=False, xaxis_rangeslider_visible=False,
                    margin=dict(l=10, r=40, t=10, b=20),
                    yaxis=dict(title="💵 Precio", side="right", gridcolor="#1a202c"),
                    xaxis=dict(title="⏰ Día Completo Revelado", gridcolor="#1a202c", type="category")
                )
                st.plotly_chart(fig_revelado, use_container_width=True)

                # EVALUACIÓN EXACTA Y PEDAGÓGICA DE LA DECISIÓN
                es_compra = "COMPRAR" in operacion
                gane_operacion = (es_compra and precio_final > precio_entrada) or (not es_compra and precio_final < precio_entrada)

                # DIAGNÓSTICO ESTRATÉGICO DE LA ESTRATEGIA UTILIZADA
                rsi_val = df_visible['RSI'].iloc[-1]
                estrategia_retroalimentacion = ""
                if rsi_val > 68:
                    estrategia_retroalimentacion = f" (Nota: El RSI marcaba `{rsi_val:.1f}`, indicando Zona de Sobrecompra ideal para Ventas)."
                elif rsi_val < 32:
                    estrategia_retroalimentacion = f" (Nota: El RSI marcaba `{rsi_val:.1f}`, indicando Zona de Sobrevenda ideal para Compras)."

                if gane_operacion:
                    st.success(f"""
                    ### 🎉 ¡EXCELENTE LECTURA DE MERCADO!
                    * **Decisión Correcta:** Acertaste la dirección ({operacion}).
                    * **Precio Entrada:** `{precio_entrada:.4f}` ➔ **Cierre Día:** `{precio_final:.4f}`
                    * **Confirmación Estratégica:**{estrategia_retroalimentacion}
                    * **Gestión de Riesgo:** {"Protegiste tu cuenta correctamente con el " + str(riesgo_porcentaje) + "% de Stop Loss." if tiene_proteccion else "⚠️ Ganaste esta vez, pero operar **sin Stop Loss** es extremadamente peligroso para tu capital."}
                    """)
                else:
                    if not tiene_proteccion:
                        # SIN STOP LOSS Y PERDIÓ (LECCIÓN IMPACTANTE)
                        st.error(f"""
                        ### 🚨 ¡ALERTA DE SEGURIDAD: CUENTA EN RIESGO GRAVE!
                        * **Resultado:** Elegiste **{operacion}**, pero el mercado se movió en tu contra.
                        * **Peligro Detectado:** Marcaste **❌ NO (Sin Límite)**. 
                        * **Tiempo & Impacto:** En solo **2 a 3 velas (30-45 min)** el precio se fue en tu contra. Al no tener Stop Loss, la posición siguió acumulando pérdidas ilimitadas hasta comprometer seriamente tu capital.
                        * **Lección de Trading:** Un trader profesional **siempre** define su límite de pérdida antes de entrar al mercado.
                        """)
                    else:
                        # CON STOP LOSS Y PERDIÓ (PÉRDIDA CONTROLADA)
                        st.warning(f"""
                        ### 📉 OPERACIÓN CON PÉRDIDA CONTROLADA
                        * **Resultado:** Elegiste **{operacion}**, pero el mercado se movió en dirección opuesta.
                        * **Lo bueno de tu gestión:** Como activaste tu **Stop Loss**, la operación se cerró automáticamente protegiendo tu cuenta.
                        * **Riesgo Respetado:** Solo perdiste el **{riesgo_porcentaje}%** programado y mantienes el 98% de tu capital intacto.
                        """)
        else:
            st.error("No hay suficientes datos para simular en esta fecha.")

# ==============================================================================
# PESTAÑA 3 (EN DESARROLLO)
# ==============================================================================
with tab3:
    st.info("🚧 Pestaña de Evaluación IA en construcción.")

