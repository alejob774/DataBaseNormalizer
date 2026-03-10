import pandas as pd
from core.normalizer import Normalizer

class Exporter:
    @staticmethod
    def save_to_excel(df: pd.DataFrame, output_path: str):
        """
        Exporta el DataFrame final con orden de columnas fijo y tipos de datos correctos.
        """
        if df.empty:
            return False

        # 1. Definir orden de columnas fijas
        fixed_columns = [
            'Country', 'Channel', 'Year', 'Cycle', 
            'NAMEPLATE', 'TRIM', 'CONCAT', 'SEGMENT', 'PARAMETER'
        ]
        
        # 2. Identificar columnas de fechas (todas las que no son fijas)
        date_columns = [col for col in df.columns if col not in fixed_columns]
        
        # 3. Asegurar orden total: fijas + fechas
        final_column_order = fixed_columns + date_columns
        df = df[final_column_order]

        # 4. Conversión de tipos de datos
        # Convertir columnas de fechas a datetime real de Excel
        for col in date_columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(df[col])
            # Intentar convertir el nombre de la columna a fecha si es posible
            # y los valores de la columna a numérico (floats/ints para análisis)
            try:
                df[col] = pd.to_numeric(df[col])
            except:
                pass

        # 5. Escritura técnica
        with pd.ExcelWriter(output_path, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='Data_Normalized')
            
            # Formateo básico (opcional: auto-ajuste de columnas)
            workbook = writer.book
            worksheet = writer.sheets['Data_Normalized']
            
            # Formato de fecha para las celdas (si los valores son datetimes)
            # date_format = workbook.add_format({'num_format': 'yyyy-mm-dd'})
            
            for i, col in enumerate(df.columns):
                column_len = max(df[col].astype(str).str.len().max(), len(col)) + 2
                worksheet.set_column(i, i, column_len)

        return True
