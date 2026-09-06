# ============================================================
# XPACE TRADING IA - BACKTESTING
# ============================================================

import pandas as pd
import numpy as np

def ejecutar_backtesting(df, capital_inicial=10000.0):
    """
    Ejecuta una simulación de backtesting basada en la columna 'Senal' del DataFrame.
    Calcula el rendimiento del capital, win rate y estadísticas clave.
    """
    if df is None or df.empty or "Senal" not in df.columns:
        return None, "Error: El DataFrame no contiene datos válidos o señales para evaluar."
        
    df = df.copy()
    
    # Calcular el cambio porcentual diario/por vela
    df["Retorno_Precio"] = df["Close"].pct_change()
    
    # El retorno de la estrategia depende de la señal de la vela anterior (shift 1)
    df["Retorno_Estrategia"] = df["Senal"].shift(1) * df["Retorno_Precio"]
    
    # Reemplazar valores nulos iniciales por 0
    df["Retorno_Estrategia"] = df["Retorno_Estrategia"].fillna(0)
    
    # Evolución del capital
    df["Evolucion_Capital"] = capital_inicial * (1 + df["Retorno_Estrategia"]).cumprod()
    
    # Estadísticas básicas de operaciones
    operaciones = df[df["Senal"].diff() != 0]
    total_operaciones = len(operaciones)
    
    retornos_positivos = df[df["Retorno_Estrategia"] > 0]["Retorno_Estrategia"]
    retornos_negativos = df[df["Retorno_Estrategia"] < 0]["Retorno_Estrategia"]
    
    ganadoras = len(retornos_positivos)
    perdedoras = len(retornos_negativos)
    total_efectivas = ganadoras + perdedoras
    
    win_rate = (ganadoras / total_efectivas * 100) if total_efectivas > 0 else 0.0
    
    capital_final = df["Evolucion_Capital"].iloc[-1]
    rendimiento_total = ((capital_final - capital_inicial) / capital_inicial) * 100
    
    resumen = {
        "Capital Inicial": f"${capital_inicial:,.2f}",
        "Capital Final": f"${capital_final:,.2f}",
        "Rendimiento Total": f"{rendimiento_total:.2f}%",
        "Total Cambios de Señal": total_operaciones,
        "Velas Ganadoras": ganadoras,
        "Velas Perdedoras": perdedoras,
        "Porcentaje de Aciertos (Win Rate)": f"{win_rate:.2f}%"
    }
    
    return df, resumen


