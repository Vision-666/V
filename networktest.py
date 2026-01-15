import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QListWidget, QLabel, QTextEdit, QDialog, QFileDialog
from PyQt5.QtCore import QTimer, QMimeData
from PyQt5.QtGui import QClipboard
import subprocess
import pyqtgraph as pg
from collections import deque

class LogDialog(QDialog):
    def __init__(self, log_text, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Full Log")
        layout = QVBoxLayout()
        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        self.text_edit.setText(log_text)
        layout.addWidget(self.text_edit)
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)
        self.setLayout(layout)

class NetworkScanner(QWidget):
    """
    PyQt5 GUI application for scanning and displaying available WiFi networks.

    This widget provides a main window with a button to trigger a network scan,
    a list of detected SSIDs, and panes for showing additional information and
    detailed properties of the selected network.
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Live Network Scanner")
        self.setGeometry(100, 100, 600, 400)
        layout = QVBoxLayout()

        self.label = QLabel("Click 'Scan' to search for live networks:")
        layout.addWidget(self.label)

        self.scan_btn = QPushButton("Scan")
        self.scan_btn.clicked.connect(self.scan_networks)
        layout.addWidget(self.scan_btn)

        # Add horizontal layout for columns
        columns_layout = QHBoxLayout()

        # Column A: Networks
        col_a_layout = QVBoxLayout()
        col_a_label = QLabel("SSID")
        col_a_layout.addWidget(col_a_label)
        self.list_widget = QListWidget()
        self.list_widget.currentRowChanged.connect(self.show_details)
        col_a_layout.addWidget(self.list_widget)
        columns_layout.addLayout(col_a_layout)

        # Column B: Additional Info
        col_b_layout = QVBoxLayout()
        col_b_label = QLabel("Details")
        col_b_layout.addWidget(col_b_label)
        self.list_widget_b = QListWidget()
        col_b_layout.addWidget(self.list_widget_b)
        columns_layout.addLayout(col_b_layout)

        # Column C: Extra Info
        col_c_layout = QVBoxLayout()
        col_c_label = QLabel("Extra Info")
        col_c_layout.addWidget(col_c_label)
        self.list_widget_c = QListWidget()
        col_c_layout.addWidget(self.list_widget_c)
        columns_layout.addLayout(col_c_layout)

        layout.addLayout(columns_layout)

        # Details pane
        self.details_pane = QTextEdit()
        self.details_pane.setReadOnly(True)
        layout.addWidget(QLabel("Network Details:"))
        layout.addWidget(self.details_pane)

        # Log file display
        self.log_pane = QTextEdit()
        self.log_pane.setReadOnly(True)
        layout.addWidget(QLabel("Log File:"))
        layout.addWidget(self.log_pane)

        # --- Add Copy Log and Save Log buttons ---
        log_btn_layout = QHBoxLayout()
        self.copy_log_btn = QPushButton("Copy Log")
        self.copy_log_btn.clicked.connect(self.copy_log)
        log_btn_layout.addWidget(self.copy_log_btn)

        self.save_log_btn = QPushButton("Save Log")
        self.save_log_btn.clicked.connect(self.save_log)
        log_btn_layout.addWidget(self.save_log_btn)

        layout.addLayout(log_btn_layout)
        # --- End buttons ---

        self.setLayout(layout)

        # Store full details for each network
        self.network_details = []
        self.previous_signals = {}  # Store previous signal strengths

        # ECG-like live signal plot
        self.plot_widget = pg.PlotWidget(title="Live Signal (ECG-like)")
        self.plot_widget.setYRange(0, 100)
        layout.addWidget(self.plot_widget)
        self.signal_history = {}  # SSID -> deque of recent signal values
        self.max_history = 100    # Number of points to show

        # Add timer for live scanning
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.scan_networks)
        self.timer.start(3000)  # Scan every 3 seconds

        self.log_pane.mousePressEvent = self.open_log_dialog

    def scan_networks(self):
        # Save current selection
        selected_row = self.list_widget.currentRow()
        selected_ssid_c = None
        if 0 <= selected_row < len(self.network_details):
            selected_ssid_c = self.network_details[selected_row].get('SSID', '')

        self.list_widget.clear()
        self.list_widget_b.clear()
        self.list_widget_c.clear()  # Clear column C
        self.details_pane.clear()
        self.network_details = []
        current_signals = {}
        log_lines = []
        try:
            # Try Windows first, fallback to Linux
            try:
                result = subprocess.check_output(
                    ['netsh', 'wlan', 'show', 'networks', 'mode=Bssid'],
                    encoding='utf-8'
                )
                mode = "win"
            except Exception:
                result = subprocess.check_output(
                    ['nmcli', '-t', '-f', 'SSID,SIGNAL,SECURITY,CHAN,MODE', 'dev', 'wifi'],
                    encoding='utf-8'
                )
                mode = "linux"

            log_lines.append("Raw scan output:\n" + result)  # Log raw output for debugging

            if mode == "win":
                networks = self.parse_windows_scan(result)
                for net in networks:
                    ssid = net.get('SSID', '')
                    if not ssid:
                        ssid = "Hidden Network"
                    signal = net.get('Signal', '')
                    anomaly = ""
                    try:
                        signal_val = int(signal.replace('%', ''))
                        prev_val = self.previous_signals.get(ssid)
                        if prev_val is not None and abs(signal_val - prev_val) > 20:
                            anomaly = " (Anomaly!)"
                        current_signals[ssid] = signal_val
                        if ssid not in self.signal_history:
                            self.signal_history[ssid] = deque(maxlen=self.max_history)
                        self.signal_history[ssid].append(signal_val)
                    except:
                        pass
                    channel = net.get('Channel', '')
                    channel_util = net.get('Channel Utilization', '')
                    if channel_util:
                        channel_info = f"{channel} ({channel_util})"
                    else:
                        channel_info = channel
                    info = f"Signal: {signal}{anomaly}, Auth: {net.get('Authentication', '')}, Enc: {net.get('Encryption', '')}, Channel: {channel_info}"
                    self.list_widget.addItem(ssid)
                    self.list_widget_b.addItem(info)
                    extra_info = net.get('Network type', '')  # Example for column C
                    self.list_widget_c.addItem(extra_info)  # Add to column C
                    self.network_details.append(net)
                    log_lines.append(f"{ssid}: {info} | {extra_info}")
            else:
                networks = self.parse_linux_scan(result)
                for net in networks:
                    ssid = net.get('SSID', '')
                    if not ssid:
                        ssid = "Hidden Network"
                    signal = net.get('Signal', '')
                    anomaly = ""
                    try:
                        signal_val = int(signal)
                        prev_val = self.previous_signals.get(ssid)
                        if prev_val is not None and abs(signal_val - prev_val) > 20:
                            anomaly = " (Anomaly!)"
                        current_signals[ssid] = signal_val
                        if ssid not in self.signal_history:
                            self.signal_history[ssid] = deque(maxlen=self.max_history)
                        self.signal_history[ssid].append(signal_val)
                    except:
                        pass
                    info = f"Signal: {signal}{anomaly}, Security: {net.get('Security', '')}, Channel: {net.get('Channel', '')}, Mode: {net.get('Mode', '').upper()}"
                    self.list_widget.addItem(ssid)
                    self.list_widget_b.addItem(info)
                    extra_info = net.get('Mode', '')  # Example for column C
                    self.list_widget_c.addItem(extra_info)  # Add to column C
                    self.network_details.append(net)
                    log_lines.append(f"{ssid}: {info} | {extra_info}")
        except Exception as e:
            self.list_widget.addItem(f"Error: {e}")
            self.list_widget_b.addItem("")
            self.list_widget_c.addItem("")  # Add to column C
            self.network_details.append({'Error': str(e)})
            log_lines.append(f"Error: {e}")

        self.previous_signals = current_signals  # Update for next scan
        self.log_pane.setText("\n".join(log_lines))

        # --- Live ECG plot update ---
        # Remove the duplicate selection logic here

        # Restore selection using selected_ssid_c
        if selected_ssid_c:
            for i, net in enumerate(self.network_details):
                if net.get('SSID', '') == selected_ssid_c:
                    self.list_widget.setCurrentRow(i)
                    # Update ECG plot for the restored selection
                    if selected_ssid_c in self.signal_history:
                        self.plot_widget.clear()
                        self.plot_widget.plot(list(self.signal_history[selected_ssid_c]), pen='g')
                    else:
                        self.plot_widget.clear()
                    break
        elif self.list_widget.count() > 0:
            self.list_widget.setCurrentRow(0)
            # Update ECG plot for the first item
            first_ssid = self.network_details[0].get('SSID', '') if self.network_details else ''
            if first_ssid in self.signal_history:
                self.plot_widget.clear()
                self.plot_widget.plot(list(self.signal_history[first_ssid]), pen='g')
            else:
                self.plot_widget.clear()

    def open_log_dialog(self, event):
        dialog = LogDialog(self.log_pane.toPlainText(), self)
        dialog.resize(600, 400)
        dialog.exec_()

    def show_details(self, row):
        if 0 <= row < len(self.network_details):
            details = self.network_details[row]
            ssid = details.get('SSID', '')
            # Define the order and labels for known fields
            fields = [
                ('SSID', 'SSID'),
                ('Signal', 'Signal'),
                ('Authentication', 'Auth'),
                ('Encryption', 'Enc'),
                ('Channel', 'Channel'),
                ('Network type', 'Type'),
                ('Security', 'Security'),
                ('Mode', 'Mode'),
                ('Error', 'Error')
            ]
            lines = []
            for key, label in fields:
                if key in details:
                    lines.append(f"- {label}: {details[key]}")
            # Add any other fields not listed above
            for k, v in details.items():
                if k not in [f[0] for f in fields]:
                    lines.append(f"- {k}: {v}")
            text = "\n".join(lines)
            self.details_pane.setText(text)
            # Update ECG plot
            if ssid in self.signal_history:
                self.plot_widget.clear()
                self.plot_widget.plot(list(self.signal_history[ssid]), pen='g')
            else:
                self.plot_widget.clear()
        else:
            self.details_pane.clear()

    def copy_log(self):
        clipboard = QApplication.clipboard()
        clipboard.setText(self.log_pane.toPlainText())

    def save_log(self):
        options = QFileDialog.Options()
        filename, _ = QFileDialog.getSaveFileName(self, "Save Log File", "network_log.txt", "Text Files (*.txt);;All Files (*)", options=options)
        if filename:
            with open(filename, "w", encoding="utf-8") as f:
                f.write(self.log_pane.toPlainText())

    def parse_windows_scan(self, result):
        networks = []
        current = {}
        for line in result.split('\n'):
            line = line.strip()
            if line.startswith("SSID"):
                if current:
                    networks.append(current)
                    current = {}
                current['SSID'] = line.split(":", 1)[-1].strip()
            elif line.startswith("Network type"):
                current['Network type'] = line.split(":", 1)[-1].strip()
            elif line.startswith("Authentication"):
                current['Authentication'] = line.split(":", 1)[-1].strip()
            elif line.startswith("Encryption"):
                current['Encryption'] = line.split(":", 1)[-1].strip()
            elif line.startswith("Signal"):
                current['Signal'] = line.split(":", 1)[-1].strip()
            elif line.startswith("Channel"):
                current['Channel'] = line.split(":", 1)[-1].strip()
            elif line.startswith("Channel Utilization"):
                current['Channel Utilization'] = line.split(":", 1)[-1].strip()
        if current:
            networks.append(current)
        return networks

    def parse_linux_scan(self, result):
        networks = []
        for line in result.split('\n'):
            if line:
                parts = line.split(':')
                ssid = parts[0].strip() if len(parts) > 0 else ""
                if not ssid:
                    ssid = "Hidden Network"
                signal = parts[1].strip() if len(parts) > 1 else ""
                security = parts[2].strip() if len(parts) > 2 else ""
                channel = parts[3].strip() if len(parts) > 3 else ""
                mode_val = parts[4].strip().lower() if len(parts) > 4 else ""
                networks.append({
                    'SSID': ssid,
                    'Signal': signal,
                    'Security': security,
                    'Channel': channel,
                    'Mode': mode_val
                })
        return networks

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = NetworkScanner()
    window.show()
    sys.exit(app.exec_())