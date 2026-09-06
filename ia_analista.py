# ============================================================
# XPACE TRADING IA - ANALISTA IA
# ============================================================

def generar_informe_analista(par, temporalidad, precio_actual, rsi, sma_20, sma_50, senal, resumen_riesgo=None):
    """
    Genera un informe analítico avanzado evaluando tendencia, osciladores, 
    volatilidad y estructura de mercado sin generar falsas expectativas.
    """
    # 1. Análisis Avanzado de Tendencia e Impulso
    diferencia_sma = abs(sma_20 - sma_50) / precio_actual * 100
    
    if sma_20 > sma_50:
        estado_tendencia = "ALCISTA SÓLIDA" if diferencia_sma > 0.15 else "ALCISTA DÉBIL / CONSOLIDACIÓN"
    elif sma_20 < sma_50:
        estado_tendencia = "BAJISTA SÓLIDA" if diferencia_sma > 0.15 else "BAJISTA DÉBIL / CONSOLIDACIÓN"
    else:
        estado_tendencia = "LATERAL / INDEFINIDA"

    # 2. Diagnóstico Técnico del RSI (14)
    if rsi >= 70:
        diagnostico_rsi = f"SOBRECOMPRA ({rsi:.1f}) — Riesgo de corrección a la baja."
    elif rsi <= 30:
        diagnostico_rsi = f"SOBREVENTA ({rsi:.1f}) — Riesgo de rebote al alza."
    elif 50 <= rsi < 70:
        diagnostico_rsi = f"MOMENTUM COMPRADOR ({rsi:.1f}) — Impulso a favor de las compras."
    else:
        diagnostico_rsi = f"MOMENTUM VENDEDOR ({rsi:.1f}) — Impulso a favor de las ventas."

    # 3. Evaluación de Volatilidad / Compresión de Precio
    if diferencia_sma < 0.05:
        alerta_volatilidad = "⚠️ Mercado comprimido (Squeeze). Evitar entradas agresivas hasta ver ruptura clara."
    else:
        alerta_volatilidad = "✅ Volatilidad adecuada para operar con la tendencia actual."

    # 4. Decisión Cuantitativa y Plan de Acción
    if senal == 1 and "ALCISTA" in estado_tendencia and rsi > 50:
        postura = "🟢 COMPRA CONFIRMADA (LONG)"
        plan = "Buscar operaciones a favor de la tendencia alcista. Validar con el Stop Loss asignado."
        invalidacion = f"Si el precio cierra por debajo de la SMA 50 ({sma_50:.5f}), la hipótesis alcista se anula."
    elif senal == -1 and "BAJISTA" in estado_tendencia and rsi < 50:
        postura = "🔴 VENTA CONFIRMADA (SHORT)"
        plan = "Buscar operaciones a favor de la tendencia bajista. Validar con el Stop Loss asignado."
        invalidacion = f"Si el precio cierra por encima de la SMA 50 ({sma_50:.5f}), la hipótesis bajista se anula."
    else:
        postura = "🟡 MANTENERSE AL MARGEN (ESPERAR)"
        plan = "El mercado no muestra una convergencia clara entre tendencia y momento. Es mejor esperar un patrón limpio."
        invalidacion = "No hay operación activa en riesgo actualmente."

    # 5. Construcción del Reporte Completo
    informe = f"""
🧠 **DIAGNÓSTICO AVANZADO XPace IA**
---
* **Activo:** {par} | **Temporalidad:** {temporalidad}
* **Precio Mercado:** {precio_actual:.5f}

📊 **ESTRUCTURA TÉCNICA DEL MERCADO:**
* **Estructura:** {estado_tendencia}
* **Fuerza RSI (14):** {diagnostico_rsi}
* **Estado de Volatilidad:** {alerta_volatilidad}

🎯 **POSTURA DEL SISTEMA:**
* **Diagnóstico:** {postura}
* **Estrategia Recomendada:** {plan}
* **Nivel de Invalidación:** {invalidacion}
"""

    # 6. Integración opcional de la Gestión de Riesgo
    if resumen_riesgo:
        informe += f"""
🛡️ **PARÁMETROS DE RIESGO SUGERIDOS:**
* **Stop Loss (SL):** {resumen_riesgo.get('Stop Loss (SL)', 'N/A')}
* **Take Profit (TP):** {resumen_riesgo.get('Take Profit (TP)', 'N/A')}
* **Gestión de Lote:** {resumen_riesgo.get('Tamaño Posición (Unidades)', 'N/A')}
* **Riesgo Permitido:** {resumen_riesgo.get('Monto en Riesgo', 'N/A')} ({resumen_riesgo.get('Riesgo (%)', 'N/A')})
"""

    return informe


