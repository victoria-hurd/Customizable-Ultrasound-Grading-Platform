from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel,
    QRadioButton, QPushButton
)

class WelcomeDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Ultrasound Grading Tool")

        layout = QVBoxLayout()

        layout.addWidget(QLabel("Welcome to the Ultrasound Grading Tool"))

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
            from admin.admin_window import AdminMainWindow
            self.window = AdminMainWindow()
        else:
            from grader.grader_window import GraderMainWindow
            self.window = GraderMainWindow()

        self.window.show()
        self.close()
