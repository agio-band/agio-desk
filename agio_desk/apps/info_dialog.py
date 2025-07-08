from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel
from PySide6.QtCore import Qt


class InfoDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout()
        self.setLayout(layout)
        message = QLabel(self)
        message.setAlignment(Qt.AlignCenter)
        layout.addWidget(message)
        message.setText(self.get_message_text())
        self.resize(400, 200)

    def get_message_text(self):
        return 'Info dialog!!!'


