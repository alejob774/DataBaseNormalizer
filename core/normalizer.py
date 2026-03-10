# core/normalizer.py
import pandas as pd
import unicodedata

class Normalizer:
    @staticmethod
    def standardize_text(text: any) -> str:
        """
        Normaliza texto para comparaciones:
        - Quita espacios al inicio/final
        - Todo a MAYÚSCULAS
        - Elimina acentos/tildes
        """
        # IMPORTANTE: pd ya está disponible aquí ahora
        if pd.isna(text) or text is None:
            return ""
        
        text = str(text).strip().upper()
        
        # Eliminar tildes/acentos
        text = ''.join(
            c for c in unicodedata.normalize('NFD', text)
            if unicodedata.category(c) != 'Mn'
        )
        return text

    @staticmethod
    def format_excel_date(val: any):
        """Asegura que las fechas sean objetos datetime."""
        if isinstance(val, (pd.Timestamp, pd.Timestamp)):
            return val
        try:
            return pd.to_datetime(val)
        except:
            return val