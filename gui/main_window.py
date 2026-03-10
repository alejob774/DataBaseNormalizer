from PySide6.QtWidgets import (QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, 
                             QScrollArea, QFrame, QPushButton)
from .drop_zone import DropZone
from .config_panel import ConfigPanel
from .preview_panel import PreviewPanel
from core.table_detector import TableDetector

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Data Transformer Pro")
        self.resize(1180, 620) # Tamaño de la pestaña al ser abierta
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(15)

        # Columna Izquierda: Archivos
        left_frame = QFrame()
        left_layout = QVBoxLayout(left_frame)
        left_layout.setContentsMargins(0,0,0,0)
        self.dict_drop = DropZone("Dictionary System")
        self.data_drop = DropZone("Source Data File")
        left_layout.addWidget(self.dict_drop)
        left_layout.addWidget(self.data_drop)
        left_layout.addStretch()

        # Columna Central: Mapeo y Datos (Más ancha)
        self.preview_panel = PreviewPanel()

        # Columna Derecha: Configuración y Ejecución
        right_frame = QFrame()
        right_frame.setFixedWidth(300)
        right_layout = QVBoxLayout(right_frame)
        right_layout.setContentsMargins(0,0,0,0)
        
        self.config_panel = ConfigPanel()
        right_layout.addWidget(self.config_panel)
        
        self.process_btn = QPushButton("EXECUTE TRANSFORMATION")
        self.process_btn.setFixedHeight(50)
        self.process_btn.setStyleSheet("background-color: #409eff; color: white; font-weight: bold; border-radius: 8px;")
        right_layout.addWidget(self.process_btn)

        main_layout.addWidget(left_frame, 1)
        main_layout.addWidget(self.preview_panel, 2)
        main_layout.addWidget(right_frame, 1)
