import sys
from PyQt6.QtWidgets import QApplication
from welcome_dialog import WelcomeDialog
from admin.admin_window import AdminMainWindow
from grader.grader_window import GraderMainWindow

def main():
    app = QApplication(sys.argv)
    welcome = WelcomeDialog() # Start application with WelcomeDialog
    admin_window = AdminMainWindow()
    grader_window = GraderMainWindow()

    welcome.launch_admin.connect(lambda: (
        admin_window.show(),
        welcome.hide()
    ))

    welcome.launch_grader.connect(lambda: (
        grader_window.show(),
        welcome.hide()
    ))

    welcome.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
