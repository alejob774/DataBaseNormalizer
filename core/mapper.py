import pandas as pd
import re
from datetime import date, datetime
from typing import Optional
from core.normalizer import Normalizer

class Mapper:
    MONTH_TOKEN_TO_NUMBER = {
        'ene': 1, 'jan': 1,
        'feb': 2,
        'mar': 3,
        'abr': 4, 'apr': 4,
        'may': 5,
        'jun': 6,
        'jul': 7,
        'ago': 8, 'aug': 8,
        'sep': 9,
        'oct': 10,
        'nov': 11,
        'dic': 12, 'dec': 12,
    }
    MONTH_NUMBER_TO_ABBR = {
        1: 'JAN', 2: 'FEB', 3: 'MAR', 4: 'APR',
        5: 'MAY', 6: 'JUN', 7: 'JUL', 8: 'AUG',
        9: 'SEP', 10: 'OCT', 11: 'NOV', 12: 'DEC'
    }
    VALID_YEAR_MIN = 1900
    VALID_YEAR_MAX = 2100
    MONTH_YEAR_PATTERN = re.compile(
        r'(?<![A-Za-z])(?P<month>ene|feb|mar|abr|may|jun|jul|ago|sep|oct|nov|dic|jan|apr|aug|dec)[-/\s]?(?P<year>\d{2,4})(?!\d)',
        re.IGNORECASE
    )

    def __init__(self, config, mapping, dictionary_dfs):
        self.config = config
        self.mapping = mapping
        # IMPORTANTE: se hace una copia profunda de cada DataFrame del diccionario
        # para evitar que las mutaciones internas (normalización de columnas, etc.)
        # afecten al objeto original y contaminen procesos posteriores.
        self.dict_dfs = {sheet: df.copy() for sheet, df in dictionary_dfs.items()}
        self.norm = Normalizer()

    @staticmethod
    def _normalize_two_digit_year(year: int) -> int:
        """Replica la convención estándar de %y: 00-68 -> 2000-2068, 69-99 -> 1969-1999."""
        return 2000 + year if year <= 68 else 1900 + year

    def _normalize_month_timestamp(self, dt) -> Optional[pd.Timestamp]:
        if dt is None or pd.isna(dt):
            return None

        try:
            year = int(dt.year)
            month = int(dt.month)
        except Exception:
            return None

        if not (self.VALID_YEAR_MIN <= year <= self.VALID_YEAR_MAX):
            return None

        try:
            return pd.Timestamp(year=year, month=month, day=1)
        except Exception:
            return None

    def _format_month_label(self, dt) -> Optional[str]:
        normalized_dt = self._normalize_month_timestamp(dt)
        if normalized_dt is None:
            return None

        month_abbr = self.MONTH_NUMBER_TO_ABBR.get(int(normalized_dt.month))
        if not month_abbr:
            return None

        return f"{month_abbr}-{normalized_dt.year % 100:02d}"

    def is_date_column(self, col_name):
        """
        Intenta interpretar el nombre de la columna como fecha mensual.
        Soporta:
        - Objetos fecha/datetime reales.
        - Abreviaturas de mes en español/inglés tipo 'ene-24', 'feb/2023', etc.
        - Fechas explícitas parseables por pandas (ej. '2024-01-01').

        Importante:
        - Evita usar strftime sobre años < 1900 (rompe en Windows).
        - Evita que encabezados puramente numéricos se interpreten como fechas Unix/nanosegundos.
        """
        if col_name is None or pd.isna(col_name):
            return None

        if isinstance(col_name, (pd.Timestamp, datetime, date)):
            return self._normalize_month_timestamp(pd.Timestamp(col_name))

        col_str = str(col_name).strip()
        if not col_str:
            return None

        # 1) Heurística controlada por texto (mes-año)
        match = self.MONTH_YEAR_PATTERN.search(col_str.lower())
        if match:
            month_token = match.group('month').lower()
            month = self.MONTH_TOKEN_TO_NUMBER.get(month_token)
            year_str = match.group('year')
            year = int(year_str)
            if len(year_str) == 2:
                year = self._normalize_two_digit_year(year)

            try:
                return self._normalize_month_timestamp(pd.Timestamp(year=year, month=month, day=1))
            except Exception:
                return None

        # 2) Intento directo, pero solo para strings con pinta real de fecha.
        #    Así evitamos que valores numéricos como 24 o 202401 se conviertan
        #    en timestamps relativos a 1970.
        if re.search(r'[A-Za-z]', col_str) or any(sep in col_str for sep in ('-', '/', '.')):
            dt = pd.to_datetime(col_str, errors='coerce')
            if pd.notnull(dt):
                return self._normalize_month_timestamp(dt)

        return None

    def process_transformation(self, source_df: pd.DataFrame) -> pd.DataFrame:
        country_selected = self.config.country

        # Normalizar nombres de columnas en todos los diccionarios
        for sheet in self.dict_dfs:
            self.dict_dfs[sheet].columns = [str(c).strip() for c in self.dict_dfs[sheet].columns]

        df_country  = self.dict_dfs[country_selected]
        df_params   = self.dict_dfs['PARAMETER']
        df_segmento = self.dict_dfs['SEGMENT']

        # Columna de parámetro específica del país en la hoja PARAMETER
        param_col_in_dict = next(
            (c for c in df_params.columns if c.upper() == country_selected.upper()),
            None
        )
        if not param_col_in_dict:
            return pd.DataFrame()

        # ---------------------------------------------------------
        # Lookup de parámetros normalizados
        # key:   parámetro del país normalizado
        # value: lista de parámetros normalizados (columna PARAMETER)
        # ---------------------------------------------------------
        param_lookup = {}
        for _, row in df_params.iterrows():
            raw_country_param = row.get(param_col_in_dict)
            if pd.isna(raw_country_param):
                continue
            key   = self.norm.standardize_text(raw_country_param)
            value = str(row['PARAMETER']).upper()
            if key not in param_lookup:
                param_lookup[key] = []
            if value not in param_lookup[key]:
                param_lookup[key].append(value)

        # ---------------------------------------------------------
        # Lookup (NAMEPLATE COUNTRY normalizado, TRIM-alias normalizado) -> datos canónicos
        # Usamos TRIM 1/2/3 como alias que apuntan al TRIM canónico de la fila.
        # ---------------------------------------------------------
        country_lookup = {}
        for _, row in df_country.iterrows():
            npc_norm = self.norm.standardize_text(row['NAMEPLATE COUNTRY'])
            val_data = {
                'NAMEPLATE': str(row['NAMEPLATE']).upper(),
                'TRIM':      str(row['TRIM']).upper(),
                'CONCAT':    str(row['CONCAT']).upper()
            }
            # Alias de TRIM (TRIM 1/2/3)
            for col in ['TRIM 1', 'TRIM 2', 'TRIM 3']:
                if col in df_country.columns and pd.notna(row.get(col)):
                    trim_norm = self.norm.standardize_text(row[col])
                    key = (npc_norm, trim_norm)
                    # Si el mismo (país, trim) apunta a dos filas distintas -> ambigüedad.
                    # Dejamos la primera definición encontrada.
                    if key not in country_lookup:
                        country_lookup[key] = val_data

        segmento_lookup = df_segmento.set_index('NAMEPLATE')['SEGMENT'].to_dict()

        mapped_keys = [
            self.mapping.nameplate_column,
            self.mapping.trim_column,
            self.mapping.parameter_column
        ]

        # ---------------------------------------------------------
        # Mapear columnas de fecha (cada columna de origen -> UNA columna normalizada)
        # ---------------------------------------------------------
        date_map = {}
        for col in source_df.columns:
            if col not in mapped_keys:
                dt = self.is_date_column(col)
                if dt is not None and pd.notnull(dt):
                    formatted_label = self._format_month_label(dt)
                    if formatted_label:
                        date_map[col] = formatted_label

        output_rows = []

        # Pre-filtrado de filas válidas (sin perder el índice)
        valid_mask = (
            source_df[self.mapping.nameplate_column].notna()
            & source_df[self.mapping.parameter_column].notna()
        )
        source_valid = source_df[valid_mask].copy()

        for idx, row in source_valid.iterrows():
            raw_npc   = row.get(self.mapping.nameplate_column)
            raw_trim  = row.get(self.mapping.trim_column)
            raw_param = row.get(self.mapping.parameter_column)

            norm_npc   = self.norm.standardize_text(raw_npc)
            norm_trim  = self.norm.standardize_text(raw_trim)
            norm_param = self.norm.standardize_text(raw_param)

            # Si el parámetro no existe en el diccionario, saltamos la fila
            if norm_param not in param_lookup:
                continue

            base_data = country_lookup.get((norm_npc, norm_trim))
            if not base_data:
                # No hay match exacto (país, trim normalizado) -> no inventamos nada.
                continue

            # Puede haber 1 o N parámetros normalizados para el mismo norm_param
            for normalized_param in param_lookup[norm_param]:
                new_row = {
                    'COUNTRY':    country_selected.upper(),
                    'CHANNEL':    "ALL CHANNELS",
                    'FILE_YEAR':  str(self.config.year).upper(),
                    'CYCLE':      f"{self.config.period} {self.config.stage}".upper(),
                    'NAMEPLATE':  base_data['NAMEPLATE'],
                    'TRIM':       base_data['TRIM'],
                    'CONCAT':     base_data['CONCAT'],
                    'SEGMENT':    str(segmento_lookup.get(base_data['NAMEPLATE'], "OTROS")).upper(),
                    'PARAMETER':  normalized_param,
                    '_SRC_INDEX': idx
                }

                # Cada columna de fecha del origen va a la misma columna normalizada
                for orig_col, formatted_col in date_map.items():
                    val = row.get(orig_col)
                    try:
                        new_row[formatted_col] = float(val) if pd.notna(val) else 0.0
                    except Exception:
                        new_row[formatted_col] = 0.0

                output_rows.append(new_row)

        if not output_rows:
            return pd.DataFrame()

        final_df = pd.DataFrame(output_rows)

        # ---------------------------------------------------------
        # Orden y agregación final (formato wide)
        # ---------------------------------------------------------
        fixed_cols = [
            'COUNTRY', 'CHANNEL', 'FILE_YEAR', 'CYCLE',
            'NAMEPLATE', 'TRIM', 'CONCAT', 'SEGMENT', 'PARAMETER'
        ]
        date_cols = list(dict.fromkeys(date_map.values()))

        # Groupby sin _SRC_INDEX
        grouped = (
            final_df
            .drop(columns=['_SRC_INDEX'])
            .groupby(fixed_cols, as_index=False)[date_cols]
            .sum()
        )

        # ---------------------------------------------------------
        # Paso 1 – MELT: wide -> long para poder separar año y mes
        # ---------------------------------------------------------
        melted = grouped.melt(
            id_vars=fixed_cols,
            value_vars=date_cols,
            var_name='_MONTH_LABEL',   # ej. 'JAN-24'
            value_name='VALUE'
        )

        # Parsear el label (ej. 'JAN-24') para obtener año y abreviación de mes
        _dt = pd.to_datetime(melted['_MONTH_LABEL'], format='%b-%y', errors='coerce')
        melted['_MONTH_SHORT'] = _dt.dt.month.map(self.MONTH_NUMBER_TO_ABBR)    # ej. 'JAN'

        # pd.to_numeric garantiza dtype float/int independiente de la versión de pandas
        # (evita que Int64 quede como object cuando hay NaT en _dt)
        melted['YEAR'] = pd.to_numeric(_dt.dt.year, errors='coerce')

        # =========================================================
        # FILTRO DE AÑO MÍNIMO
        # Se descartan todas las filas cuyo año de mes sea anterior
        # a 2020. Cambiar el valor 2020 si se requiere otro límite.
        # Las filas cuyo label de mes no pudo parsearse (YEAR == NaN)
        # también quedan excluidas automáticamente por esta condición.
        # =========================================================
        melted = melted[melted['YEAR'] >= 2020]

        # Convertir YEAR a string limpio después del filtro (ej. 2024.0 -> '2024')
        melted['YEAR'] = melted['YEAR'].astype('Int64').astype(str).str.replace('<NA>', '', regex=False)

        # ---------------------------------------------------------
        # Paso 2 – PIVOT: long -> wide con abreviaciones de mes como columnas
        # Índice = columnas fijas + YEAR  |  columnas = JAN…DEC  |  valores = VALUE
        # ---------------------------------------------------------
        pivot_index = fixed_cols + ['YEAR']
        pivoted = melted.pivot_table(
            index=pivot_index,
            columns='_MONTH_SHORT',
            values='VALUE',
            aggfunc='sum',
            fill_value=0
        ).reset_index()
        pivoted.columns.name = None

        # Garantizar que los 12 meses existen aunque no haya datos
        month_order = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN',
                       'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']
        for m in month_order:
            if m not in pivoted.columns:
                pivoted[m] = 0

        # ---------------------------------------------------------
        # Orden de columnas del archivo de salida
        # ---------------------------------------------------------
        output_cols = [
            'COUNTRY', 'CHANNEL', 'FILE_YEAR', 'YEAR', 'CYCLE',
            'NAMEPLATE', 'TRIM', 'CONCAT', 'SEGMENT', 'PARAMETER'
        ] + month_order

        return pivoted[output_cols]
