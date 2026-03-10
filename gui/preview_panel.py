from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QComboBox, QTableWidget, QHeaderView, QGroupBox, 
                             QTableWidgetItem)
from PySide6.QtCore import Qt

class PreviewPanel(QWidget):
    def __init__(self):
        super().__init__()
        # Configuración general del layout principal
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.layout.setSpacing(15)

        # --- SECCIÓN DE MAPEO DE COLUMNAS ---
        self.map_group = QGroupBox("COLUMN MAPPING")
        self.map_group.setStyleSheet("""
            QGroupBox { 
                font-weight: bold; 
                border: 1px solid #dcdfe6; 
                border-radius: 8px; 
                margin-top: 15px; 
                padding-top: 25px; 
                background: #fdfdfd; 
            }
            QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 5px; }
        """)
        map_h_layout = QHBoxLayout(self.map_group)
        
        # Inicialización de los desplegables (ComboBoxes)
        self.map_nameplate = QComboBox()
        self.map_trim = QComboBox()
        self.map_parameter = QComboBox()

        # Creación dinámica de etiquetas y layouts para los combos
        for label, combo in [("Model:", self.map_nameplate), 
                             ("Trim:", self.map_trim), 
                             ("Param:", self.map_parameter)]:
            v_box = QVBoxLayout()
            v_box.addWidget(QLabel(label))
            v_box.addWidget(combo)
            map_h_layout.addLayout(v_box)

        self.layout.addWidget(self.map_group)

        # --- SECCIÓN DE VISTA PREVIA (TABLA) ---
        self.preview_group = QGroupBox("DETECTED HEADER PREVIEW")
        self.preview_group.setStyleSheet("""
            QGroupBox { 
                font-weight: bold; 
                border: 1px solid #dcdfe6; 
                border-radius: 8px; 
                margin-top: 10px; 
                padding-top: 25px; 
            }
        """)
        preview_layout = QVBoxLayout(self.preview_group)
        
        self.table = QTableWidget()
        self.table.setRowCount(1)
        self.table.setFixedHeight(80) 
        self.table.verticalHeader().setVisible(False)
        # Hacemos que la tabla sea de solo lectura para el usuario
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        preview_layout.addWidget(self.table)
        self.layout.addWidget(self.preview_group)

    def fill_mapping_combos(self, columns):
        """
        Llena los combos con las columnas detectadas y realiza una búsqueda lineal
        para auto-seleccionar el valor por defecto basado en alias comunes.
        """
        # Definimos "keywords" o alias para cada campo. 
        # Si la columna contiene alguna de estas palabras, se seleccionará automáticamente.
        default_mappings = {
            self.map_nameplate: ["familia", "modelo"],
            self.map_trim: ["version simple", "versión", "modelo / versión", "vigencia"],
            self.map_parameter: ["ratio", "factor"]
        }

        # Iteramos sobre cada combo y su lista de alias
        for combo, keywords in default_mappings.items():
            combo.blockSignals(True)  # Bloqueamos señales para evitar disparar eventos durante la carga
            combo.clear()
            combo.addItems(columns)
            
            # --- Lógica de Búsqueda Lineal para Selección Automática ---
            found_index = -1
            for i, col_name in enumerate(columns):
                # Convertimos a minúsculas para una comparación insensible a mayúsculas
                col_lower = col_name.lower()
                
                # Verificamos si alguna keyword está dentro del nombre de la columna
                if any(key in col_lower for key in keywords):
                    found_index = i
                    break # Detenemos la búsqueda al encontrar la primera coincidencia
            
            # Si encontramos una coincidencia, ajustamos el índice actual del combo
            if found_index != -1:
                combo.setCurrentIndex(found_index)
            else:
                # Si no hay coincidencia, podemos dejarlo en el primero o en blanco (-1)
                combo.setCurrentIndex(0) if columns else combo.setCurrentIndex(-1)
                
            combo.blockSignals(False)

    def display_headers(self, headers):
        """
        Muestra los nombres de las columnas en la tabla de vista previa.
        """
        self.table.setColumnCount(len(headers))
        # Generamos etiquetas simples para las cabeceras de la tabla
        self.table.setHorizontalHeaderLabels([f"Col {i+1}" for i in range(len(headers))])
        
        for i, h in enumerate(headers):
            item = QTableWidgetItem(str(h))
            # Centramos el texto para mejor estética
            item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(0, i, item)
            
        # Ajustamos el tamaño de las columnas al contenido para que sea legible
        self.table.resizeColumnsToContents()
        # Hacemos que las columnas ocupen el espacio disponible de forma equitativa si es posible
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
