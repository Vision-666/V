import sys, math
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QCalendarWidget, QLabel, QHBoxLayout
from PyQt5.QtCore import QTimer, Qt, QTime, QDate, QRectF, QPointF
from PyQt5.QtGui import QPainter, QPen, QColor

class ToggleSwitch(QPushButton):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setCheckable(True)
        self.setFixedSize(14, 8)
        self.setStyleSheet("QPushButton { border: 1px solid #888; border-radius: 4px; background: #e0e0e0; } QPushButton:checked { background: #2196F3; }")
    def paintEvent(self, event):
        super().paintEvent(event)
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        x = self.width() - 7 if self.isChecked() else 1
        p.setBrush(QColor("#fff"))
        p.setPen(Qt.NoPen)
        p.drawEllipse(x, 1, 6, 6)
    def set_dark(self): self.setChecked(True)
    def set_light(self): self.setChecked(False)

class SimpleCalendar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.resize(340, 260)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)

        # --- Add Back button at the top ---
        top_bar = QHBoxLayout()
        top_bar.setContentsMargins(0, 0, 0, 0)
        top_bar.setSpacing(0)
        self.back_btn = QPushButton("← Back", self)
        self.back_btn.setFixedHeight(24)
        self.back_btn.setStyleSheet(
            "QPushButton { background: #1976d2; color: white; border: none; border-radius: 4px; padding: 0 12px; font-weight: bold; }"
            "QPushButton:hover { background: #1565c0; }"
        )
        self.back_btn.clicked.connect(self.close)
        top_bar.addWidget(self.back_btn)
        top_bar.addStretch(1)
        layout.addLayout(top_bar)
        # --- End Back button ---

        self.calendar = QCalendarWidget(self)
        self.label = QLabel("Selected date: ", self)
        self.calendar.clicked.connect(self.on_date_clicked)
        layout.addWidget(self.calendar)
        layout.addWidget(self.label)
        self.today = QDate.currentDate()
        self.calendar.setStyleSheet("""
            QCalendarWidget QWidget { background: #f8fafd; color: #222; }
            QCalendarWidget QToolButton { background: #1976d2; color: white; font-weight: bold; border-radius: 4px; height: 28px; }
            QCalendarWidget QMenu { background: #f8fafd; }
            QCalendarWidget QSpinBox { background: #f8fafd; }
            QCalendarWidget QAbstractItemView:enabled { background: #f8fafd; color: #222; selection-background-color: #1976d2; selection-color: white; }
            QCalendarWidget QAbstractItemView:disabled { color: #aaa; }
            QCalendarWidget QAbstractItemView { outline: 0; }
            QCalendarWidget QHeaderView-section { background: #f8fafd; color: #1976d2; font-weight: bold; }
        """)
        self.label.setStyleSheet("padding: 4px; color: #1976d2; font-weight: bold;")
        self.setStyleSheet("background: #f8fafd; border: 1px solid #1976d2; border-radius: 8px;")
        self.update_label(self.calendar.selectedDate())

    def on_date_clicked(self, date):
        self.update_label(date)
        if date == self.today:
            self.close()
        elif date.day() in (1, 30, 31):
            QApplication.quit()

    def update_label(self, date):
        self.label.setText(f"Selected date: {date.toString()}")

    def closeEvent(self, event):
        parent = self.parentWidget()
        if parent and hasattr(parent, "_calendar_popup"):
            parent._calendar_popup = None
        super().closeEvent(event)

class AnalogClock(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.resize(172, 192)
        g = QApplication.primaryScreen().availableGeometry()
        self.move(g.x() + g.width() - self.width() - 10, g.y() + 10)
        self.is_dark = True

        self.close_btn = QPushButton(self)
        self.close_btn.setFixedSize(18, 18)
        self.close_btn.setStyleSheet("QPushButton { background: transparent; border: none; }")
        self.close_btn.setToolTip("Close")
        self.close_btn.clicked.connect(self.close)

        self.toggle = ToggleSwitch(self)
        self.toggle.set_dark()
        self.toggle.clicked.connect(self.toggle_theme_switch)

        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setStyleSheet("QWidget { background: transparent; }")
        QTimer(self, timeout=self.update).start(1000)

        self.setCursor(Qt.ArrowCursor)
        self._toggle_offset = None  # Store offset from top for toggle

        self._drag_pos = None
        self._resizing = False
        self._resize_start = None
        self._resize_radius = None

        self._date_rect = None  # Store bounding rect for date
        self._calendar_popup = None  # Reference to calendar popup

    def toggle_theme_switch(self):
        self.is_dark = self.toggle.isChecked()
        self.toggle.set_dark() if self.is_dark else self.toggle.set_light()
        self.update()

    def paintEvent(self, event):
        side = min(self.width(), self.height())
        r = side // 2
        t = QTime.currentTime()
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        p.translate(self.width() / 2, self.height() / 2)
        p.scale(r / 100.0, r / 100.0)
        if self.is_dark:
            face, hmc, mmc, hhc, mhc, shc, cc, bc = (
                QColor(50,50,60), QColor(120,180,255), QColor(90,120,160),
                QColor(0,255,255), QColor(100,255,100), QColor(255,80,80),
                QColor(220,220,220), QColor(180,220,255)
            )
        else:
            face, hmc, mmc, hhc, mhc, shc, cc, bc = (
                QColor(255,255,255), QColor(40,80,160), QColor(120,150,200),
                QColor(0,120,180), QColor(60,180,80), QColor(200,0,0),
                QColor(40,40,40), QColor(80,120,200)
            )
        p.setPen(QPen(bc, 1.5)); p.setBrush(Qt.NoBrush); p.drawEllipse(-100, -100, 200, 200)
        p.setPen(Qt.NoPen); p.setBrush(face); p.drawEllipse(-100, -100, 200, 200)
        p.setPen(QPen(hmc, 3))
        for i in range(12): p.drawLine(88, 0, 98, 0); p.rotate(30)
        p.setPen(QPen(mmc, 1))
        for i in range(60):
            if i % 5: p.drawLine(92, 0, 98, 0)
            p.rotate(6)
        p.setPen(QPen(hmc))
        f = p.font(); f.setPointSize(8); f.setBold(True); p.setFont(f)
        fm = p.fontMetrics(); nr = 78
        for i in range(1, 13):
            a = (i - 3) * (math.pi / 6)
            x, y = nr * math.cos(a), nr * math.sin(a)
            txt = str(i)
            w, h = fm.horizontalAdvance(txt), fm.height()
            p.drawText(int(x - w / 2), int(y + h / 3), txt)
        p.setPen(QPen(hhc, 5.6, Qt.SolidLine, Qt.RoundCap))
        p.save(); p.rotate(30 * ((t.hour() % 12) + t.minute() / 60.0)); p.drawLine(0, 0, 0, -50); p.restore()
        p.setPen(QPen(mhc, 4, Qt.SolidLine, Qt.RoundCap))
        p.save(); p.rotate(6 * (t.minute() + t.second() / 60.0)); p.drawLine(0, 0, 0, -70); p.restore()
        p.setPen(QPen(shc, 2, Qt.SolidLine, Qt.RoundCap))
        p.save(); p.rotate(6 * t.second()); p.drawLine(0, 10, 0, -80); p.restore()
        p.setBrush(QColor(220,220,220) if self.is_dark else QColor(40,40,40))
        p.setPen(Qt.NoPen)
        p.drawEllipse(-6, -6, 12, 12)
        cross_color = QColor(0, 200, 0) if self.is_dark else QColor(0, 0, 0)
        p.setPen(QPen(cross_color, 2.25, Qt.SolidLine, Qt.RoundCap))
        cx, cy = 0, 0
        d = 4
        p.drawLine(cx - d, cy - d, cx + d, cy + d)
        p.drawLine(cx - d, cy + d, cx + d, cy - d)

        # --- Draw date below the center ---
        date = QDate.currentDate()
        date_str = date.toString("ddd, dd MMM yyyy")
        p.setPen(cc)
        date_font = p.font()
        date_font.setPointSize(7)
        date_font.setBold(False)
        p.setFont(date_font)
        date_fm = p.fontMetrics()
        date_w = date_fm.horizontalAdvance(date_str)
        date_h = date_fm.height()
        date_x = -date_w // 2
        date_y = 30 + date_h // 2
        p.drawText(date_x, date_y, date_str)
        # Make clickable rect bigger for easier clicking
        scale = (min(self.width(), self.height()) / 200.0)
        center_x = self.width() / 2
        center_y = self.height() / 2
        pad = 8  # padding in logical units
        rect_top_left = QPointF(center_x + (date_x - pad) * scale, center_y + (date_y - date_h - pad) * scale)
        rect_bottom_right = QPointF(center_x + (date_x + date_w + pad) * scale, center_y + (date_y + pad) * scale)
        self._date_rect = QRectF(rect_top_left, rect_bottom_right)
        # Draw the clickable rect for debugging (remove after testing)
        p.setPen(QPen(Qt.red, 1, Qt.DashLine))
        p.setBrush(Qt.NoBrush)
        p.drawRect(self._date_rect)
        # --- End date drawing ---

    def resizeEvent(self, event):
        # Position toggle directly below "12" numeral, using proportional offset
        side = min(self.width(), self.height())
        center_x = self.width() // 2
        center_y = self.height() // 2
        radius = side // 2
        numeral_offset = int(radius * 0.22)  # proportional distance from center to "12"
        toggle_gap = int(radius * 0.08)      # proportional gap below "12"
        toggle_y = center_y - radius + numeral_offset + toggle_gap
        self.toggle.move(center_x - self.toggle.width() // 2, int(toggle_y))
        self.close_btn.move(center_x - self.close_btn.width() // 2, self.height() // 2 - self.close_btn.height() // 2)
        super().resizeEvent(event)

    def wheelEvent(self, event):
        # Resize clock using trackpad/mouse wheel
        delta = event.angleDelta().y() // 8  # 1 unit = 1 px
        side = max(80, min(self.width(), self.height()) + delta)
        self.resize(side, side)

    def mousePressEvent(self, e):
        # Check if click is inside date rect
        if self._date_rect and self._date_rect.contains(e.pos()):
            self.open_calendar_popup()
            e.accept()
            return
        if e.button() == Qt.LeftButton:
            x, y = e.x(), e.y()
            center_x, center_y = self.width() // 2, self.height() // 2
            dist = math.hypot(x - center_x, y - center_y)
            radius = min(self.width(), self.height()) // 2
            if abs(dist - radius) < 10:
                self._resizing = True
                self._resize_start = (e.globalX(), e.globalY())
                self._resize_radius = radius
            else:
                self._drag_pos = e.globalPos() - self.frameGeometry().topLeft()
            e.accept()

    def mouseMoveEvent(self, e):
        # Change cursor if hovering over date
        if self._date_rect and self._date_rect.contains(e.pos()):
            self.setCursor(Qt.PointingHandCursor)
        else:
            self.setCursor(Qt.ArrowCursor)
        if self._resizing and e.buttons() == Qt.LeftButton:
            dx = e.globalX() - self._resize_start[0]
            dy = e.globalY() - self._resize_start[1]
            delta = max(dx, dy)
            new_radius = max(80, self._resize_radius + delta)
            self.resize(new_radius * 2, new_radius * 2)
            e.accept()
        elif self._drag_pos and e.buttons() == Qt.LeftButton:
            self.move(e.globalPos() - self._drag_pos)
            e.accept()

    def mouseReleaseEvent(self, e):
        self._drag_pos = None
        self._resizing = False
        self._resize_start = None
        self._resize_radius = None
        e.accept()

    def mouseDoubleClickEvent(self, event):
        # Do nothing on double-click to prevent accidental close
        event.ignore()

    def open_calendar_popup(self):
        if self._calendar_popup is None:
            self._calendar_popup = SimpleCalendar(self)
            # Position the calendar centered relative to the clock, on the screen
            parent_geo = self.frameGeometry()
            popup_geo = self._calendar_popup.frameGeometry()
            screen = QApplication.primaryScreen().availableGeometry()
            x = parent_geo.left() + (parent_geo.width() - self._calendar_popup.width()) // 2
            y = parent_geo.top() + (parent_geo.height() - self._calendar_popup.height()) // 2
            # Ensure the popup stays within the screen bounds
            x = max(screen.left(), min(x, screen.right() - self._calendar_popup.width()))
            y = max(screen.top(), min(y, screen.bottom() - self._calendar_popup.height()))
            self._calendar_popup.move(x, y)
            self._calendar_popup.setWindowFlags(Qt.Window | Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
            self._calendar_popup.show()
            self._calendar_popup.destroyed.connect(self._on_calendar_closed)
        else:
            self._calendar_popup.raise_()
            self._calendar_popup.activateWindow()

    def _on_calendar_closed(self, obj):
        self._calendar_popup = None

    def closeEvent(self, event):
        self.deleteLater()
        super().closeEvent(event)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    clock = AnalogClock()
    clock.setStyleSheet("background: transparent;")
    clock.show()
    sys.exit(app.exec_())