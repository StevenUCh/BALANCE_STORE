import pandas as pd
import re

def limpiar_precio(valor):
    if pd.isna(valor):
        return 0
    return float(
        str(valor)
        .replace('$', '')
        .replace('.', '')
        .replace(',', '.')
    )

def normalizar_modelo(descripcion):
    """
    Elimina la talla (T4, T6, T10, etc.)
    """
    return re.sub(r'\s*T\d+', '', descripcion).strip()

