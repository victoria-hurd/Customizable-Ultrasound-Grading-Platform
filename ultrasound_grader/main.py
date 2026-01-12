import sys
from PyQt6.QtWidgets import QApplication
from welcome_dialog import WelcomeDialog

def main():
    app = QApplication(sys.argv)
    dialog = WelcomeDialog() # Start application with WelcomeDialog
    dialog.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
