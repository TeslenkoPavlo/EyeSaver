import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QLabel, QLineEdit, QPushButton, QGraphicsDropShadowEffect,
    QSpacerItem, QSizePolicy
)
from PyQt6.QtCore import Qt, QTimer, QEvent, QRegularExpression
from PyQt6.QtGui import QColor, QPalette, QIntValidator, QRegularExpressionValidator


class StyleSheet:

    MAIN_WINDOW = "QMainWindow { background: #000000; }"
    CENTRAL_WIDGET = "QWidget#centralWidget { background: #000000; }"

    INPUT_LABEL = """
        QLabel {
            color: #888888;
            font-size: 14px;
            font-family: 'Segoe UI', Arial;
        }
    """

    LINE_EDIT = """
        QLineEdit {
            background: #111111;
            border: none;
            border-bottom: 2px solid #333333;
            color: #ffffff;
            font-size: 36px;
            font-weight: bold;
            font-family: 'Consolas', monospace;
            padding: 15px;
        }
        QLineEdit:focus {
            border-bottom: 2px solid #ff6b35;
        }
    """

    START_BUTTON = """
        QPushButton {
            background: #ff6b35;
            border: none;
            border-radius: 12px;
            color: #000000;
            font-size: 22px;
            font-weight: bold;
            font-family: 'Segoe UI', Arial;
            padding: 20px 60px;
        }
        QPushButton:hover {
            background: #ff8c5a;
        }
        QPushButton:pressed {
            background: #e55a2b;
        }
    """

    STOP_BUTTON = """
        QPushButton {
            background: #cc3333;
            border: none;
            border-radius: 12px;
            color: #ffffff;
            font-size: 22px;
            font-weight: bold;
            font-family: 'Segoe UI', Arial;
            padding: 20px 60px;
        }
        QPushButton:hover {
            background: #ff4444;
        }
        QPushButton:pressed {
            background: #aa2222;
        }
    """

    WORK_TIMER_DISPLAY = """
        QLabel {
            color: #ff6b35;
            font-size: 150px;
            font-weight: bold;
            font-family: 'Consolas', monospace;
        }
    """


class BlockingScreen(QWidget):

    def __init__(self, break_duration, on_finished_callback, parent=None):
        super().__init__(parent)
        self.remaining_time = break_duration
        self.on_finished_callback = on_finished_callback
        self.init_ui()
        self.setup_timer()
        self.setup_focus_timer()

    def init_ui(self):
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.BypassWindowManagerHint
        )
        self.setStyleSheet("QWidget { background: #000000; }")

        screen = QApplication.primaryScreen().geometry()
        self.setGeometry(screen)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.countdown_label = QLabel()
        self.countdown_label.setStyleSheet("color: #ff6b35; font-size: 200px; font-weight: bold; font-family: 'Consolas', monospace;")
        self.countdown_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.countdown_label)

        self.update_display()

    def setup_timer(self):
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.tick)
        self.timer.start(1000)

    def setup_focus_timer(self):
        self.focus_timer = QTimer(self)
        self.focus_timer.timeout.connect(self.force_focus)
        self.focus_timer.start(100)

    def force_focus(self):
        self.raise_()
        self.activateWindow()
        self.setFocus()

    def tick(self):
        self.remaining_time -= 1
        self.update_display()
        if self.remaining_time <= 0:
            self.timer.stop()
            self.focus_timer.stop()
            self.on_finished_callback()
            self.close()

    def update_display(self):
        m, s = divmod(self.remaining_time, 60)
        self.countdown_label.setText(f"{m:02d}:{s:02d}")

    def keyPressEvent(self, event):
        event.ignore()

    def keyReleaseEvent(self, event):
        event.ignore()

    def mousePressEvent(self, event):
        event.ignore()

    def mouseDoubleClickEvent(self, event):
        event.ignore()

    def closeEvent(self, event):
        if self.remaining_time > 0:
            event.ignore()
        else:
            event.accept()

    def event(self, event):
        if event.type() in (QEvent.Type.Close, QEvent.Type.Hide, QEvent.Type.WindowDeactivate):
            if self.remaining_time > 0:
                self.force_focus()
                return True
        return super().event(event)


class EyeSaverApp(QMainWindow):

    def __init__(self):
        super().__init__()
        self.work_timer = QTimer(self)
        self.display_timer = QTimer(self)
        self.remaining_work_time = 0
        self.blocking_screen = None
        self.is_running = False
        self.init_ui()
        self.connect_signals()

    def init_ui(self):
        self.setWindowTitle("EyeSaver - Developed by Pavlo TESLENKO (Group 45 2026)")
        self.setMinimumSize(400, 500)
        self.setStyleSheet(StyleSheet.MAIN_WINDOW)

        central = QWidget()
        central.setObjectName("centralWidget")
        central.setStyleSheet(StyleSheet.CENTRAL_WIDGET)
        self.setCentralWidget(central)

        layout = QVBoxLayout(central)
        layout.setContentsMargins(50, 50, 50, 50)
        layout.setSpacing(0)

        layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        self.settings_container = QWidget()
        settings_layout = QVBoxLayout(self.settings_container)
        settings_layout.setContentsMargins(0, 0, 0, 0)
        settings_layout.setSpacing(0)

        self.work_label = QLabel("Час роботи (хв)")
        self.work_label.setStyleSheet(StyleSheet.INPUT_LABEL)
        self.work_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        settings_layout.addWidget(self.work_label)

        self.work_input = QLineEdit("25")
        self.work_input.setStyleSheet(StyleSheet.LINE_EDIT)
        work_validator = QRegularExpressionValidator(QRegularExpression(r"^[0-9]*[.,]?[0-9]*$"))
        self.work_input.setValidator(work_validator)
        self.work_input.setMaxLength(5)
        self.work_input.setFixedWidth(150)
        self.work_input.setAlignment(Qt.AlignmentFlag.AlignCenter)
        settings_layout.addWidget(self.work_input, alignment=Qt.AlignmentFlag.AlignCenter)

        settings_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed))

        self.break_label = QLabel("Час перерви (сек)")
        self.break_label.setStyleSheet(StyleSheet.INPUT_LABEL)
        self.break_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        settings_layout.addWidget(self.break_label)

        self.break_input = QLineEdit("20")
        self.break_input.setStyleSheet(StyleSheet.LINE_EDIT)
        self.break_input.setValidator(QIntValidator(1, 999))
        self.break_input.setMaxLength(3)
        self.break_input.setFixedWidth(150)
        self.break_input.setAlignment(Qt.AlignmentFlag.AlignCenter)
        settings_layout.addWidget(self.break_input, alignment=Qt.AlignmentFlag.AlignCenter)

        settings_layout.addSpacerItem(QSpacerItem(20, 60, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed))

        self.btn = QPushButton("ЗАПУСТИТИ")
        self.btn.setStyleSheet(StyleSheet.START_BUTTON)
        self.btn.setCursor(Qt.CursorShape.PointingHandCursor)

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(30)
        shadow.setOffset(0, 0)
        shadow.setColor(QColor(255, 107, 53, 150))
        self.btn.setGraphicsEffect(shadow)

        settings_layout.addWidget(self.btn, alignment=Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(self.settings_container)

        self.timer_container = QWidget()
        timer_layout = QVBoxLayout(self.timer_container)
        timer_layout.setContentsMargins(0, 0, 0, 0)
        timer_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.work_timer_display = QLabel("")
        self.work_timer_display.setStyleSheet(StyleSheet.WORK_TIMER_DISPLAY)
        self.work_timer_display.setAlignment(Qt.AlignmentFlag.AlignCenter)
        timer_layout.addWidget(self.work_timer_display)

        self.stop_btn = QPushButton("ЗУПИНИТИ")
        self.stop_btn.setStyleSheet(StyleSheet.STOP_BUTTON)
        self.stop_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        timer_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed))
        timer_layout.addWidget(self.stop_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        self.timer_container.hide()
        layout.addWidget(self.timer_container)

        layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

    def connect_signals(self):
        self.btn.clicked.connect(self.start)
        self.stop_btn.clicked.connect(self.stop)
        self.work_timer.timeout.connect(self.on_work_done)
        self.display_timer.timeout.connect(self.update_work_display)

    def get_work_time(self):
        try:
            value_str = self.work_input.text().replace(',', '.')
            minutes = float(value_str)
            seconds = int(minutes * 60)
            return max(1, seconds)
        except:
            return 25 * 60

    def get_break_time(self):
        try:
            return max(1, int(self.break_input.text()))
        except:
            return 20

    def start(self):
        self.is_running = True
        self.remaining_work_time = self.get_work_time()

        self.settings_container.hide()
        self.timer_container.show()
        self.update_work_display()

        self.work_timer.start(self.remaining_work_time * 1000)
        self.display_timer.start(1000)

    def stop(self):
        self.is_running = False
        self.work_timer.stop()
        self.display_timer.stop()

        self.timer_container.hide()
        self.settings_container.show()

    def update_work_display(self):
        if self.remaining_work_time > 0:
            self.remaining_work_time -= 1
            m, s = divmod(self.remaining_work_time, 60)
            self.work_timer_display.setText(f"{m:02d}:{s:02d}")
        else:
            self.display_timer.stop()

    def on_work_done(self):
        self.work_timer.stop()
        self.display_timer.stop()

        duration = self.get_break_time()
        self.blocking_screen = BlockingScreen(duration, self.on_break_done)
        self.blocking_screen.showFullScreen()
        self.blocking_screen.activateWindow()
        self.blocking_screen.raise_()

    def on_break_done(self):
        self.blocking_screen = None

        if self.is_running:
            self.remaining_work_time = self.get_work_time()
            self.work_timer.start(self.remaining_work_time * 1000)
            self.display_timer.start(1000)
            self.update_work_display()


def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')

    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor(0, 0, 0))
    palette.setColor(QPalette.ColorRole.WindowText, QColor(255, 255, 255))
    palette.setColor(QPalette.ColorRole.Base, QColor(17, 17, 17))
    palette.setColor(QPalette.ColorRole.Text, QColor(255, 255, 255))
    palette.setColor(QPalette.ColorRole.Button, QColor(17, 17, 17))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor(255, 255, 255))
    palette.setColor(QPalette.ColorRole.Highlight, QColor(255, 107, 53))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor(0, 0, 0))
    app.setPalette(palette)

    window = EyeSaverApp()
    window.showMaximized()

    sys.exit(app.exec())


if __name__ == '__main__':
    main()

