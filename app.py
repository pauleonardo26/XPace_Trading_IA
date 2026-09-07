import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, date

# Simulación de carga de datos para Forex
def obtener_datos_forex(par, fecha_sel, tf_sel):
    # Generación de fechas dentro del rango para la temporalidad
    fechas = pd.date_range(end=datetime.combine(fecha_sel, datetime.min.time()), periods=40, freq='H' if '1H' in tf_sel else 'D')
    
    # Precios simulados base según el par
    base_price = 1.0850 if "EUR" in par else 150.25
    import numpy as np
    np.random.seed(42)
    cambios = np.random.normal(0, 0.002 if "EUR" in par else 0.2, size=len(fechas))
    precios = base_price + np.cumsum(cambios)
    
    df = pd.DataFrame({
        'Open': precios - 0.0005,
        'High': precios + 0.0015,
        'Low': precios - 0.0015,
        'Close': precios,
    }, index=fechas)
    return df

# Diagnóstico pedagógico del Profesor IA
def generar_explicacion_profesor(par, fecha_sel, tf_sel, df):
    p_act = df['Close'].iloc[-1]
    p_open = df['Open'].iloc[-1]
    es_verde = p_act >= p_open
    
    color_txt = "verde 🟢 (compradores al mando)" if es_verde else "roja 🔴 (vendedores al mando)"
    
    explicacion = f"""
    ### 🗣️ Lección del Profesor IA — {par} ({tf_sel})
    **Fecha analizada:** {fecha_sel.strftime('%d/%m/%Y')}
    
    ---
    
    #### 1. ¿Qué estamos viendo en el gráfico?
    * **Dirección reciente:** La última vela registrada es de color **{color_txt}**. Esto nos indica quién ganó la batalla en ese intervalo de tiempo.
    * **Patrón de Vela Destacado (El Martillo 🔨):** Si observas las velas con cola larga abajo y cuerpo pequeño arriba, representan un "Martillo". Significa que los vendedores intentaron empujar el precio hacia el suelo, pero los compradores reaccionaron con fuerza y lo regresaron hacia arriba.
    
    #### 2. Tendencia y Estructura
    * El mercado muestra una **Estructura en Rango/Tendencia Local**. Los "pisos" (soportes) están aguantando el precio para evitar que siga cayendo.
    
    #### 3. Consejo de Gestión de Riesgo (Stop Loss & Take Profit)
    * **Límite de Pérdida (Stop Loss):** Si hubieras entrado en compra hoy, tu límite de seguridad debió colocarse **justo debajo del último piso (soporte)** para proteger tu dinero si el mercado se daba la vuelta.
    * **Meta de Ganancia (Take Profit):** Tu objetivo de cobro ideal estaría cerca del **techo más cercano (resistencia)**.
    """
    return explicacion

# ------------------ CONFIGURACIÓN DE PÁGINA ------------------
st.set_page_config(page_title="XPace — Escuela de Trading", layout="wide", page_icon="🎓")

# Estilos CSS limpios
st.markdown("""
    <style>
    .stApp { background-color: #0b0e14 !important; color: #e6edf3 !important; }
    .block-container { padding-top: 1rem !important; }
    </style>
""", unsafe_allow_html=True)

st.title("🎓 XPace — Plataforma Educativa de Trading")
st.caption("Aprende a analizar mercados con asistencia pedagógica de Inteligencia Artificial")

# ------------------ NAVEGACIÓN POR PESTAÑAS ------------------
tab1, tab2, tab3 = st.tabs(["📈 Histórico Educativo", "🧪 Backtesting (Próximamente)", "🤖 Evaluación IA (Próximamente)"])

# ==============================================================================
# PESTAÑA 1: HISTÓRICO EDUCATIVO (OPERATIVA)
# ==============================================================================
with tab1:
    st.subheader("📌 Clase de Análisis Visual e Histórico")
    
    # 1. Panel de Filtros
    col_par, col_fecha, col_tf = st.columns([1.5, 1.5, 2])
    
    with col_par:
        par_seleccionado = st.selectbox("1. Selecciona el Par de Forex", ["EUR/USD", "USD/JPY", "GBP/USD", "EUR/JPY"])
        
    with col_fecha:
        fecha_seleccionada = st.date_input(
            "2. Selecciona la Fecha",
            value=date(2026, 1, 15),
            min_value=date(2026, 1, 1),
            max_value=date(2026, 8, 31)
        )
        
    with col_tf:
        tf_seleccionada = st.select_slider(
            "3. Temporalidad",
            options=["15M", "1H", "4H", "1D", "1W", "1M"],
            value="1H"
        )

    # Validar fin de semana
    if fecha_seleccionada.weekday() >= 5:
        st.warning("⚠️ La fecha seleccionada cae en fin de semana. El mercado Forex está cerrado los sábados y domingos. Selecciona un día entre lunes y viernes.")
    else:
        # Carga de datos
        df_historico = obtener_datos_forex(par_seleccionado, fecha_seleccionada, tf_seleccionada)
        
        # 2. Lienzo Gráfico de Velas Japonesas
        fig = go.Figure()
        fig.add_trace(go.Candlestick(
            x=df_historico.index,
            open=df_historico['Open'],
            high=df_historico['High'],
            low=df_historico['Low'],
            close=df_historico['Close'],
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
            yaxis=dict(side="right", gridcolor="#151a23"),
            xaxis=dict(gridcolor="#151a23"),
            hovermode=False
        )

        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

        # 3. Botón de Explicación Didáctica
        if st.button("💡 Explicar Gráfico con Profesor IA", type="primary", use_container_width=True):
            explicacion_txt = generar_explicacion_profesor(par_seleccionado, fecha_seleccionada, tf_seleccionada, df_historico)
            st.info(explicacion_txt)

# ==============================================================================
# PESTAÑA 2: BACKTESTING (EN CONSTRUCCIÓN)
# ==============================================================================
with tab2:
    st.info("🚧 **Pestaña en construcción.** Aquí configuraremos los botones de Compra/Venta, Stop Loss, Take Profit y parámetros de estrategia una vez aprobemos la Pestaña 1.")

# ==============================================================================
# PESTAÑA 3: EVALUACIÓN IA (EN CONSTRUCCIÓN)
# ==============================================================================
with tab3:
    st.info("🚧 **Pestaña en construcción.** Aquí la IA evaluará las decisiones tomadas en el Backtesting.")






