# ============================================================
# XPACE TRADING IA - CONEXIÓN CON OANDA
# ============================================================

import os
from dotenv import load_dotenv

# Cargamos las variables del archivo .env a la memoria del sistema
load_dotenv()

def conectar_oanda():
    """
    Lee las credenciales guardadas en .env y verifica que existan.
    """
    token = os.getenv("OANDA_TOKEN")
    account_id = os.getenv("OANDA_ACCOUNT_ID")
    entorno = os.getenv("OANDA_ENV", "practice")
    
    if not token or token == "TU_TOKEN_AQUI":
        return False, "Error: El token no ha sido configurado en el archivo .env"
        
    if not account_id or account_id == "TU_ACCOUNT_ID_AQUI":
        return False, "Error: El ID de cuenta no ha sido configurado en el archivo .env"
        
    return True, f"Credenciales cargadas correctamente. Modo: {entorno}"

