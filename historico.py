# ============================================================
# XPACE TRADING IA - DATOS HISTÓRICOS
# ============================================================

import pandas as pd
import yfinance as yf

# Mapeo de pares de Forex al formato que entiende Yahoo Finance
SIMBOLOS_YAHOO = {
    "EUR/USD": "EURUSD=X",
    "GBP/USD": "GBPUSD=X",
    "USD/JPY": "JPY=X"
}

# Mapeo de temporalidades al formato de Yahoo Finance
TEMPORALIDADES_YAHOO = {
    "15 Minutos (M15)": "15m",
    "1 Hora (H1)": "1h",
    "4 Horas (H4)": "1h",  # Yahoo usa 1h para granularidad intraddía alta
    "1 Día (D1)": "1d"
}

def obtener_historico(par="EUR/USD", temporalidad="1 Hora (H1)", cantidad=100):
    """
    Descarga datos históricos de precios usando la librería gratuita Yahoo Finance.
    Retorna un DataFrame de Pandas estandarizado con columnas: Date, Open, High, Low, Close, Volume.
    """
    try:
        simbolo = SIMBOLOS_YAHOO.get(par, "EURUSD=X")
        intervalo = TEMPORALIDADES_YAHOO.get(temporalidad, "1h")
        
        # Definir período de descarga según la cantidad solicitada
        periodo = "1mo" if intervalo in ["15m", "1h"] else "1y"
        
        # Descargar datos desde Yahoo Finance
        ticker = yf.Ticker(simbolo)
        df = ticker.history(period=periodo, interval=intervalo)
        
        if df.empty:
            return None, f"No se pudieron obtener datos de Yahoo Finance para {par}."
            
        # Limpiar y estandarizar el DataFrame
        df = df.reset_index()
        
        # Mapear nombres de columnas
        col_fecha = "Datetime" if "Datetime" in df.columns else "Date"
        df = df.rename(columns={
            col_fecha: "Date",
            "Open": "Open",
            "High": "High",
            "Low": "Low",
            "Close": "Close",
            "Volume": "Volume"
        })
        
        # Seleccionar las últimas N velas solicitadas
        df = df.tail(cantidad).copy()
        df["Date"] = pd.to_datetime(df["Date"]).dt.strftime('%Y-%m-%d %H:%M')
        
        return df[["Date", "Open", "High", "Low", "Close", "Volume"]], "Datos descargados exitosamente desde Yahoo Finance"
        
    except Exception as e:
        return None, f"Error al conectar con Yahoo Finance: {str(e)}"



