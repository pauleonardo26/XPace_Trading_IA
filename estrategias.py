# ============================================================
# XPACE TRADING IA - ESTRATEGIAS
# ============================================================

import pandas as pd
import numpy as np

def generar_senales(df):
    """
    Genera señales cuantitativas de Compra (1), Venta (-1) y Neutral (0) 
    basadas en el cruce de Medias Móviles (SMA 20 y SMA 50) y confirmación por RSI.
    """
    df = df.copy()
    
    # Inicializar la columna de Señal en 0 (Neutral)
    df["Senal"] = 0
    
    # Condición Alcista: SMA_20 > SMA_50 y RSI por encima de 50 (fuerza compradora)
    condicion_compra = (df["SMA_20"] > df["SMA_50"]) & (df["RSI"] > 50)
    
    # Condición Bajista: SMA_20 < SMA_50 y RSI por debajo de 50 (fuerza vendedora)
    condicion_venta = (df["SMA_20"] < df["SMA_50"]) & (df["RSI"] < 50)
    
    # Asignar 1 para Compra y -1 para Venta
    df.loc[condicion_compra, "Senal"] = 1
    df.loc[condicion_venta, "Senal"] = -1
    
    return df


