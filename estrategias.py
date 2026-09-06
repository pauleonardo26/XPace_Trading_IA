# ============================================================
# XPACE TRADING IA - ESTRATEGIAS
# ============================================================

import pandas as pd

def generar_senales(df):
    """
    Genera señales de trading validando la existencia de las columnas 
    para prevenir cualquier KeyError.
    """
    if df is None or df.empty:
        return df

    df = df.copy()
    df["Senal"] = 0

    # Crear columnas faltantes en caso de emergencia para no romper la app
    for col in ["SMA_20", "SMA_50", "RSI"]:
        if col not in df.columns:
            if col == "RSI":
                df[col] = 50.0
            else:
                df[col] = df["Close"]

    # Aplicar reglas de señal
    condicion_compra = (df["SMA_20"] > df["SMA_50"]) & (df["RSI"] > 50)
    condicion_venta = (df["SMA_20"] < df["SMA_50"]) & (df["RSI"] < 50)

    df.loc[condicion_compra, "Senal"] = 1
    df.loc[condicion_venta, "Senal"] = -1

    return df




