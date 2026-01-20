import sys
from PyQt6.QtWidgets import QApplication
from code.utils.app_paths import ensure_app_directories
from code.ui.landing_page import LandingPage

def main():
    ensure_app_directories()

    app = QApplication(sys.argv)
    window = LandingPage()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()