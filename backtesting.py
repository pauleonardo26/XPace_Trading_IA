# ============================================================
# XPACE TRADING IA - BACKTESTING
# ============================================================

import pandas as pd
import numpy as np

def ejecutar_backtesting(df, capital_inicial=10000.0, pips_sl=20, ratio_rr=2.0):
    """
    Ejecuta una simulación de backtesting registrando cada trade de forma transparente.
    Devuelve la evolución del DataFrame y el resumen detallado de operaciones.
    """
    if df is None or df.empty or "Senal" not in df.columns:
        return None, "Error: El DataFrame no contiene datos válidos o señales para evaluar."
        
    df = df.copy()
    
    # --- MEJORA: Cálculo de Evolucion_Capital para solucionar el KeyError en app.py ---
    df["Retorno_Precio"] = df["Close"].pct_change().fillna(0)
    df["Retorno_Estrategia"] = (df["Senal"].shift(1) * df["Retorno_Precio"]).fillna(0)
    df["Evolucion_Capital"] = capital_inicial * (1 + df["Retorno_Estrategia"]).cumprod()
    
    # Rastrear trades individuales
    df["Bloque_Trade"] = (df["Senal"] != df["Senal"].shift(1)).cumsum()
    trades_activos = df[df["Senal"] != 0].copy()
    
    historial_trades = []
    capital_actual = capital_inicial
    
    if not trades_activos.empty:
        grupos = trades_activos.groupby("Bloque_Trade")
        for bloque_id, grupo in grupos:
            tipo_operacion = "COMPRA 🟢" if grupo["Senal"].iloc[0] == 1 else "VENTA 🔴"
            fecha_entrada = grupo.index[0] if isinstance(grupo.index[0], str) else str(grupo.index[0])
            fecha_salida = grupo.index[-1] if isinstance(grupo.index[-1], str) else str(grupo.index[-1])
            
            precio_entrada = grupo["Close"].iloc[0]
            precio_salida = grupo["Close"].iloc[-1]
            
            # Retorno según dirección de la señal
            if grupo["Senal"].iloc[0] == 1:
                retorno_pct = (precio_salida - precio_entrada) / precio_entrada
            else:
                retorno_pct = (precio_entrada - precio_salida) / precio_entrada
                
            pnl_usd = capital_actual * retorno_pct
            capital_actual += pnl_usd
            resultado = "GANADA 🟢" if pnl_usd > 0 else ("PERDIDA 🔴" if pnl_usd < 0 else "NEUTRAL ⚪")
            
            historial_trades.append({
                "Tipo": tipo_operacion,
                "Fecha Entrada": fecha_entrada,
                "Fecha Salida": fecha_salida,
                "Precio Entrada": round(precio_entrada, 5),
                "Precio Salida": round(precio_salida, 5),
                "Resultado": resultado,
                "Ganancia/Pérdida ($)": round(pnl_usd, 2),
                "Rendimiento (%)": f"{retorno_pct * 100:.2f}%",
                "Capital Restante ($)": round(capital_actual, 2)
            })

    df_trades = pd.DataFrame(historial_trades)
    
    ganadoras = len(df_trades[df_trades["Resultado"] == "GANADA 🟢"]) if not df_trades.empty else 0
    perdedoras = len(df_trades[df_trades["Resultado"] == "PERDIDA 🔴"]) if not df_trades.empty else 0
    total_operaciones = len(df_trades)
    
    win_rate = (ganadoras / total_operaciones * 100) if total_operaciones > 0 else 0.0
    rendimiento_total = ((capital_actual - capital_inicial) / capital_inicial) * 100
    
    resumen = {
        "Capital Inicial": f"${capital_inicial:,.2f}",
        "Capital Final": f"${capital_actual:,.2f}",
        "Rendimiento Total": f"{rendimiento_total:.2f}%",
        "Total Operaciones": total_operaciones,
        "Operaciones Ganadoras": ganadoras,
        "Operaciones Perdedoras": perdedoras,
        "Win Rate": f"{win_rate:.2f}%",
        "Detalle Trades": df_trades
    }
    
    return df, resumen


def ejecutar_backtest(df, capital_inicial=10000.0):
    """
    Alias para mantener compatibilidad con app.py devolviendo la tupla de variables.
    """
    df_res, resumen = ejecutar_backtesting(df, capital_inicial)
    if isinstance(resumen, str):
        return df_res, 0.0, 0, 0, 0.0, 0, capital_inicial
    
    rendimiento_num = float(resumen["Rendimiento Total"].replace("%", ""))
    ganadoras = resumen["Operaciones Ganadoras"]
    perdedoras = resumen["Operaciones Perdedoras"]
    win_rate_num = float(resumen["Win Rate"].replace("%", ""))
    total_ops = resumen["Total Operaciones"]
    capital_final_num = float(resumen["Capital Final"].replace("$", "").replace(",", ""))
    
    return df_res, rendimiento_num, ganadoras, perdedoras, win_rate_num, total_ops, capital_final_num




