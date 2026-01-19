from PyQt6.QtWidgets import QMainWindow
from grader.grading_session import GradingSessionTab

# Open grader main window with intro and workflow start
class GraderMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Grading Session")
        self.resize(1200, 800)

        self.session_tab = GradingSessionTab()
        self.setCentralWidget(self.session_tab)
