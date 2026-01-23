import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon
from code.utils.app_paths import ensure_app_directories, get_project_root
from code.ui.landing_page import LandingPage

def main():
    ensure_app_directories()
    icon_path = get_project_root() / "app_resources" / "icons" / "ultrasoundastronaut.png"
    print(icon_path)
    app = QApplication(sys.argv)
    window = LandingPage()
    window.setWindowIcon(QIcon(str(icon_path)))
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()