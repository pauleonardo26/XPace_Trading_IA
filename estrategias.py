# ============================================================
# XPACE TRADING IA - ESTRATEGIAS
# ============================================================

import pandas as pd
from indicadores import calcular_indicadores

def evaluar_estrategia_cruces(df):
    """
    Estrategia de Tendencia + Momento (SMA 20/50 + RSI 14).
    Genera señales: 1 (Compra), -1 (Venta), 0 (Neutral).
    """
    if df is None or df.empty:
        return df
        
    # Asegurar que el DataFrame contenga los indicadores
    if "SMA_20" not in df.columns or "RSI_14" not in df.columns:
        df = calcular_indicadores(df)
        
    df = df.copy()
    
    # Inicializar la columna de señales en 0 (Neutral)
    df["Senal"] = 0
    
    # Condición Alcista (Compra)
    condicion_compra = (df["SMA_20"] > df["SMA_50"]) & (df["RSI_14"] > 50)
    
    # Condición Bajista (Venta)
    condicion_venta = (df["SMA_20"] < df["SMA_50"]) & (df["RSI_14"] < 50)
    
    # Asignar las señales en el DataFrame
    df.loc[condicion_compra, "Senal"] = 1
    df.loc[condicion_venta, "Senal"] = -1
    
    return df

