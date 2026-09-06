# ============================================================
# XPACE TRADING IA - INDICADORES TÉCNICOS
# ============================================================

import pandas as pd

def calcular_rsi(serie_precios, periodo=14):
    """
    Calcula el RSI (Relative Strength Index) a partir de una serie de precios de cierre.
    """
    diferencia = serie_precios.diff()
    
    ganancia = diferencia.clip(lower=0)
    perdida = -diferencia.clip(upper=0)
    
    # Media móvil exponencial para suavizar ganancias y pérdidas
    media_ganancia = ganancia.ewm(com=periodo - 1, adjust=False).mean()
    media_perdida = perdida.ewm(com=periodo - 1, adjust=False).mean()
    
    # Calcular RS (Relative Strength)
    rs = media_ganancia / media_perdida
    
    # Calcular RSI (0 a 100)
    rsi = 100 - (100 / (1 + rs))
    return rsi

def calcular_indicadores(df):
    """
    Recibe un DataFrame con datos OHLC y le agrega columnas con indicadores técnicos.
    """
    if df is None or df.empty:
        return df
        
    # Crear una copia para evitar modificar el DataFrame original directamente
    df = df.copy()
    
    # 1. Medias Móviles Simples (SMA)
    df["SMA_20"] = df["Close"].rolling(window=20).mean()
    df["SMA_50"] = df["Close"].rolling(window=50).mean()
    
    # 2. RSI de 14 períodos
    df["RSI_14"] = calcular_rsi(df["Close"], periodo=14)
    
    return df

