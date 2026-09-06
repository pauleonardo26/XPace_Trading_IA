# ============================================================
# XPACE TRADING IA - GESTIÓN DE RIESGO
# ============================================================

def calcular_riesgo_operacion(capital_total, porcentaje_riesgo, precio_entrada, distancia_stop_loss_pips, direccion="compra", relacion_rr=2.0, par="EUR/USD"):
    """
    Calcula el tamaño de posición en unidades, dinero en riesgo, Stop Loss y Take Profit.
    
    - porcentaje_riesgo: Expresado en número (ej. 1.0 para 1%)
    - distancia_stop_loss_pips: Distancia en pips (ej. 30.0)
    - relacion_rr: Relación Riesgo/Beneficio (ej. 2.0 para 1:2)
    """
    if capital_total <= 0 or porcentaje_riesgo <= 0 or distancia_stop_loss_pips <= 0 or precio_entrada <= 0:
        return None, "Error: Los valores de capital, riesgo y distancia de stop loss deben ser mayores a cero."
        
    # 1. Monto máximo en dinero a arriesgar
    monto_riesgo = capital_total * (porcentaje_riesgo / 100.0)
    
    # 2. Valor aproximado por pip según el par
    # En la mayoría de pares mayores (salvo JPY), 1 pip = 0.0001 en precio
    es_jpy = "JPY" in par
    factor_pip = 0.01 if es_jpy else 0.0001
    
    distancia_precio_sl = distancia_stop_loss_pips * factor_pip
    distancia_precio_tp = distancia_precio_sl * relacion_rr
    
    # 3. Niveles de Stop Loss y Take Profit
    if direccion.lower() == "compra":
        stop_loss = precio_entrada - distancia_precio_sl
        take_profit = precio_entrada + distancia_precio_tp
    else:  # venta
        stop_loss = precio_entrada + distancia_precio_sl
        take_profit = precio_entrada - distancia_precio_tp
        
    # 4. Cálculo aproximado de unidades (1 micro lote = 1,000 unidades)
    # 1 pip en 10,000 unidades (0.1 lote) equivale aprox. a $1.00 USD en pares USD de contraparte
    unidades = (monto_riesgo / (distancia_stop_loss_pips * factor_pip))
    unidades = round(unidades, -2)  # Redondear a centenas
    
    resumen_riesgo = {
        "Capital Total": f"${capital_total:,.2f}",
        "Riesgo (%)": f"{porcentaje_riesgo}%",
        "Monto en Riesgo": f"${monto_riesgo:,.2f}",
        "Precio Entrada": f"{precio_entrada:.5f}",
        "Stop Loss (SL)": f"{stop_loss:.5f}",
        "Take Profit (TP)": f"{take_profit:.5f}",
        "Distancia SL (Pips)": f"{distancia_stop_loss_pips} pips",
        "Relación R:R": f"1:{relacion_rr}",
        "Beneficio Potencial": f"${monto_riesgo * relacion_rr:,.2f}",
        "Tamaño Posición (Unidades)": f"{int(unidades):,} unidades"
    }
    
    return resumen_riesgo, "Cálculo de riesgo realizado exitosamente."

