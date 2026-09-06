# ============================================================
# XPACE TRADING IA - ANALISTA IA
# ============================================================

def generar_informe_analista(par, temporalidad, precio_actual, rsi, sma_20, sma_50, senal, resumen_riesgo=None):
    """
    Genera un diagnóstico objetivo en lenguaje natural basado en los datos cuantitativos.
    """
    # 1. Determinar el estado de la tendencia por medias móviles
    if sma_20 > sma_50:
        tendencia = "Alcista (SMA 20 por encima de SMA 50)"
    elif sma_20 < sma_50:
        tendencia = "Bajista (SMA 20 por debajo de SMA 50)"
    else:
        tendencia = "Lateral / Indefinida"

    # 2. Diagnóstico del oscilador RSI
    if rsi >= 70:
        estado_rsi = "Sobrecompra (zona de posible agotamiento comprador)"
    elif rsi <= 30:
        estado_rsi = "Sobreventa (zona de posible agotamiento vendedor)"
    elif rsi > 50:
        estado_rsi = "Momentum comprador (por encima de 50)"
    else:
        estado_rsi = "Momentum vendedor (por debajo de 50)"

    # 3. Interpretación de la señal de la estrategia
    if senal == 1:
        postura = "EVALUAR ENTRADA EN COMPRA (LONG)"
        justificacion = "Coinciden la tendencia alcista y el impulso del RSI superior a 50."
    elif senal == -1:
        postura = "EVALUAR ENTRADA EN VENTA (SHORT)"
        justificacion = "Coinciden la tendencia bajista y el impulso del RSI inferior a 50."
    else:
        postura = "MANTENERSE AL MARGEN (NEUTRAL)"
        justificacion = "El mercado no cumple todas las reglas de entrada simultáneamente."

    # 4. Construcción del informe en formato estructurado
    informe = f"""
📌 **DIAGNÓSTICO TÉCNICO XPace IA**
---
* **Par:** {par}
* **Temporalidad:** {temporalidad}
* **Precio Actual:** {precio_actual:.5f}

📊 **EVALUACIÓN DE MERCADO:**
* **Tendencia:** {tendencia}
* **Indicador RSI (14):** {rsi:.2f} → {estado_rsi}

🎯 **POSTURA DEL SISTEMA:**
* **Estado:** {postura}
* **Razón Técnica:** {justificacion}

⚠️ **GESTIÓN Y ADVERTENCIA:**
* Recuerda que las señales son probabilísticas, nunca certezas.
* Si decider operar, valida que la pérdida potencial respete el límite máximo configurado en tu gestión de riesgo.
"""
    if resumen_riesgo:
        informe += f"\n🛡️ **REGLA DE RIESGO SUGERIDA:**\n"
        informe += f"* SL: {resumen_riesgo.get('Stop Loss (SL)')} | TP: {resumen_riesgo.get('Take Profit (TP)')}\n"
        informe += f"* Posición Máxima: {resumen_riesgo.get('Tamaño Posición (Unidades)')}\n"

    return informe

