from PyQt6.QtWidgets import QMainWindow, QLabel

# Open grader main window with intro and workflow start
class GraderMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Grader")
        self.resize(1200, 800)

        self.setCentralWidget(QLabel("Placeholder: Grader workflow start"))
