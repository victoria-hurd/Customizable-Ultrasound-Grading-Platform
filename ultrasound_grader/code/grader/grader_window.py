from PyQt6.QtWidgets import QMainWindow
from code.grader.grading_session import GradingSessionTab

# Open grader main window with intro and workflow start
class GraderStartWindow(QMainWindow):
    def __init__(self,loaded_metadata,current_study_path,grader_name):
        super().__init__()
        self.setWindowTitle("Grading Session")
        self.resize(1200, 800)

        self.session_tab = GradingSessionTab(loaded_metadata,current_study_path,grader_name)
        self.setCentralWidget(self.session_tab)
