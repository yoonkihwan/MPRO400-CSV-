from __future__ import annotations

import logging
import sys
from pathlib import Path

if __package__ is None or __package__ == "":
    sys.path.append(str(Path(__file__).resolve().parent.parent))

import matplotlib
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication


from PySide6.QtGui import QPalette, QColor, QIcon



from app.config import AppConfig
from data.data_manager import DataManager
from ui.main_window import MainWindow

LOG_DIR = Path("logs")
LOG_FILE = LOG_DIR / "app.log"
STYLE_PATH = Path(__file__).resolve().parent.parent / "assets" / "style.qss"
ICON_PATH = Path(__file__).resolve().parent.parent.parent / "app.ICO"

matplotlib.rcParams["axes.unicode_minus"] = False


def setup_logging() -> None:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    handlers = [logging.FileHandler(LOG_FILE, encoding="utf-8")]
    handlers.append(logging.StreamHandler())
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=handlers,
    )


def apply_palette(app: QApplication) -> None:
    app.setStyle('Fusion')
    palette = QPalette()
    base = QColor('#ffffff')
    window = QColor('#f4f9f4')
    text = QColor('#1c3324')
    button = QColor('#ffffff')
    highlight = QColor('#c9ead3')
    palette.setColor(QPalette.Window, window)
    palette.setColor(QPalette.WindowText, text)
    palette.setColor(QPalette.Base, base)
    palette.setColor(QPalette.AlternateBase, QColor('#ecf8ef'))
    palette.setColor(QPalette.ToolTipBase, base)
    palette.setColor(QPalette.ToolTipText, text)
    palette.setColor(QPalette.Text, text)
    palette.setColor(QPalette.Button, button)
    palette.setColor(QPalette.ButtonText, text)
    palette.setColor(QPalette.Highlight, highlight)
    palette.setColor(QPalette.HighlightedText, text)
    palette.setColor(QPalette.Link, QColor('#5aa573'))
    app.setPalette(palette)


def apply_stylesheet(app: QApplication) -> None:
    if STYLE_PATH.exists():
        try:
            qss = STYLE_PATH.read_text(encoding="utf-8")
        except OSError:
            return
        app.setStyleSheet(qss)


def main() -> int:
    setup_logging()

    # Set AppUserModelID for Windows to handle taskbar icon correctly
    if sys.platform == "win32":
        import ctypes
        myappid = u'my-mpro400-analyzer.1.0'
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    app = QApplication(sys.argv)
    apply_palette(app)
    apply_stylesheet(app)

    config = AppConfig.load()
    manager = DataManager()
    window = MainWindow(manager, config)

    if ICON_PATH.exists():
        window.setWindowIcon(QIcon(str(ICON_PATH)))

    window.resize(1200, 800)
    window.show()
    window.maybe_show_onboarding()

    exit_code = app.exec()
    config.save()
    return int(exit_code)


if __name__ == "__main__":
    sys.exit(main())
