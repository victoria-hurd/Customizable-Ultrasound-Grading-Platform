import sys
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon
from code.utils.app_paths import ensure_app_directories, get_resource_dir
from code.ui.landing_page import LandingPage

def main():
    APP_RESOURCES_DIR = get_resource_dir()

    ensure_app_directories()
    icon_path = os.path.join(APP_RESOURCES_DIR, "icons", "ultrasoundastronaut.png")
    app = QApplication(sys.argv)
    window = LandingPage()
    window.setWindowIcon(QIcon(str(icon_path)))
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()