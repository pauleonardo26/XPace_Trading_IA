# ============================================================
# XPACE TRADING IA - INDICADORES TÉCNICOS
# ============================================================

import pandas as pd

def calcular_indicadores(df):
    """
    Calcula Medias Móviles Simples (SMA 20 y SMA 50) y el Índice de Fuerza Relativa (RSI 14).
    Garantiza la creación limpia de la columna 'RSI'.
    """
    df = df.copy()
    
    # Calculo de Medias Móviles
    df["SMA_20"] = df["Close"].rolling(window=20).mean()
    df["SMA_50"] = df["Close"].rolling(window=50).mean()
    
    # Cálculo de RSI (14 periodos)
    delta = df["Close"].diff()
    ganancia = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    perdida = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    
    rs = ganancia / perdida
    df["RSI"] = 100 - (100 / (1 + rs))
    
    # Rellenar valores nulos iniciales con 50 (neutral) para evitar errores en las primeras filas
    df["RSI"] = df["RSI"].fillna(50)
    df["SMA_20"] = df["SMA_20"].bfill()
    df["SMA_50"] = df["SMA_50"].bfill()
    
    return df


