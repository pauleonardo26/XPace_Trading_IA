# ============================================================
# XPACE TRADING IA - ESTRATEGIAS
# ============================================================

import pandas as pd

def generar_senales(df):
    """
    Genera señales cuantitativas de Compra (1) y Venta (-1) 
    verificando la presencia segura de SMA_20, SMA_50 y RSI.
    """
    df = df.copy()
    df["Senal"] = 0
    
    # Asegurar que existan las columnas requeridas
    if "SMA_20" in df.columns and "SMA_50" in df.columns and "RSI" in df.columns:
        condicion_compra = (df["SMA_20"] > df["SMA_50"]) & (df["RSI"] > 50)
        condicion_venta = (df["SMA_20"] < df["SMA_50"]) & (df["RSI"] < 50)
        
        df.loc[condicion_compra, "Senal"] = 1
        df.loc[condicion_venta, "Senal"] = -1
        
    return df



