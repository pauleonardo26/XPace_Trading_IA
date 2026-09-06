# ============================================================
# XPACE TRADING IA - CONEXIÓN CON OANDA
# ============================================================

import os
import requests
from dotenv import load_dotenv

load_dotenv()

def obtener_configuracion():
    """Lee y retorna las credenciales cargadas desde el archivo .env."""
    token = os.getenv("OANDA_TOKEN")
    account_id = os.getenv("OANDA_ACCOUNT_ID")
    entorno = os.getenv("OANDA_ENV", "practice")
    
    # Definir URL base según el entorno (Practice o Real)
    if entorno == "practice":
        url_base = "https://api-fxpractice.oanda.com/v3"
    else:
        url_base = "https://api-fxtrade.oanda.com/v3"
        
    return token, account_id, url_base

def probar_conexion_oanda():
    """
    Realiza una solicitud real a OANDA para verificar si las credenciales son válidas.
    """
    token, account_id, url_base = obtener_configuracion()
    
    if not token or token == "TU_TOKEN_AQUI":
        return False, "Error: Configura tu OANDA_TOKEN en el archivo .env"
        
    if not account_id or account_id == "TU_ACCOUNT_ID_AQUI":
        return False, "Error: Configura tu OANDA_ACCOUNT_ID en el archivo .env"
        
    # Encabezados de seguridad requeridos por OANDA
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Endpoint para consultar el resumen de la cuenta
    url = f"{url_base}/accounts/{account_id}/summary"
    
    try:
        respuesta = requests.get(url, headers=headers, timeout=10)
        
        if respuesta.status_code == 200:
            datos = respuesta.json()
            alias = datos.get("account", {}).get("alias", "Cuenta Practice")
            balance = datos.get("account", {}).get("balance", "0.00")
            moneda = datos.get("account", {}).get("currency", "USD")
            return True, f"Conexión Exitosa. Cuenta: {alias} | Balance: {balance} {moneda}"
        elif respuesta.status_code == 401:
            return False, "Error 401: Token de OANDA no válido o expirado."
        elif respuesta.status_code == 404:
            return False, "Error 404: Account ID no encontrado."
        else:
            return False, f"Error OANDA ({respuesta.status_code}): {respuesta.text}"
            
    except Exception as e:
        return False, f"Error de red/conexión: {str(e)}"



