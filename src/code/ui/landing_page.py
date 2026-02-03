from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QApplication
from code.admin.admin_landing import AdminLanding
from code.grader.grader_landing import GraderLanding

class LandingPage(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Ultrasound Grading Platform")

        layout = QVBoxLayout(self)

        title = QLabel("Welcome to the Ultrasound Grading Platform")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title)

        admin_btn = QPushButton("Enter as Admin")
        grader_btn = QPushButton("Enter as Grader")
        exit_btn = QPushButton("Exit Application")

        admin_btn.clicked.connect(self.open_admin)
        grader_btn.clicked.connect(self.open_grader)
        exit_btn.clicked.connect(QApplication.instance().quit)

        layout.addWidget(admin_btn)
        layout.addWidget(grader_btn)
        layout.addWidget(exit_btn)

    def open_admin(self):
        self.admin_window = AdminLanding(parent_window=self)
        self.admin_window.show()
        self.close()

    def open_grader(self):
        self.grader_window = GraderLanding(parent_window=self)
        self.grader_window.show()
        self.close()
