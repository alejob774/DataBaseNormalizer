
import pandas as pd
from core.normalizer import Normalizer


class Exporter:

    @staticmethod
    def save_to_excel(df: pd.DataFrame, output_path: str):
        """
        Exporta el DataFrame final (formato wide) con orden de columnas fijo
        y tipos de datos correctos.

        Esquema de columnas de salida:
            COUNTRY, CHANNEL, FILE_YEAR, YEAR, CYCLE,
            NAMEPLATE, TRIM, CONCAT, SEGMENT, PARAMETER,
            JAN, FEB, MAR, APR, MAY, JUN, JUL, AUG, SEP, OCT, NOV, DEC
        """
        if df.empty:
            return False

        # 1. Definir orden de columnas del esquema wide
        month_cols = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN',
                      'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']
        fixed_cols = [
            'COUNTRY', 'CHANNEL', 'FILE_YEAR', 'YEAR', 'CYCLE',
            'NAMEPLATE', 'TRIM', 'CONCAT', 'SEGMENT', 'PARAMETER'
        ]
        expected_columns = fixed_cols + month_cols

        # 2. Garantizar que los 12 meses existen (rellenar con 0 si faltan)
        for m in month_cols:
            if m not in df.columns:
                df[m] = 0

        # 3. Filtrar y reordenar solo las columnas esperadas
        final_column_order = [col for col in expected_columns if col in df.columns]
        df = df[final_column_order].copy()

        # 4. Conversión de tipos de datos
        #    Columnas de mes -> numérico
        for m in month_cols:
            if m in df.columns:
                df[m] = pd.to_numeric(df[m], errors='coerce').fillna(0.0)

        #    FILE_YEAR y YEAR como string limpio (sin decimales)
        for col in ['FILE_YEAR', 'YEAR']:
            if col in df.columns:
                df[col] = df[col].astype(str).str.replace(r'\.0$', '', regex=True)

        # 5. Escritura técnica
        with pd.ExcelWriter(output_path, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='Data_Normalized')

            workbook  = writer.book
            worksheet = writer.sheets['Data_Normalized']

            num_format  = workbook.add_format({'num_format': '#,##0.00'})
            text_format = workbook.add_format({'text_wrap': False})

            for i, col in enumerate(df.columns):
                col_len = max(df[col].astype(str).str.len().max(), len(col)) + 2
                if col in month_cols:
                    worksheet.set_column(i, i, col_len, num_format)
                else:
                    worksheet.set_column(i, i, col_len, text_format)

        return True
