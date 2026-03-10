import pandas as pd
import re
from core.normalizer import Normalizer

class Mapper:
    def __init__(self, config, mapping, dictionary_dfs):
        self.config = config
        self.mapping = mapping
        self.dict_dfs = dictionary_dfs
        self.norm = Normalizer()

    def is_date_column(self, col_name):
        dt = pd.to_datetime(col_name, errors='coerce')
        if pd.notnull(dt):
            return dt

        col_str = str(col_name).lower().strip()
        meses = r'(ene|feb|mar|abr|may|jun|jul|ago|sep|oct|nov|dic|jan|apr|aug|dec)'
        pattern = re.compile(rf'{meses}[-/\s]?(\d{{2,4}})')
        match = pattern.search(col_str)
        if match:
            replacements = {'ene': 'jan', 'abr': 'apr', 'ago': 'aug', 'dic': 'dec'}
            for sp, en in replacements.items():
                col_str = col_str.replace(sp, en)
            return pd.to_datetime(col_str, errors='coerce', format='%b-%y')

        return None

    def process_transformation(self, source_df: pd.DataFrame) -> pd.DataFrame:
        country_selected = self.config.country

        # Normalizar nombres de columnas en todos los diccionarios
        for sheet in self.dict_dfs:
            self.dict_dfs[sheet].columns = [str(c).strip() for c in self.dict_dfs[sheet].columns]

        df_country = self.dict_dfs[country_selected]
        df_params = self.dict_dfs['PARAMETER']
        df_segmento = self.dict_dfs['SEGMENT']

        # Columna de parámetro específica del país
        param_col_in_dict = next(
            (c for c in df_params.columns if c.upper() == country_selected.upper()),
            None
        )
        if not param_col_in_dict:
            return pd.DataFrame()

        # Lookup de parámetros normalizados
        param_lookup = {
            self.norm.standardize_text(row[param_col_in_dict]): str(row['PARAMETER']).upper()
            for _, row in df_params.iterrows()
            if pd.notna(row.get(param_col_in_dict))
        }

        # === Lookup país + TRIM normalizado -> val_data ===
        # Solo usamos TRIM 1/2/3 como "alias" que apuntan al TRIM canónico de la fila.
        country_lookup = {}

        for _, row in df_country.iterrows():
            npc_norm = self.norm.standardize_text(row['NAMEPLATE COUNTRY'])
            val_data = {
                'NAMEPLATE': str(row['NAMEPLATE']).upper(),
                'TRIM': str(row['TRIM']).upper(),
                'CONCAT': str(row['CONCAT']).upper()
            }

            # Alias de TRIM (TRIM 1/2/3)
            for col in ['TRIM 1', 'TRIM 2', 'TRIM 3']:
                if col in df_country.columns and pd.notna(row.get(col)):
                    trim_norm = self.norm.standardize_text(row[col])
                    key = (npc_norm, trim_norm)

                    # Si el mismo (país, trim) apunta a dos filas distintas -> ambigüedad
                    # En ese caso, mejor no mapear en silencio: dejamos la primera
                    # y podrías loguear/validar si lo necesitas.
                    if key not in country_lookup:
                        country_lookup[key] = val_data

        segmento_lookup = df_segmento.set_index('NAMEPLATE')['SEGMENT'].to_dict()

        mapped_keys = [
            self.mapping.nameplate_column,
            self.mapping.trim_column,
            self.mapping.parameter_column
        ]

        # Mapear columnas de fecha (cada columna de origen -> UNA columna normalizada)
        date_map = {}
        for col in source_df.columns:
            if col not in mapped_keys:
                dt = self.is_date_column(col)
                if dt:
                    date_map[col] = dt.strftime('%b-%y').upper()

        output_rows = []

        # Pre-filtrado de filas válidas (sin perder el índice)
        valid_mask = (
            source_df[self.mapping.nameplate_column].notna()
            & source_df[self.mapping.parameter_column].notna()
        )
        source_valid = source_df[valid_mask].copy()

        for idx, row in source_valid.iterrows():
            raw_npc = row.get(self.mapping.nameplate_column)
            raw_trim = row.get(self.mapping.trim_column)
            raw_param = row.get(self.mapping.parameter_column)

            norm_npc = self.norm.standardize_text(raw_npc)
            norm_trim = self.norm.standardize_text(raw_trim)
            norm_param = self.norm.standardize_text(raw_param)

            if norm_param not in param_lookup:
                continue

            base_data = country_lookup.get((norm_npc, norm_trim))
            if not base_data:
                # No hay match exacto (país, trim normalizado) -> no inventamos nada.
                continue

            new_row = {
                'COUNTRY': country_selected.upper(),
                'CHANNEL': "ALL CHANNELS",
                'YEAR': str(self.config.year).upper(),
                'CYCLE': f"{self.config.period} {self.config.stage}".upper(),
                'NAMEPLATE': base_data['NAMEPLATE'],
                'TRIM': base_data['TRIM'],
                'CONCAT': base_data['CONCAT'],
                'SEGMENT': str(segmento_lookup.get(base_data['NAMEPLATE'], "OTROS")).upper(),
                'PARAMETER': param_lookup[norm_param],
                # Campo opcional para trazabilidad: de qué fila del origen viene
                '_SRC_INDEX': idx
            }

            # Cada columna de fecha del origen va a una sola columna normalizada
            for orig_col, formatted_col in date_map.items():
                val = row[orig_col]
                try:
                    new_row[formatted_col] = float(val) if pd.notna(val) else 0.0
                except Exception:
                    new_row[formatted_col] = 0.0

            output_rows.append(new_row)

        if not output_rows:
            return pd.DataFrame()

        final_df = pd.DataFrame(output_rows)

        # --- Control de calidad básico: ninguna fila se duplica ---
        # Cada _SRC_INDEX debe aparecer a lo sumo una vez.
        if final_df['_SRC_INDEX'].duplicated().any():
            # Si quieres, aquí puedes lanzar una excepción o loguear para depurar.
            raise ValueError("Hay filas de origen mapeadas más de una vez (_SRC_INDEX duplicado).")

        fixed_cols = [
            'COUNTRY', 'CHANNEL', 'YEAR', 'CYCLE',
            'NAMEPLATE', 'TRIM', 'CONCAT', 'SEGMENT', 'PARAMETER'
        ]
        date_cols = list(dict.fromkeys(date_map.values()))

        # Hacemos el groupby solo en las columnas finales, sin _SRC_INDEX
        grouped = (
            final_df
            .drop(columns=['_SRC_INDEX'])
            .groupby(fixed_cols, as_index=False)[date_cols]
            .sum()
        )

        return grouped[fixed_cols + date_cols]
