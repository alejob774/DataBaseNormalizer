from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QComboBox, QLineEdit, QSpinBox, QGroupBox
from PySide6.QtCore import Qt

class ConfigPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        self.main_layout.setSpacing(25) # Espacio amplio para evitar solapamientos
        
        self.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 1px solid #dcdfe6;
                border-radius: 8px;
                margin-top: 20px;
                padding-top: 25px; /* Espacio para que el título no pise el contenido */
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                left: 10px;
                padding: 0 8px;
                color: #2c3e50;
            }
            QLabel { color: #5a5e66; margin-top: 5px; }
            QComboBox, QLineEdit, QSpinBox {
                border: 1px solid #dcdfe6;
                border-radius: 4px;
                padding: 6px;
                min-height: 28px;
            }
        """)
        self.init_ui()

    def create_field(self, label_text, widget):
        container = QVBoxLayout()
        container.setSpacing(4)
        container.addWidget(QLabel(label_text))
        container.addWidget(widget)
        return container

    def init_ui(self):
        # Grupo 1: Project
        group_proj = QGroupBox("PROJECT SETTINGS")
        layout_proj = QVBoxLayout(group_proj)
        self.combo_country = QComboBox()
        self.input_year = QLineEdit("")
        self.spin_start_row = QSpinBox()
        self.spin_start_row.setRange(1, 1000)
        
        layout_proj.addLayout(self.create_field("Target Country:", self.combo_country))
        layout_proj.addLayout(self.create_field("Target Year:", self.input_year))
        layout_proj.addLayout(self.create_field("Header Row Index:", self.spin_start_row))

        # Grupo 2: Cycle
        group_cycle = QGroupBox("CYCLE & STAGE")
        layout_cycle = QVBoxLayout(group_cycle)
        self.combo_period = QComboBox()
        self.combo_period.addItems([f"{i}+{12-i}" for i in range(12)])
        self.combo_stage = QComboBox()
        self.combo_stage.addItems(["Free", "Constraint", "Closing"])
        
        layout_cycle.addLayout(self.create_field("Period:", self.combo_period))
        layout_cycle.addLayout(self.create_field("Stage:", self.combo_stage))

        self.main_layout.addWidget(group_proj)
        self.main_layout.addWidget(group_cycle)
        self.main_layout.addStretch()

    # --- MÉTODO PARA RECARGAR PAÍSES ---
    def set_countries(self, country_list):
        self.combo_country.clear()
        self.combo_country.addItems(country_list)