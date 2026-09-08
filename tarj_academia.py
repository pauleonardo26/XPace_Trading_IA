import streamlit as st
import plotly.graph_objects as go

def render():
    st.write("## 📖 Plan de Estudio: De Cero a Trader Profesional")
    st.caption("Selecciona un nivel para aprender la teoría respaldada por gráficos didácticos.")

    nivel = st.selectbox(
        "Elige un Nivel de Aprendizaje:",
        [
            "🟢 Nivel 1: Los Fundamentos (Velas Japonesas)",
            "🟡 Nivel 2: Estructura de Mercado (Soportes y Resistencias)",
            "🟠 Nivel 3: Indicadores Técnicos (RSI y Bandas de Bollinger)",
            "🔴 Nivel 4: Gestión de Riesgo (Stop Loss)",
            "🟣 Nivel 5: Psicología y Plan de Trading"
        ]
    )

    st.markdown("---")

    if "Nivel 1" in nivel:
        st.write("### 🟢 Nivel 1: Anatomía de una Vela Japonesa")
        st.write("""
        Las **Velas Japonesas** representan el movimiento del precio durante un período determinado.
        * **Cuerpo:** Diferencia entre el precio de Apertura y Cierre.
        * **Verde (Alcista):** El precio subió (Cierre > Apertura).
        * **Roja (Bajista):** El precio cayó (Cierre < Apertura).
        * **Mechas:** Muestran los precios Máximo y Mínimo alcanzados.
        """)

        fig_velas = go.Figure()
        fig_velas.add_trace(go.Candlestick(
            x=['Vela Alcista', 'Vela Bajista'],
            open=[1.0950, 1.1000], high=[1.1020, 1.1020],
            low=[1.0930, 1.0930], close=[1.1000, 1.0950],
            increasing_line_color='#00e676', decreasing_line_color='#ff1744'
        ))
        fig_velas.update_layout(
            template="plotly_dark", height=320, title="Anatomía de Velas",
            paper_bgcolor="#0b0e14", plot_bgcolor="#0b0e14", xaxis_rangeslider_visible=False
        )
        st.plotly_chart(fig_velas, use_container_width=True)

    elif "Nivel 2" in nivel:
        st.write("### 🟡 Nivel 2: Soportes y Resistencias")
        st.write("""
        * **Soporte (Piso):** Zona donde la demanda supera la oferta. El precio suele rebotar hacia arriba.
        * **Resistencia (Techo):** Zona donde la oferta supera la demanda. El precio suele rebotar hacia abajo.
        """)

        fig_sr = go.Figure()
        fig_sr.add_trace(go.Scatter(
            x=list(range(10)), y=[10, 15, 11, 15, 10.5, 14.8, 10.2, 15.1, 11, 15],
            mode='lines+markers', line=dict(color='#2196f3', width=2), name='Precio'
        ))
        fig_sr.add_hline(y=15, line_dash="dash", line_color="#ff1744", annotation_text="Techo (Resistencia)")
        fig_sr.add_hline(y=10, line_dash="dash", line_color="#00e676", annotation_text="Piso (Soporte)")
        fig_sr.update_layout(template="plotly_dark", height=320, paper_bgcolor="#0b0e14", plot_bgcolor="#0b0e14")
        st.plotly_chart(fig_sr, use_container_width=True)

    elif "Nivel 3" in nivel:
        st.write("### 🟠 Nivel 3: Indicadores Técnicos")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("#### RSI (14)")
            st.write("Mide sobrecompra (>70) y sobrevenda (<30) para anticipar giros.")
        with col2:
            st.markdown("#### Bandas de Bollinger")
            st.write("Envuelven el precio definiendo rangos de volatilidad normales.")

    elif "Nivel 4" in nivel:
        st.write("### 🔴 Nivel 4: Gestión de Riesgo")
        st.write("Usa siempre Stop Loss (SL). Nunca arriesgues más del 1% al 2% de la cuenta por operación.")

    elif "Nivel 5" in nivel:
        st.write("### 🟣 Nivel 5: Psicotrading")
        st.write("Evita el FOMO y respeta estrictamente tu plan de trading predefinido.")

