# ============================================================
# XPACE TRADING IA - GESTIÓN DE RIESGO
# ============================================================

import pandas as pd

def calcular_gestion_riesgo(capital=10000.0, porcentaje_riesgo=1.0, precio_entrada=1.0850, ratio_rr=2.0, pips_sl=20):
    """
    Calcula el tamaño de la posición (lote), Stop Loss y Take Profit 
    con un Ratio Riesgo:Beneficio optimizado de 1:2.
    """
    try:
        # Monto máximo dispuesto a perder en dinero
        monto_riesgo = capital * (porcentaje_riesgo / 100.0)
        
        # Valor estimado por pip por lote estándar en Forex ($10 USD por pip aproximadamente en EUR/USD)
        valor_pip = 10.0
        
        # Cálculo del tamaño de la posición en lotes estándar
        lotes = monto_riesgo / (pips_sl * valor_pip)
        unidades = lotes * 100000
        
        # Distancia del Pip en Forex (4 decimales para la mayoría de pares)
        distancia_pip = 0.0001
        
        # Cálculo de Stop Loss y Take Profit con Ratio 1:2
        distancia_sl = pips_sl * distancia_pip
        distancia_tp = (pips_sl * ratio_rr) * distancia_pip
        
        sl_comprador = precio_entrada - distancia_sl
        tp_comprador = precio_entrada + distancia_tp
        
        sl_vendedor = precio_entrada + distancia_sl
        tp_vendedor = precio_entrada - distancia_tp
        
        resumen = {
            "Capital Inicial": f"${capital:,.2f} USD",
            "Monto en Riesgo": f"${monto_riesgo:,.2f} USD",
            "Riesgo (%)": f"{porcentaje_riesgo}%",
            "Ratio R:R": f"1:{ratio_rr}",
            "Lotes Sugeridos": f"{lotes:.2f}",
            "Tamaño Posición (Unidades)": f"{unidades:,.0f}",
            "Stop Loss (SL) Comprador": f"{sl_comprador:.5f}",
            "Take Profit (TP) Comprador": f"{tp_comprador:.5f}",
            "Stop Loss (SL) Vendedor": f"{sl_vendedor:.5f}",
            "Take Profit (TP) Vendedor": f"{tp_vendedor:.5f}"
        }
        
        return resumen
        
    except Exception as e:
        return {"Error": f"No se pudo calcular el riesgo: {str(e)}"}


