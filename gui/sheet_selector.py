from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QComboBox, QPushButton

class SheetSelectorDialog(QDialog):
    def __init__(self, sheets):
        super().__init__()
        self.setWindowTitle("Select Sheet")
        self.layout = QVBoxLayout(self)
        
        self.layout.addWidget(QLabel("Select sheet to process:"))
        self.combo = QComboBox()
        self.combo.addItems(sheets)
        self.layout.addWidget(self.combo)
        
        self.btn = QPushButton("Accept")
        self.btn.clicked.connect(self.accept)
        self.layout.addWidget(self.btn)
        
    def get_selected_sheet(self):
        return self.combo.currentText()
