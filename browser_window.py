import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QPushButton
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QTimer, QUrl

import requests
import time

class BrowserApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setGeometry(100, 100, 800, 600)

        self.browser = QWebEngineView()
        self.browser.load(QUrl("https://www.pinksale.finance/launchpad/0x643D37ff8ee0A632BD64e4C4F666418ad00E9629?chain=ETH"))

        self.play_button = QPushButton("Play", self)
        self.play_button.clicked.connect(self.start_cycle)

        self.stop_button = QPushButton("Stop", self)
        self.stop_button.clicked.connect(self.stop_cycle)
        self.stop_button.setEnabled(False)

        self.ip_label = QLabel(self)
        self.ip_label.setText("Current Proxy IP Address: N/A")

        self.repetitions_label = QLabel(self)
        self.repetitions_label.setText("Number of Repetitions: 0")

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.play_button)
        self.layout.addWidget(self.stop_button)
        self.layout.addWidget(self.ip_label)
        self.layout.addWidget(self.repetitions_label)
        self.layout.addWidget(self.browser)

        self.central_widget = QWidget(self)
        self.central_widget.setLayout(self.layout)

        self.setCentralWidget(self.central_widget)

        self.refresh_enabled = False
        self.refresh_count = 0

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refresh_page)

    def start_cycle(self):
        self.play_button.setEnabled(False)
        self.stop_button.setEnabled(True)

        self.refresh_enabled = True
        self.refresh_count = 0

        self.cycle_refresh()

    def stop_cycle(self):
        self.refresh_enabled = False
        self.play_button.setEnabled(True)
        self.stop_button.setEnabled(False)

    def cycle_refresh(self):
        self.timer.start(5000)  # Start the timer that triggers refresh_page every 5 seconds

    def refresh_page(self):
        try:
            self.browser.page().runJavaScript('location.reload();')  # Trigger a page reload using JavaScript
            self.execute_custom_actions()

            self.refresh_count += 1
            self.update_labels()

        except Exception as e:
            print(f"Error refreshing page: {e}")

    def execute_custom_actions(self):
        # Add your custom JavaScript actions here
        pass

    def update_labels(self):
        proxy_connection = self.check_proxy_connection()
        if proxy_connection:
            self.ip_label.setText(f"Current Proxy IP Address: {get_current_ip()}")
        else:
            self.ip_label.setText("Failed to connect via proxy")
        self.repetitions_label.setText(f"Number of Repetitions: {self.refresh_count}")

    def check_proxy_connection(self):
        try:
            response = requests.get(
                "https://ipv4.webshare.io/",
                proxies={
                    "http": "http://login:password@p.webshare.io:80/",
                    "https": "http://login:password@p.webshare.io:80/"
                }
            )
            response.raise_for_status()
            return True
        except requests.exceptions.RequestException as e:
            print(f"Error connecting to proxy: {e}")
            return False

# Add the following code to get the current proxy IP address
def get_current_ip():
    try:
        response = requests.get('https://api.ipify.org')
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Failed to retrieve IP address: {e}")
        return None

if __name__ == '__main__':
    app = QApplication(sys.argv)
    browser_app = BrowserApp()
    browser_app.show()
    sys.exit(app.exec_())
