from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QLabel,
                             QRadioButton, QPushButton)
from PyQt6.QtCore import pyqtSignal

# Welcome dialog box to choose between Admin and Grader modes
# Using signals to launch respective main windows
class WelcomeDialog(QDialog):
    launch_admin = pyqtSignal()
    launch_grader = pyqtSignal()
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Ultrasound Grading Tool")

        layout = QVBoxLayout()

        layout.addWidget(QLabel("Welcome to the Dynamic, Open-Source Ultrasound Grader program!"))

        self.admin_radio = QRadioButton("Enter as Admin")
        self.grader_radio = QRadioButton("Enter as Grader")

        layout.addWidget(self.admin_radio)
        layout.addWidget(self.grader_radio)

        btn = QPushButton("Continue")
        btn.clicked.connect(self.continue_clicked)
        layout.addWidget(btn)

        self.setLayout(layout)

    def continue_clicked(self):
        if self.admin_radio.isChecked():
            self.launch_admin.emit()
        elif self.grader_radio.isChecked():
            self.launch_grader.emit()

