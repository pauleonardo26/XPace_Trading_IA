# ============================================================
# XPACE TRADING IA - ESTRATEGIAS
# ============================================================

import pandas as pd
from indicadores import calcular_indicadores

def evaluar_estrategia_cruces(df):
    """
    Estrategia de Tendencia + Momento (SMA 20/50 + RSI 14).
    Genera señales en el cruce exacto: 1 (Compra), -1 (Venta), 0 (Neutral).
    """
    if df is None or df.empty:
        return df
        
    # Asegurar que el DataFrame contenga los indicadores
    # Soportar 'RSI_14' o 'RSI' segun el nombre configurado en indicadores
    col_rsi = "RSI_14" if "RSI_14" in df.columns else "RSI"
    
    if "SMA_20" not in df.columns or col_rsi not in df.columns:
        df = calcular_indicadores(df)
        col_rsi = "RSI_14" if "RSI_14" in df.columns else "RSI"
        
    df = df.copy()
    
    # Inicializar la columna de señales en 0 (Neutral)
    df["Senal"] = 0
    
    # Detección del punto de cruce de Medias Móviles (Crossover)
    cruce_alcista = (df["SMA_20"] > df["SMA_50"]) & (df["SMA_20"].shift(1) <= df["SMA_50"].shift(1))
    cruce_bajista = (df["SMA_20"] < df["SMA_50"]) & (df["SMA_20"].shift(1) >= df["SMA_50"].shift(1))
    
    # Condición Alcista (Compra en el cruce + confirmación RSI)
    condicion_compra = cruce_alcista & (df[col_rsi] > 50)
    
    # Condición Bajista (Venta en el cruce + confirmación RSI)
    condicion_venta = cruce_bajista & (df[col_rsi] < 50)
    
    # Asignar las señales en el DataFrame
    df.loc[condicion_compra, "Senal"] = 1
    df.loc[condicion_venta, "Senal"] = -1
    
    return df

# Alias para garantizar compatibilidad total con app.py
generar_senales = evaluar_estrategia_cruces


