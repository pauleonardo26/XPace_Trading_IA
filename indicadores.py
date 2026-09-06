# ============================================================
# XPACE TRADING IA - INDICADORES TÉCNICOS
# ============================================================

import pandas as pd
import numpy as np

def calcular_indicadores(df):
    """
    Calcula SMA_20, SMA_50 y RSI garantizando que las columnas 
    existan en el DataFrame de retorno.
    """
    if df is None or df.empty:
        return df

    df = df.copy()

    # 1. Medias Móviles Simples
    df["SMA_20"] = df["Close"].rolling(window=20, min_periods=1).mean()
    df["SMA_50"] = df["Close"].rolling(window=50, min_periods=1).mean()

    # 2. Cálculo Seguro del RSI (14 periodos)
    delta = df["Close"].diff()
    ganancia = delta.clip(lower=0)
    perdida = -1 * delta.clip(upper=0)

    prom_ganancia = ganancia.rolling(window=14, min_periods=1).mean()
    prom_perdida = perdida.rolling(window=14, min_periods=1).mean()

    # Evitar división por cero
    prom_perdida = prom_perdida.replace(0, np.nan)
    rs = prom_ganancia / prom_perdida
    
    rsi = 100 - (100 / (1 + rs))
    df["RSI"] = rsi.fillna(50)  # Valor neutral por defecto para las primeras filas

    return df



