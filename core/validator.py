import pandas as pd
from models.error_models import ErrorCollector
from core.normalizer import Normalizer

class Validator:
    def __init__(self, config, mapping, dictionary_dfs):
        self.config = config
        self.mapping = mapping
        self.dict_dfs = dictionary_dfs
        self.errors = ErrorCollector()
        self.norm = Normalizer()

    def validate_all(self, source_df: pd.DataFrame) -> ErrorCollector:
        country_name = self.config.country.upper()
        for sheet in self.dict_dfs:
            self.dict_dfs[sheet].columns = [str(c).strip() for c in self.dict_dfs[sheet].columns]

        df_country = self.dict_dfs[country_name]
        df_params = self.dict_dfs['PARAMETER']
        
        valid_params_map = {self.norm.standardize_text(row[country_name]): row['PARAMETER'] 
                            for _, row in df_params.iterrows() if pd.notna(row.get(country_name))}

        country_map = {}
        for _, row in df_country.iterrows():
            npc_norm = self.norm.standardize_text(row['NAMEPLATE COUNTRY'])
            if npc_norm not in country_map: country_map[npc_norm] = set()
            for col in ['TRIM 1', 'TRIM 2', 'TRIM 3']:
                if col in row and pd.notna(row[col]):
                    country_map[npc_norm].add(self.norm.standardize_text(row[col]))

        for index, row in source_df.iterrows():
            row_num = index + 2
            raw_npc, raw_trim, raw_param = row.get(self.mapping.nameplate_column), row.get(self.mapping.trim_column), row.get(self.mapping.parameter_column)
            # Aqui hace la comparacion para poder encontrar lo que serian las lineas que me son inutiles.
            if pd.isna(raw_npc) or pd.isna(raw_param) or "TOTAL" in str(raw_npc).strip().upper() or "ALL" in str(raw_npc).strip().upper(): continue

            norm_npc, norm_trim, norm_param = self.norm.standardize_text(raw_npc), self.norm.standardize_text(raw_trim), self.norm.standardize_text(raw_param)
            if norm_param not in valid_params_map: continue 
            if norm_npc not in country_map:
                self.errors.add_error(country_name, row_num, self.mapping.nameplate_column, str(raw_npc), f"Model '{raw_npc}' not in dictionary.")
                continue
            if norm_trim not in country_map[norm_npc]:
                self.errors.add_error(country_name, row_num, self.mapping.trim_column, str(raw_trim), f"TRIM '{raw_trim}' not valid for '{raw_npc}'.")
        return self.errors
