import asyncio
from PyQt5.QtWidgets import QMainWindow, QLabel, QStatusBar, QVBoxLayout, QWidget, QPushButton
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl
from PyQt5.QtGui import QFont
from functions import open_website_with_proxy, get_current_ip
from selenium import webdriver
import chromedriver_autoinstaller


class BrowserWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setGeometry(100, 100, 1024, 768)

        self.browser = QWebEngineView()
        self.setCentralWidget(self.browser)

        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)

        self.ip_label = QLabel(self)
        self.ip_label.setFont(QFont("Arial", 10))
        self.statusBar.addWidget(self.ip_label)

        self.default_url = "https://www.pinksale.finance/launchpad/0x643D37ff8ee0A632BD64e4C4F666418ad00E9629?chain=ETH"
        self.browser.setUrl(QUrl(self.default_url))

        self.proxy = {
            "http": "http://login:password@p.webshare.io:80/",
            "https": "http://login:password@p.webshare.io:80/"
        }

        self.play_button = QPushButton("Play", self)
        self.play_button.clicked.connect(self.start_cycle)

        self.stop_button = QPushButton("Stop", self)
        self.stop_button.clicked.connect(self.stop_cycle)
        self.stop_button.setEnabled(False)

        self.top_bar_layout = QVBoxLayout()
        self.top_bar_layout.addWidget(self.play_button)
        self.top_bar_layout.addWidget(self.stop_button)

        self.top_bar_widget = QWidget()
        self.top_bar_widget.setLayout(self.top_bar_layout)

        self.setMenuWidget(self.top_bar_widget)

        self.refresh_enabled = False
        self.refresh_count = 0

        self.refresh_task = None
        self.repeat_task = None

        # Inicializace Selenium
        chromedriver_autoinstaller.install()
        self.selenium_driver = webdriver.Chrome()

    async def run_js_on_page(self, js_code):
        await self.browser.page().runJavaScript(js_code)

    async def execute_custom_actions(self):
        js_actions = [
            'const telegramLink = document.querySelector(\'a[href^="https://t.me"]:not([href*="pink"]) \'); telegramLink.click();',
            'const githubLink = document.querySelector(\'a[href^="https://github"]:not([href*="pink"]) \'); githubLink.click();',
            'const discordLink = document.querySelector(\'a[href^="https://discord.gg"]:not([href*="pink"]) \'); discordLink.click();',
            'document.querySelectorAll(\'.is-flex.mt-1.mb-2 a\')[1].click();',
            'document.querySelectorAll(\'.is-flex.mt-1.mb-2 a\')[2].click();'
        ]

        for js_action in js_actions:
            await self.run_js_on_page(js_action)

    async def refresh_page(self):
        url = self.browser.url().toString()

        try:
            response_text = open_website_with_proxy(url, self.proxy)

            if response_text:
                self.browser.setHtml(response_text, QUrl(url))
                self.refresh_count += 1
                self.statusBar.showMessage(f"Stránka obnovena (Refresh: {self.refresh_count})", 3000)
                await self.execute_custom_actions()
            else:
                print(f"Chyba při připojování k webu")
                self.statusBar.showMessage("Chyba při obnovování stránky", 3000)

        except requests.RequestException as e:
            print(f"Chyba při připojování k webu: {e}")
            self.statusBar.showMessage("Chyba při obnovování stránky", 3000)

    async def cycle_refresh(self):
        while self.refresh_enabled:
            await self.refresh_page()
            await asyncio.sleep(5)

    def start_cycle(self):
        self.refresh_enabled = True
        self.play_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.refresh_task = asyncio.ensure_future(self.cycle_refresh())

        # Spustíme akce v Selenium
        self.load_url_selenium(self.default_url)
        self.execute_actions_selenium()

    def stop_cycle(self):
        self.refresh_enabled = False
        self.play_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        if self.refresh_task and not self.refresh_task.done():
            self.refresh_task.cancel()

        # Ukončíme Selenium
        self.selenium_driver.quit()

    def update_ip_label(self):
        try:
            proxy_ip = get_current_ip()
            self.ip_label.setText(f'Připojen k proxy, IP adresa: {proxy_ip}')
        except requests.RequestException as e:
            self.ip_label.setText('Nepodařilo se získat IP adresu')

    # Nová funkce pro otevření stránky v Selenium
    def load_url_selenium(self, url):
        self.selenium_driver.get(url)

    # Nová funkce pro provádění akcí v Selenium
    def execute_actions_selenium(self):
        js_actions = [
            'const telegramLink = document.querySelector(\'a[href^="https://t.me"]:not([href*="pink"]) \'); telegramLink.click();',
            'const githubLink = document.querySelector(\'a[href^="https://github"]:not([href*="pink"]) \'); githubLink.click();',
            'const discordLink = document.querySelector(\'a[href^="https://discord.gg"]:not([href*="pink"]) \'); discordLink.click();',
            'document.querySelectorAll(\'.is-flex.mt-1.mb-2 a\')[1].click();',
            'document.querySelectorAll(\'.is-flex.mt-1.mb-2 a\')[2].click();'
        ]

        for js_action in js_actions:
            self.selenium_driver.execute_script(js_action)
