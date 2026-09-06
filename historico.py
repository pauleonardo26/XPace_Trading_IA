# ============================================================
# XPACE TRADING IA - DATOS HISTÓRICOS
# ============================================================

import pandas as pd
import yfinance as yf

def obtener_historico(par="EUR/USD", temporalidad="1 Hora (H1)", cantidad=100):
    """
    Descarga datos de Yahoo Finance y limpia las columnas para evitar errores de KeyError.
    """
    # Mapeo de pares a tickers de Yahoo Finance
    tickers = {
        "EUR/USD": "EURUSD=X",
        "GBP/USD": "GBPUSD=X",
        "USD/JPY": "JPY=X"
    }
    
    # Mapeo de temporalidades
    intervalos = {
        "15 Minutos (M15)": ("15m", "1mo"),
        "1 Hora (H1)": ("1h", "2mo"),
        "4 Horas (H4)": ("1h", "3mo"),
        "1 Día (D1)": ("1d", "2y")
    }
    
    ticker = tickers.get(par, "EURUSD=X")
    intervalo, periodo = intervalos.get(temporalidad, ("1h", "2mo"))
    
    try:
        df = yf.download(ticker, period=periodo, interval=intervalo, progress=False)
        
        if df.empty:
            return None, "No se recibieron datos de Yahoo Finance."
            
        # Aplanar MultiIndex de columnas si Yahoo Finance lo devuelve
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
            
        # Asegurar que existan las columnas esenciales
        df = df.reset_index()
        
        # Buscar columna de precio de cierre
        col_close = [c for c in df.columns if str(c).lower() in ["close", "adj close"]]
        if col_close:
            df["Close"] = df[col_close[0]]
        else:
            return None, "La columna Close no está presente en los datos."

        # Filtrar solo las últimas 'cantidad' de velas solicitadas
        df = df.tail(int(cantidad)).copy()
        return df, "OK"
        
    except Exception as e:
        return None, f"Error al descargar datos: {str(e)}"
