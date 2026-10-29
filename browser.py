import os

os.environ["QTWEBENGINE_DISABLE_SANDBOX"] = "1"

import sys
from PyQt5.QtCore import QUrl
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWidgets import (
    QApplication,
    QComboBox,
    QDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)


class AccountDialog(QDialog):

  def __init__(self, parent=None):
    super().__init__(parent)
    self.setWindowTitle("Atlas Account")
    self.resize(340, 240)
    self.setStyleSheet("""
            QDialog {
                background-color: #1e1e2e;
                color: #cdd6f4;
                font-family: 'Segoe UI', sans-serif;
            }
            QLabel {
                color: #89b4fa;
                font-size: 13px;
                font-weight: 600;
            }
            QLineEdit {
                background-color: #313244;
                color: #cdd6f4;
                border: 1px solid #45475a;
                border-radius: 6px;
                padding: 6px;
                font-size: 13px;
            }
            QLineEdit:focus {
                border: 1px solid #89b4fa;
            }
            QPushButton {
                background-color: #89b4fa;
                color: #11111b;
                border: none;
                border-radius: 6px;
                padding: 8px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #b4befe;
            }
        """)

    layout = QFormLayout()

    self.login_input = QLineEdit()
    self.login_input.setPlaceholderText("Gmail / Phone Number")

    self.password_input = QLineEdit()
    self.password_input.setEchoMode(QLineEdit.Password)
    self.password_input.setPlaceholderText("Password")

    layout.addRow(QLabel("Email / Phone:"), self.login_input)
    layout.addRow(QLabel("Password:"), self.password_input)

    self.login_btn = QPushButton("Sign In")
    self.login_btn.clicked.connect(self.handle_login)
    layout.addRow(self.login_btn)

    self.setLayout(layout)
    self.user_data = None

  def handle_login(self):
    identifier = self.login_input.text().strip()
    password = self.password_input.text().strip()

    if not identifier or not password:
      QMessageBox.warning(self, "Error", "Please enter valid credentials")
      return

    self.user_data = {"identifier": identifier, "logged_in": True}
    QMessageBox.information(
        self, "Success", f"Logged in successfully:\n{identifier}"
    )
    self.accept()


class SettingsDialog(QDialog):

  def __init__(self, parent=None):
    super().__init__(parent)
    self.setWindowTitle("Settings")
    self.resize(300, 160)
    self.setStyleSheet("""
            QDialog {
                background-color: #1e1e2e;
                color: #cdd6f4;
                font-family: 'Segoe UI', sans-serif;
            }
            QLabel {
                color: #89b4fa;
                font-size: 13px;
                font-weight: 600;
            }
            QComboBox {
                background-color: #313244;
                color: #cdd6f4;
                border: 1px solid #45475a;
                border-radius: 6px;
                padding: 6px;
                font-size: 13px;
            }
            QPushButton {
                background-color: #89b4fa;
                color: #11111b;
                border: none;
                border-radius: 6px;
                padding: 8px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #b4befe;
            }
        """)

    layout = QFormLayout()

    self.lang_box = QComboBox()
    self.lang_box.addItems(
        ["English (en-US)", "العربية (ar)", "Français (fr)"]
    )

    layout.addRow(QLabel("Language:"), self.lang_box)

    save_btn = QPushButton("Save")
    save_btn.clicked.connect(self.accept)
    layout.addRow(save_btn)

    self.setLayout(layout)


class AtlasBrowser(QMainWindow):

  def __init__(self):
    super().__init__()
    self.setWindowTitle("Atlas Browser")

    self.setGeometry(100, 100, 1100, 700)
    self.setMinimumSize(360, 500)

    self.current_lang = "en-US"
    self.current_user = None

    self.tabs = QTabWidget()
    self.tabs.setDocumentMode(True)
    self.tabs.setTabsClosable(True)
    self.tabs.tabCloseRequested.connect(self.close_tab)
    self.tabs.currentChanged.connect(self.tab_changed)

    self.setStyleSheet("""
            QMainWindow {
                background-color: #181825;
            }
            QTabWidget::pane {
                border: none;
            }
            QTabBar::tab {
                background-color: #1e1e2e;
                color: #a6adc8;
                border: 1px solid #313244;
                padding: 8px 16px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                font-family: 'Segoe UI', sans-serif;
                font-size: 12px;
                font-weight: 500;
                max-width: 140px;
            }
            QTabBar::tab:selected {
                background-color: #313244;
                color: #89b4fa;
                border-bottom: 2px solid #89b4fa;
                font-weight: 600;
            }
            QLineEdit {
                background-color: #1e1e2e;
                color: #cdd6f4;
                border: 1px solid #313244;
                border-radius: 8px;
                padding: 6px 12px;
                font-size: 13px;
                font-family: 'Segoe UI', sans-serif;
            }
            QLineEdit:focus {
                border: 1px solid #89b4fa;
            }
            QPushButton {
                background-color: #1e1e2e;
                color: #cdd6f4;
                border: 1px solid #313244;
                border-radius: 8px;
                padding: 6px 10px;
                font-size: 13px;
                font-family: 'Segoe UI', sans-serif;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #313244;
                color: #89b4fa;
                border: 1px solid #89b4fa;
            }
        """)

    self.url_bar = QLineEdit()
    self.url_bar.setPlaceholderText("Enter URL...")
    self.url_bar.returnPressed.connect(self.navigate_to_url)

    self.search_bar = QLineEdit()
    self.search_bar.setPlaceholderText("🔍 Search...")
    self.search_bar.returnPressed.connect(self.perform_search)

    nav_layout = QHBoxLayout()
    nav_layout.setContentsMargins(8, 8, 8, 8)
    nav_layout.setSpacing(6)

    back_btn = QPushButton("◀")
    back_btn.setFixedWidth(34)
    back_btn.clicked.connect(
        lambda: self.current_browser().back()
        if self.current_browser()
        else None
    )
    nav_layout.addWidget(back_btn)

    forward_btn = QPushButton("▶")
    forward_btn.setFixedWidth(34)
    forward_btn.clicked.connect(
        lambda: self.current_browser().forward()
        if self.current_browser()
        else None
    )
    nav_layout.addWidget(forward_btn)

    reload_btn = QPushButton("🔄")
    reload_btn.setFixedWidth(34)
    reload_btn.clicked.connect(
        lambda: self.current_browser().reload()
        if self.current_browser()
        else None
    )
    nav_layout.addWidget(reload_btn)

    nav_layout.addWidget(self.url_bar, 2)
    nav_layout.addWidget(self.search_bar, 1)

    add_tab_btn = QPushButton("+")
    add_tab_btn.setFixedWidth(34)
    add_tab_btn.clicked.connect(lambda: self.add_home_tab())
    nav_layout.addWidget(add_tab_btn)

    self.account_btn = QPushButton("👤 Account")
    self.account_btn.clicked.connect(self.open_account)
    nav_layout.addWidget(self.account_btn)

    settings_btn = QPushButton("⚙️")
    settings_btn.setFixedWidth(34)
    settings_btn.clicked.connect(self.open_settings)
    nav_layout.addWidget(settings_btn)

    main_layout = QVBoxLayout()
    main_layout.setContentsMargins(0, 0, 0, 0)
    main_layout.addLayout(nav_layout)
    main_layout.addWidget(self.tabs)

    container = QWidget()
    container.setLayout(main_layout)
    self.setCentralWidget(container)

    self.add_home_tab()

  def add_home_tab(self):
    browser = QWebEngineView()
    html_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body {
                    background-color: #181825;
                    color: #cdd6f4;
                    font-family: 'Segoe UI', sans-serif;
                    display: flex;
                    flex-direction: column;
                    justify-content: center;
                    align-items: center;
                    min-height: 85vh;
                    margin: 0;
                    padding: 10px;
                    box-sizing: border-box;
                }
                .logo {
                    font-size: 48px;
                    font-weight: 700;
                    color: #89b4fa;
                    margin-bottom: 6px;
                    letter-spacing: 1px;
                }
                .subtitle {
                    font-size: 14px;
                    color: #a6adc8;
                    margin-bottom: 30px;
                }
            </style>
        </head>
        <body>
            <div class="logo">Atlas Engine</div>
            <div class="subtitle">Custom Search Engine</div>
        </body>
        </html>
        """
    browser.setHtml(html_content)

    i = self.tabs.addTab(browser, "Atlas Home")
    self.tabs.setCurrentIndex(i)

    browser.urlChanged.connect(
        lambda qurl, browser=browser: self.update_urlbar(qurl, browser)
    )
    # ربط حدث انتهاء التحميل بحذف الشعارات تلقائياً
    browser.loadFinished.connect(
        lambda ok, browser=browser: self.clean_page_branding(browser)
    )

  def clean_page_branding(self, browser):
    # إخفاء الشعار وشريط البحث العلوي التابع لـ Google عبر JS
    js_script = """
        (function() {
            var logo = document.getElementById('logo') || document.querySelector('img[alt="Google"]') || document.querySelector('.logo');
            if (logo) { logo.style.display = 'none'; }
            var header = document.getElementById('header') || document.querySelector('header');
            if (header) { header.style.display = 'none'; }
            var searchHeader = document.querySelector('form[role="search"]');
            if (searchHeader && window.location.href.includes('google')) {
                searchHeader.style.visibility = 'hidden';
            }
        })();
        """
    browser.page().runJavaScript(js_script)

  def close_tab(self, i):
    if self.tabs.count() < 2:
      return
    self.tabs.removeTab(i)

  def tab_changed(self, i):
    if self.current_browser():
      qurl = self.current_browser().url()
      self.update_urlbar(qurl, self.current_browser())

  def current_browser(self):
    return self.tabs.currentWidget()

  def update_urlbar(self, q, browser=None):
    if browser != self.current_browser():
      return
    url_str = q.toString()
    if (
        not url_str
        or url_str.startswith("about:")
        or url_str.startswith("data:")
    ):
      self.url_bar.setText("atlas://home")
    else:
      self.url_bar.setText(url_str)

  def open_account(self):
    dlg = AccountDialog(parent=self)
    if dlg.exec_():
      if dlg.user_data:
        self.current_user = dlg.user_data["identifier"]
        display_name = self.current_user.split("@")[0]
        self.account_btn.setText(f"👤 {display_name[:10]}")

  def open_settings(self):
    dlg = SettingsDialog(parent=self)
    if dlg.exec_():
      lang_idx = dlg.lang_box.currentIndex()
      langs = ["en-US", "ar", "fr"]
      self.current_lang = langs[lang_idx]

      if self.current_browser():
        profile = self.current_browser().page().profile()
        profile.setHttpAcceptLanguage(self.current_lang)

  def navigate_to_url(self):
    text = self.url_bar.text().strip()
    if text == "atlas://home" or text == "":
      self.add_home_tab()
      return

    if not text.startswith("http://") and not text.startswith("https://"):
      url = "https://" + text
    else:
      url = text

    if self.current_browser():
      self.current_browser().setUrl(QUrl(url))

  def perform_search(self):
    query = self.search_bar.text().strip()
    if query:
      url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
      if self.current_browser():
        self.current_browser().setUrl(QUrl(url))


app = QApplication(sys.argv)
window = AtlasBrowser()
window.show()
sys.exit(app.exec_())