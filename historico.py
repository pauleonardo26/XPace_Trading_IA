# ============================================================
# XPACE TRADING IA - DATOS HISTÓRICOS
# ============================================================

import requests
import pandas as pd
from conexion_oanda import obtener_configuracion

# Mapeo de temporalidades de interfaz humana a formato de OANDA
MAPEO_TEMPORALIDAD = {
    "15 Minutos (M15)": "M15",
    "1 Hora (H1)": "H1",
    "4 Horas (H4)": "H4",
    "1 Día (D1)": "D"
}

# Mapeo de nombres de pares a formato de OANDA
MAPEO_PARES = {
    "EUR/USD": "EUR_USD",
    "GBP/USD": "GBP_USD",
    "USD/JPY": "USD_JPY"
}

def obtener_historico(par="EUR/USD", temporalidad="1 Hora (H1)", cantidad=100):
    """
    Descarga velas históricas OHLC desde la API de OANDA y las devuelve en un DataFrame de Pandas.
    """
    token, account_id, url_base = obtener_configuracion()
    
    if not token or token == "TU_TOKEN_AQUI":
        return None, "Error: Configura tu OANDA_TOKEN en el archivo .env"
        
    instrumento = MAPEO_PARES.get(par, "EUR_USD")
    granularity = MAPEO_TEMPORALIDAD.get(temporalidad, "H1")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    endpoint = f"{url_base}/instruments/{instrumento}/candles"
    params = {
        "count": cantidad,
        "granularity": granularity,
        "price": "M"  # Precios Mid (Promedio entre oferta y demanda)
    }
    
    try:
        respuesta = requests.get(endpoint, headers=headers, params=params, timeout=10)
        
        if respuesta.status_code == 200:
            datos = respuesta.json()
            velas = datos.get("candles", [])
            
            registros = []
            for v in velas:
                # Solo procesar velas completas (cerradas)
                if v.get("complete", False):
                    mid = v.get("mid", {})
                    registros.append({
                        "Fecha": v.get("time"),
                        "Open": float(mid.get("o", 0)),
                        "High": float(mid.get("h", 0)),
                        "Low": float(mid.get("l", 0)),
                        "Close": float(mid.get("c", 0)),
                        "Volumen": int(v.get("volume", 0))
                    })
            
            # Convertir a DataFrame de Pandas
            df = pd.DataFrame(registros)
            if not df.empty:
                df["Fecha"] = pd.to_datetime(df["Fecha"])
                
            return df, f"Se descargaron {len(df)} velas exitosamente."
        else:
            return None, f"Error OANDA ({respuesta.status_code}): {respuesta.text}"
            
    except Exception as e:
        return None, f"Error de red/conexión al descargar histórico: {str(e)}"

