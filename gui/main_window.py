import json
import os
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QScrollArea, QFrame, QPushButton, QMessageBox,
    QDialog, QLabel
)
from PySide6.QtCore import Qt
from .drop_zone import DropZone
from .config_panel import ConfigPanel
from .preview_panel import PreviewPanel
from core.table_detector import TableDetector

# ---------------------------------------------------------------------------
# Path to the customizable info messages file.
# Place info_messages.json in the same folder as this file.
# To edit messages, open info_messages.json and modify the "main_window" key.
# ---------------------------------------------------------------------------
INFO_FILE = os.path.join(os.path.dirname(__file__), "info_messages.json")


def _load_info_message(key: str) -> dict:
    """
    Load a specific info message block from info_messages.json.

    Args:
        key (str): The top-level key in the JSON (e.g. "main_window").

    Returns:
        dict: A dict with "title" and "message" keys.
    """
    try:
        with open(INFO_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data.get(key, {"title": "Info", "message": "No information available."})
    except FileNotFoundError:
        return {"title": "Info", "message": f"Info file not found:\n{INFO_FILE}"}
    except json.JSONDecodeError as e:
        return {"title": "Error", "message": f"Could not parse info_messages.json:\n{e}"}


# ---------------------------------------------------------------------------
# Shared stylesheet for the circular info button (ⓘ).
# ---------------------------------------------------------------------------
INFO_BTN_STYLE = """
    QPushButton {
        background-color: transparent;
        color: #409eff;
        border: 1.5px solid #409eff;
        border-radius: 12px;
        font-size: 13px;
        font-weight: bold;
        padding: 0px;
    }
    QPushButton:hover {
        background-color: #409eff;
        color: white;
    }
    QPushButton:pressed {
        background-color: #2980d9;
        color: white;
    }
"""


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Data Transformer Pro")
        self.resize(1180, 620)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Outer vertical layout: thin top bar + main content area
        outer_layout = QVBoxLayout(central_widget)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.setSpacing(0)

        # ── Top bar: holds the ⓘ info button aligned to the top-right ───────
        top_bar = QHBoxLayout()
        top_bar.setContentsMargins(15, 8, 15, 0)
        top_bar.addStretch()  # Push the button to the right

        self.info_btn = QPushButton("ⓘ")
        self.info_btn.setFixedSize(24, 24)
        self.info_btn.setToolTip("How to use Data Transformer Pro")
        self.info_btn.setStyleSheet(INFO_BTN_STYLE)
        self.info_btn.clicked.connect(self._show_info)
        top_bar.addWidget(self.info_btn)

        outer_layout.addLayout(top_bar)

        # ── Main content area ────────────────────────────────────────────────
        content_widget = QWidget()
        main_layout = QHBoxLayout(content_widget)
        main_layout.setContentsMargins(15, 10, 15, 15)
        main_layout.setSpacing(15)

        # Columna Izquierda: Archivos
        left_frame = QFrame()
        left_layout = QVBoxLayout(left_frame)
        left_layout.setContentsMargins(0, 0, 0, 0)
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
        right_layout.setContentsMargins(0, 0, 0, 0)
        self.config_panel = ConfigPanel()
        right_layout.addWidget(self.config_panel)

        self.process_btn = QPushButton("EXECUTE TRANSFORMATION")
        self.process_btn.setFixedHeight(50)
        self.process_btn.setStyleSheet(
            "background-color: #409eff; color: white; font-weight: bold; border-radius: 8px;"
        )
        right_layout.addWidget(self.process_btn)

        main_layout.addWidget(left_frame, 1)
        main_layout.addWidget(self.preview_panel, 2)
        main_layout.addWidget(right_frame, 1)

        outer_layout.addWidget(content_widget)

    def _show_info(self):
        """
        Display a fully size-controllable info pop-up.
        Adjust the setFixedSize values below to resize the dialog.
        """
        info = _load_info_message("main_window")

        # Custom QDialog for full size control (QMessageBox cannot be resized)
        dialog = QDialog(self)
        dialog.setWindowTitle(info["title"])
        dialog.setFixedSize(650, 300)  # ← Change width/height here to resize

        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(20, 20, 20, 15)
        layout.setSpacing(15)

        # Message label with word wrap enabled
        label = QLabel(info["message"])
        label.setWordWrap(True)
        label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        layout.addWidget(label, stretch=1)

        # Close button aligned to the right
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        close_btn = QPushButton("Close")
        close_btn.setFixedWidth(80)
        close_btn.clicked.connect(dialog.accept)
        btn_row.addWidget(close_btn)
        layout.addLayout(btn_row)

        dialog.exec()
