from dataclasses import dataclass
import pandas as pd
from typing import Dict, Optional

@dataclass
class AppConfig:
    """Almacena la configuración seleccionada en el GUI"""
    country: str
    year: str
    period: str
    stage: str
    language: str  # 'ES' / 'EN'
    channel: str = "All Channels"

    @property
    def cycle(self) -> str:
        return f"{self.period} {self.stage}"

@dataclass
class MappingConfig:
    """Define qué columnas del Excel origen mapean a los conceptos base"""
    nameplate_column: str
    trim_column: str
    parameter_column: str

@dataclass
class ProcessingData:
    """Contenedor de DataFrames para evitar lecturas repetidas"""
    dictionary_df_dict: Dict[str, pd.DataFrame]  # Todas las hojas del BASE
    source_df: pd.DataFrame                      # Hoja seleccionada del país
    start_row: int                               # Fila donde inicia la tabla real
