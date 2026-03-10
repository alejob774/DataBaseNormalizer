import pandas as pd
import numpy as np


class TableDetector:

    KEYWORDS = ["NAMEPLATE", "VALIDO/DISPONIBLE", "FAMILY", "FAMILIA", "MODEL", "KMAT", "SEGMENTO", "SEGMENT", "FACTOR", "RATIO", "VERSION SIMPLE", "MODELO", "VIGENCIA", "ORDEN", "MODELO / VERSION", "VISIBLE"]

    @staticmethod
    def find_start_row(df: pd.DataFrame) -> int:
        """
        1️⃣ Primero detecta la fila con mayor densidad de strings.
        2️⃣ Si no es suficientemente representativa, busca por keywords.
        """

        search_limit = min(50, len(df))

        max_density = 0
        best_row_index = None

        # ---------------------------------
        # 2️⃣ Fallback: buscar por keywords
        # ---------------------------------
        for i in range(search_limit):
            row = df.iloc[i]

            row_str = " ".join(
                str(x).upper()
                for x in row.values
                if pd.notna(x)
            )

            matched_keywords = [
                keyword for keyword in TableDetector.KEYWORDS
                if keyword in row_str
            ]

            if len(set(matched_keywords)) >= 3:
                return i

        # ---------------------------------
        # 1️⃣ Detectar por densidad
        # ---------------------------------
        for i in range(search_limit):
            row = df.iloc[i]
            non_null = row.dropna()

            if len(non_null) == 0:
                continue

            string_count = sum(
                isinstance(val, str) and val.strip() != ""
                for val in non_null
            )

            density = string_count / len(non_null)

            if density > max_density:
                max_density = density
                best_row_index = i

        # Validación mínima de header razonable
        if best_row_index is not None:
            row = df.iloc[best_row_index].dropna()
            string_count = sum(
                isinstance(val, str) and val.strip() != ""
                for val in row
            )

            if string_count >= 2 and max_density >= 0.4:
                return best_row_index

        # ---------------------------------
        # 3️⃣ Fallback final
        # ---------------------------------
        return 0

    @staticmethod
    def get_clean_table(df: pd.DataFrame, start_row: int) -> pd.DataFrame:
        """
        Limpia la tabla desde start_row:
        - Asigna header
        - Elimina fila header
        - Limpia valores inválidos
        """

        df_clean = df.iloc[start_row:].copy()

        # Asignar encabezados
        df_clean.columns = df_clean.iloc[0]

        # Eliminar fila header
        df_clean = df_clean.iloc[1:].reset_index(drop=True)

        # Limpiar errores Excel
        df_clean = df_clean.replace(
            [np.inf, -np.inf, "#N/A", "#REF!", "#VALUE!", "#DIV/0!"],
            np.nan
        )

        return df_clean
