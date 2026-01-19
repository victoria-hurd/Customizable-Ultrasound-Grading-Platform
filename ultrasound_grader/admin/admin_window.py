from PyQt6.QtWidgets import QMainWindow, QTabWidget
from admin.create_study_tab import CreateStudyTab
#from admin.review_results_tab import ReviewResultsTab

# Open admin main window with tabs for study creation and results review
class AdminMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Admin: Study Management")
        self.resize(1200, 800)

        tabs = QTabWidget()
        tabs.addTab(CreateStudyTab(), "Create Study")
        #tabs.addTab(ReviewResultsTab(), "Review Results")

        self.setCentralWidget(tabs)
