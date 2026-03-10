import sys
import pandas as pd
from PySide6.QtWidgets import QApplication, QFileDialog
from gui.main_window import MainWindow
from gui.sheet_selector import SheetSelectorDialog
from gui.dialogs import ErrorReportDialog, NativeDialogs
from core.validator import Validator
from core.mapper import Mapper
from core.table_detector import TableDetector

class AppConfig:
    def __init__(self, country, channel, year, period, stage):
        self.country, self.channel, self.year, self.period, self.stage = country, channel, year, period, stage

class MappingConfig:
    def __init__(self, nameplate, trim, parameter):
        self.nameplate_column, self.trim_column, self.parameter_column = nameplate, trim, parameter

class Controller:
    def __init__(self):
        self.view = MainWindow()
        self.dict_data, self.source_path, self.selected_sheet, self.source_df_raw = None, None, None, None
        
        self.view.dict_drop.file_dropped.connect(self.load_dictionary)
        self.view.data_drop.file_dropped.connect(self.load_source_data)
        self.view.process_btn.clicked.connect(self.run_process)
        self.view.config_panel.spin_start_row.valueChanged.connect(self.update_columns_on_row_change)
        self.view.show()

    def load_dictionary(self, path):
        try:
            self.dict_data = pd.read_excel(path, sheet_name=None)
            excluded = ["PARAMETER", "SEGMENT", "RESUMEN", "INSTRUCCIONES"]
            countries = [sheet for sheet in self.dict_data.keys() if sheet.upper() not in excluded]
            self.view.config_panel.set_countries(sorted(countries))
            self.view.dict_drop.status_label.setText("Loaded ✅")
        except Exception as e: NativeDialogs.show_error("Error", str(e))

    def load_source_data(self, path):
        try:
            xls = pd.ExcelFile(path)
            selector = SheetSelectorDialog(xls.sheet_names)
            if selector.exec():
                self.source_path, self.selected_sheet = path, selector.get_selected_sheet()
                df_full = pd.read_excel(path, sheet_name=self.selected_sheet, header=None)
                detected_row = TableDetector.find_start_row(df_full)
                # Al cambiar el SpinBox se disparará update_columns_on_row_change automáticamente
                self.view.config_panel.spin_start_row.setValue(detected_row + 1)
                self.view.data_drop.status_label.setText(f"{self.selected_sheet} ✅")
        except Exception as e: NativeDialogs.show_error("Error", str(e))

    # Dentro de la clase Controller en app.py
    def update_columns_on_row_change(self):
        if not self.source_path or not self.selected_sheet: return
        try:
            row_idx = self.view.config_panel.spin_start_row.value() - 1
            df = pd.read_excel(self.source_path, sheet_name=self.selected_sheet, header=None)
        
            # 1. Obtener la fila literal para el preview
            header_row = df.iloc[row_idx].fillna("").values.tolist()
            # LLAMADA AL MÉTODO CORREGIDO
            self.view.preview_panel.display_headers(header_row) 
        
            # 2. Limpiar la tabla y llenar combos de mapeo
            self.source_df_raw = TableDetector.get_clean_table(df, row_idx)
            cols = [str(c) for c in self.source_df_raw.columns]
            # LLAMADA AL OTRO MÉTODO DEL PREVIEW PANEL
            self.view.preview_panel.fill_mapping_combos(cols) 
        
        except Exception as e: 
            print(f"Preview error: {e}")

    def run_process(self):
        if not self.dict_data or self.source_df_raw is None:
            NativeDialogs.show_error("Warning", "Load files first.")
            return
        try:
            config = AppConfig(self.view.config_panel.combo_country.currentText(), "ALL CHANNELS", 
                               self.view.config_panel.input_year.text(), self.view.config_panel.combo_period.currentText(), 
                               self.view.config_panel.combo_stage.currentText())
            mapping = MappingConfig(
        		       self.view.preview_panel.map_nameplate.currentText(), 
        		       self.view.preview_panel.map_trim.currentText(), 
        		       self.view.preview_panel.map_parameter.currentText()
    			       )
            validator = Validator(config, mapping, self.dict_data)
            errors = validator.validate_all(self.source_df_raw)
            if errors.has_errors():
                ErrorReportDialog(errors.get_report()).exec()
                return
            mapper = Mapper(config, mapping, self.dict_data)
            final_df = mapper.process_transformation(self.source_df_raw)
            save_path, _ = QFileDialog.getSaveFileName(self.view, "Save File", f"OUTPUT_{config.country}.xlsx", "Excel (*.xlsx)")
            if save_path:
                final_df.to_excel(save_path, index=False)
                NativeDialogs.show_success()
        except Exception as e: NativeDialogs.show_error("Process Error", str(e))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ctrl = Controller()
    sys.exit(app.exec())
