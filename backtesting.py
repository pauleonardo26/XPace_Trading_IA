# ============================================================
# XPACE TRADING IA - BACKTESTING
# ============================================================

import pandas as pd
import numpy as np

def ejecutar_backtesting(df, capital_inicial=10000.0):
    """
    Ejecuta una simulación de backtesting basada en la columna 'Senal' del DataFrame.
    Calcula el rendimiento del capital, win rate basado en trades cerrados y estadísticas clave.
    """
    if df is None or df.empty or "Senal" not in df.columns:
        return None, "Error: El DataFrame no contiene datos válidos o señales para evaluar."
        
    df = df.copy()
    
    # Calcular el cambio porcentual por vela
    df["Retorno_Precio"] = df["Close"].pct_change()
    
    # El retorno de la estrategia depende de la señal de la vela anterior (shift 1)
    df["Retorno_Estrategia"] = df["Senal"].shift(1) * df["Retorno_Precio"]
    df["Retorno_Estrategia"] = df["Retorno_Estrategia"].fillna(0)
    
    # Evolución del capital
    df["Evolucion_Capital"] = capital_inicial * (1 + df["Retorno_Estrategia"]).cumprod()
    
    # ------------------------------------------------------------
    # CÁLCULO DE TRADES COMPLETOS (Trade a Trade)
    # ------------------------------------------------------------
    df["Bloque_Trade"] = (df["Senal"] != df["Senal"].shift(1)).cumsum()
    
    # Filtrar solo los bloques donde hubo una posición activa (compra = 1, venta = -1)
    trades_activos = df[df["Senal"] != 0]
    
    ganadoras = 0
    perdedoras = 0
    total_operaciones = 0
    
    if not trades_activos.empty:
        # Calcular el retorno acumulado por cada operación (Trade)
        retorno_por_trade = trades_activos.groupby("Bloque_Trade")["Retorno_Estrategia"].apply(lambda x: (1 + x).prod() - 1)
        
        ganadoras = len(retorno_por_trade[retorno_por_trade > 0])
        perdedoras = len(retorno_por_trade[retorno_por_trade < 0])
        total_operaciones = len(retorno_por_trade)
    
    win_rate = (ganadoras / total_operaciones * 100) if total_operaciones > 0 else 0.0
    
    capital_final = df["Evolucion_Capital"].iloc[-1]
    rendimiento_total = ((capital_final - capital_inicial) / capital_inicial) * 100
    
    resumen = {
        "Capital Inicial": f"${capital_inicial:,.2f}",
        "Capital Final": f"${capital_final:,.2f}",
        "Rendimiento Total": f"{rendimiento_total:.2f}%",
        "Total Cambios de Señal": total_operaciones,
        "Operaciones Ganadoras": ganadoras,
        "Operaciones Perdedoras": perdedoras,
        "Porcentaje de Aciertos (Win Rate)": f"{win_rate:.2f}%"
    }
    
    return df, resumen

# Alias para compatibilidad con las diferentes llamadas de app.py
def ejecutar_backtest(df, capital_inicial=10000.0):
    df_res, resumen = ejecutar_backtesting(df, capital_inicial)
    if isinstance(resumen, str):
        return df_res, 0.0, 0, 0, 0.0, 0, capital_inicial
    
    # Extraer variables sueltas por si app.py espera la tupla de 7 elementos
    rendimiento_num = float(resumen["Rendimiento Total"].replace("%", ""))
    ganadoras = resumen["Operaciones Ganadoras"]
    perdedoras = resumen["Operaciones Perdedoras"]
    win_rate_num = float(resumen["Porcentaje de Aciertos (Win Rate)"].replace("%", ""))
    total_ops = resumen["Total Cambios de Señal"]
    capital_final_num = float(resumen["Capital Final"].replace("$", "").replace(",", ""))
    
    return df_res, rendimiento_num, ganadoras, perdedoras, win_rate_num, total_ops, capital_final_num



