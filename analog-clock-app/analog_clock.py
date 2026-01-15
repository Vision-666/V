import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton
from PyQt5.QtCore import QTimer, Qt, QTime
from PyQt5.QtGui import QPainter, QPen, QColor

class ToggleSwitch(QPushButton):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setCheckable(True)
        self.setFixedSize(30, 16)
        self.setStyleSheet("""
            QPushButton {
                border: 0.75px solid rgba(0,0,0,0.5);
                border-radius: 8px;
                background-color: #e0e0e0;
            }
            QPushButton:checked {
                border: 0.75px solid rgba(0,0,0,0.5);
                background-color: #2196F3;
            }
        """)

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        if self.isChecked():
            circle_x = self.width() - 16
            bg_color = QColor("#2196F3")
        else:
            circle_x = 2
            bg_color = QColor("#e0e0e0")
        painter.setBrush(QColor("#fff"))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(circle_x, 2, 12, 12)

    def set_dark(self):
        self.setChecked(True)

    def set_light(self):
        self.setChecked(False)

class AnalogClock(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.Window | Qt.CustomizeWindowHint | Qt.WindowTitleHint | Qt.WindowStaysOnTopHint)
        self.setWindowTitle('Analog Clock (Dark/Light Theme)')
        self.resize(400, 400)
        self.is_dark = True

        self.toggle = ToggleSwitch(self)
        self.toggle.move(self.width() - 45, 10)
        self.toggle.set_dark()
        self.toggle.clicked.connect(self.toggle_theme_switch)

        self.setStyleSheet("QWidget { background-color: #1e1e28; }")

        timer = QTimer(self)
        timer.timeout.connect(self.update)
        timer.start(1000)

    def toggle_theme_switch(self):
        if self.toggle.isChecked():
            self.is_dark = True
            self.toggle.set_dark()
            self.setStyleSheet("QWidget { background-color: #1e1e28; }")
        else:
            self.is_dark = False
            self.toggle.set_light()
            self.setStyleSheet("QWidget { background-color: #f0f0f0; }")
        self.update()

    def paintEvent(self, event):
        side = min(self.width(), self.height())
        margin = 10
        clock_radius = (side // 2) - margin

        time = QTime.currentTime()
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.translate(self.width() / 2, self.height() / 2)
        painter.scale(clock_radius / 100.0, clock_radius / 100.0)

        if self.is_dark:
            bg_color = QColor(30, 30, 40)
            face_color = QColor(50, 50, 60)
            hour_mark_color = QColor(120, 180, 255)
            min_mark_color = QColor(90, 120, 160)
            hour_hand_color = QColor(0, 255, 255)
            min_hand_color = QColor(100, 255, 100)
            sec_hand_color = QColor(255, 80, 80)
            center_color = QColor(220, 220, 220)
            border_color = QColor(180, 220, 255)
        else:
            bg_color = QColor(240, 240, 240)
            face_color = QColor(255, 255, 255)
            hour_mark_color = QColor(40, 80, 160)
            min_mark_color = QColor(120, 150, 200)
            hour_hand_color = QColor(0, 120, 180)
            min_hand_color = QColor(60, 180, 80)
            sec_hand_color = QColor(200, 0, 0)
            center_color = QColor(40, 40, 40)
            border_color = QColor(80, 120, 200)

        painter.setPen(Qt.NoPen)
        painter.setBrush(bg_color)
        painter.drawRect(-120, -120, 240, 240)

        painter.setPen(QPen(border_color, 1.5))
        painter.setBrush(Qt.NoBrush)
        painter.drawEllipse(-104, -104, 208, 208)

        painter.setPen(Qt.NoPen)
        painter.setBrush(face_color)
        painter.drawEllipse(-100, -100, 200, 200)

        painter.setPen(QPen(hour_mark_color, 3))
        for i in range(12):
            painter.drawLine(88, 0, 98, 0)
            painter.rotate(30)

        painter.setPen(QPen(min_mark_color, 1))
        for i in range(60):
            if i % 5 != 0:
                painter.drawLine(92, 0, 98, 0)
            painter.rotate(6)

        painter.setPen(QPen(hour_mark_color if self.is_dark else QColor(40, 80, 160)))
        font = painter.font()
        font.setPointSize(8)
        font.setBold(True)
        painter.setFont(font)
        import math
        fm = painter.fontMetrics()
        number_radius = 78
        for i in range(1, 13):
            angle = (i - 3) * (math.pi / 6)
            x = number_radius * math.cos(angle)
            y = number_radius * math.sin(angle)
            text = str(i)
            w = fm.horizontalAdvance(text)
            h = fm.height()
            painter.drawText(int(x - w / 2), int(y + h / 3), text)

        painter.setPen(QPen(hour_hand_color, 5.6, Qt.SolidLine, Qt.RoundCap))
        hour_angle = 30 * ((time.hour() % 12) + time.minute() / 60.0)
        painter.save()
        painter.rotate(hour_angle)
        painter.drawLine(0, 0, 0, -50)
        painter.restore()

        painter.setPen(QPen(min_hand_color, 4, Qt.SolidLine, Qt.RoundCap))
        minute_angle = 6 * (time.minute() + time.second() / 60.0)
        painter.save()
        painter.rotate(minute_angle)
        painter.drawLine(0, 0, 0, -70)
        painter.restore()

        painter.setPen(QPen(sec_hand_color, 2, Qt.SolidLine, Qt.RoundCap))
        second_angle = 6 * time.second()
        painter.save()
        painter.rotate(second_angle)
        painter.drawLine(0, 10, 0, -80)
        painter.restore()

        painter.setBrush(center_color)
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(-6, -6, 12, 12)

    def resizeEvent(self, event):
        self.toggle.move(self.width() - 45, 10)
        super().resizeEvent(event)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    clock = AnalogClock()
    clock.show()
    sys.exit(app.exec_())