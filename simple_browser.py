import sys
import json
import os
from PyQt5.QtCore import QUrl, Qt, QSize
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QToolBar, QAction, QLineEdit,
    QWidget, QVBoxLayout, QLabel, QPushButton, QTextEdit,
    QMessageBox, QTabWidget, QMenu, QFrame, QSizePolicy
)
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage

# --- Constants & Styles ---
DATA_FILE = "navi_data.json"

class ModernStyles:
    @staticmethod
    def light_mode():
        return """
        QMainWindow { background-color: #f8f9fa; }
        QTabWidget::pane { border: 0; background: #ffffff; }
        QTabBar::tab {
            background: #e9ecef; color: #495057; padding: 8px 20px;
            border-top-left-radius: 8px; border-top-right-radius: 8px;
            margin-right: 2px; font-family: 'Segoe UI'; font-size: 12px;
        }
        QTabBar::tab:selected { background: #ffffff; color: #007bff; font-weight: bold; }
        QToolBar { background: #ffffff; border-bottom: 1px solid #dee2e6; padding: 5px; spacing: 10px; }
        QLineEdit {
            background: #f1f3f5; border: 1px solid transparent; border-radius: 15px;
            padding: 6px 15px; color: #212529; font-size: 13px;
        }
        QLineEdit:focus { background: #ffffff; border: 1px solid #007bff; }
        QPushButton { background: transparent; border: none; border-radius: 4px; padding: 4px; }
        QPushButton:hover { background: #e9ecef; }
        """

    @staticmethod
    def dark_mode():
        return """
        QMainWindow { background-color: #212529; }
        QTabWidget::pane { border: 0; background: #2b3035; }
        QTabBar::tab {
            background: #343a40; color: #adb5bd; padding: 8px 20px;
            border-top-left-radius: 8px; border-top-right-radius: 8px;
            margin-right: 2px; font-family: 'Segoe UI'; font-size: 12px;
        }
        QTabBar::tab:selected { background: #2b3035; color: #6ea8fe; font-weight: bold; }
        QToolBar { background: #2b3035; border-bottom: 1px solid #495057; padding: 5px; spacing: 10px; }
        QLineEdit {
            background: #343a40; border: 1px solid transparent; border-radius: 15px;
            padding: 6px 15px; color: #f8f9fa; font-size: 13px;
        }
        QLineEdit:focus { background: #212529; border: 1px solid #6ea8fe; }
        QPushButton { background: transparent; border: none; border-radius: 4px; padding: 4px; color: #f8f9fa; }
        QPushButton:hover { background: #495057; }
        QMenu { background: #343a40; color: #f8f9fa; border: 1px solid #495057; }
        QMenu::item:selected { background: #0d6efd; }
        """

# --- Custom Page Handler ---
class NaviWebPage(QWebEnginePage):
    def acceptNavigationRequest(self, url, _type, isMainFrame):
        # Intercept internal schemes
        if url.scheme() == "navi":
            view = self.view()
            if view and hasattr(view, 'parent_window'):
                view.parent_window.handle_internal_pages(url.toString(), view)
            return False
        return super().acceptNavigationRequest(url, _type, isMainFrame)

# --- Internal Pages HTML Generator ---
class InternalPages:
    @staticmethod
    def css(dark_mode=False):
        bg = "#2b3035" if dark_mode else "#f8f9fa"
        card_bg = "#343a40" if dark_mode else "#ffffff"
        text = "#f8f9fa" if dark_mode else "#212529"
        border = "#495057" if dark_mode else "#dee2e6"
        
        return f"""
        body {{ font-family: 'Segoe UI', sans-serif; background-color: {bg}; color: {text}; padding: 40px; margin: 0; }}
        .container {{ max-width: 800px; margin: 0 auto; }}
        h1 {{ color: #0d6efd; font-weight: 300; font-size: 2.5em; margin-bottom: 10px; }}
        .card {{ 
            background: {card_bg}; border: 1px solid {border}; border-radius: 12px; 
            padding: 20px; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        }}
        .btn {{
            padding: 8px 16px; background-color: #0d6efd; color: white; border: none; border-radius: 6px; 
            cursor: pointer; font-size: 14px; text-decoration: none; display: inline-block;
        }}
        .btn:hover {{ background-color: #0b5ed7; }}
        .btn-danger {{ background-color: #dc3545; }}
        .btn-danger:hover {{ background-color: #bb2d3b; }}
        input, textarea, select {{
            width: 100%; padding: 10px; margin: 10px 0; border: 1px solid {border}; border-radius: 6px;
            background: {bg}; color: {text}; box-sizing: border-box;
        }}
        input:focus {{ outline: 2px solid #0d6efd; }}
        a {{ color: #0d6efd; text-decoration: none; }}
        pre {{ background: {bg}; padding: 10px; border-radius: 6px; overflow-x: auto; }}
        .nav-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 15px; margin-top: 30px; }}
        .nav-item {{ 
            display: block; background: {card_bg}; padding: 20px; text-align: center; 
            border-radius: 12px; border: 1px solid {border}; transition: transform 0.2s;
        }}
        .nav-item:hover {{ transform: translateY(-5px); border-color: #0d6efd; }}
        """

    @staticmethod
    def home(dark_mode):
        return f"""
        <html><head><style>{InternalPages.css(dark_mode)}</style></head><body>
        <div class="container" style="text-align: center; margin-top: 10vh;">
            <h1>Navi Browser</h1>
            <p style="font-size: 1.2em; opacity: 0.7;">Simple. Fast. Customizable.</p>
            <div class="nav-grid">
                <a href="navi://pw" class="nav-item"><b>My Sites</b><br>Build & Host</a>
                <a href="navi://cws" class="nav-item"><b>Extensions</b><br>Scripting</a>
                <a href="navi://proxy" class="nav-item"><b>Proxy</b><br>Config</a>
                <a href="navi://info" class="nav-item"><b>Info</b><br>About</a>
            </div>
        </div>
        </body></html>
        """

# --- Site Builder ---
class WebsiteBuilderWindow(QWidget):
    def __init__(self, browser_main, domain_to_edit=None):
        super().__init__()
        self.browser_main = browser_main
        self.domain_to_edit = domain_to_edit
        self.setWindowTitle(f"Builder - {domain_to_edit or 'New'}")
        self.resize(900, 700)
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        
        self.domain_input = QLineEdit()
        self.domain_input.setPlaceholderText("site-name")
        if self.domain_to_edit: self.domain_input.setReadOnly(True)
        
        layout.addWidget(QLabel("Domain Name (without suffix):"))
        layout.addWidget(self.domain_input)
        
        self.title_input = QLineEdit()
        layout.addWidget(QLabel("Page Title:"))
        layout.addWidget(self.title_input)
        
        self.content_input = QTextEdit()
        self.content_input.setPlaceholderText("<!DOCTYPE html>...")
        layout.addWidget(QLabel("HTML Code:"))
        layout.addWidget(self.content_input)
        
        save_btn = QPushButton("Save Site")
        save_btn.setStyleSheet("background: #2ECC71; color: white; padding: 12px; border-radius: 6px; font-weight: bold;")
        save_btn.clicked.connect(self.save_data)
        layout.addWidget(save_btn)
        
        self.setLayout(layout)

    def load_data(self):
        if self.domain_to_edit:
            data = self.browser_main.data['sites'].get(self.domain_to_edit.lower())
            if data:
                self.domain_input.setText(self.domain_to_edit.replace(".pw-navi", ""))
                self.title_input.setText(data.get('title', ''))
                self.content_input.setText(data.get('html_content', ''))

    def save_data(self):
        prefix = self.domain_input.text().strip().lower()
        if not prefix: return
        full_domain = f"{prefix}.pw-navi"
        
        self.browser_main.data['sites'][full_domain] = {
            'domain': full_domain,
            'title': self.title_input.text().strip(),
            'html_content': self.content_input.toPlainText()
        }
        self.browser_main.save_to_disk()
        self.browser_main.add_new_tab(QUrl(f"local://{full_domain}/"))
        self.close()

# --- Browser Tab ---
class BrowserTab(QWebEngineView):
    def __init__(self, parent_window):
        super().__init__()
        self.parent_window = parent_window
        self.setPage(NaviWebPage(self))
        self.page().loadFinished.connect(self.inject_user_scripts)

    def inject_user_scripts(self, ok):
        if not ok: return
        for name, script_data in self.parent_window.data['extensions'].items():
            if script_data['active']:
                self.page().runJavaScript(script_data['code'])

    def createWindow(self, _type):
        return self.parent_window.add_new_tab()

# --- Main Window ---
class NaviBrowser(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Navi Browser Ultimate")
        self.resize(1280, 850)
        
        # Default Data Structure
        self.data = {
            'sites': {},
            'extensions': {},
            'proxy': {'type': 'Google', 'key': '', 'url': ''},
            'dark_mode': False
        }
        
        self.load_from_disk()
        self.setup_ui()
        self.apply_theme()
        
        self.add_new_tab(QUrl("local://navi/"))

    def setup_ui(self):
        # Toolbar
        toolbar = QToolBar()
        toolbar.setMovable(False)
        toolbar.setIconSize(QSize(18, 18))
        self.addToolBar(toolbar)

        # Standard Actions
        nav_actions = [
            ("←", self.go_back), ("→", self.go_forward), 
            ("⟳", self.reload_page), ("🏠", self.go_home)
        ]
        for text, slot in nav_actions:
            btn = QPushButton(text)
            btn.setFixedSize(30, 30)
            btn.clicked.connect(slot)
            toolbar.addWidget(btn)

        # URL Bar
        self.url_bar = QLineEdit()
        self.url_bar.setPlaceholderText("Search Google or enter address...")
        self.url_bar.returnPressed.connect(self.navigate_from_bar)
        toolbar.addWidget(self.url_bar)

        # Add Tab
        add_btn = QPushButton("+")
        add_btn.setFixedSize(30, 30)
        add_btn.clicked.connect(lambda: self.add_new_tab())
        toolbar.addWidget(add_btn)

        # Menu
        menu_btn = QPushButton("☰")
        menu_btn.setFixedSize(30, 30)
        menu = QMenu()
        theme_action = QAction("Toggle Dark Mode", self)
        theme_action.triggered.connect(self.toggle_theme)
        menu.addAction(theme_action)
        menu_btn.setMenu(menu)
        toolbar.addWidget(menu_btn)

        # Tabs
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.tabs.currentChanged.connect(self.update_url_bar)
        self.setCentralWidget(self.tabs)

    # --- Persistence ---
    def save_to_disk(self):
        try:
            with open(DATA_FILE, 'w') as f:
                json.dump(self.data, f)
        except Exception as e:
            print(f"Save Error: {e}")

    def load_from_disk(self):
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, 'r') as f:
                    loaded = json.load(f)
                    self.data.update(loaded)
            except Exception as e:
                print(f"Load Error: {e}")

    # --- Tab Logic ---
    def add_new_tab(self, qurl=None, label="New Tab"):
        if qurl is None: qurl = QUrl("local://navi/")
        browser = BrowserTab(self)
        browser.setUrl(qurl)
        browser.urlChanged.connect(lambda q, b=browser: self.update_url_bar_from_tab(q, b))
        browser.titleChanged.connect(lambda t, b=browser: self.update_tab_title(t, b))
        i = self.tabs.addTab(browser, label)
        self.tabs.setCurrentIndex(i)
        return browser

    def close_tab(self, i):
        if self.tabs.count() > 1:
            self.tabs.removeTab(i)

    def update_tab_title(self, title, browser):
        i = self.tabs.indexOf(browser)
        if i != -1:
            self.tabs.setTabText(i, title[:15] + "..." if len(title) > 15 else title)

    # --- Navigation ---
    def go_back(self): self.tabs.currentWidget().back()
    def go_forward(self): self.tabs.currentWidget().forward()
    def reload_page(self): self.tabs.currentWidget().reload()
    def go_home(self): self.tabs.currentWidget().setUrl(QUrl("local://navi/"))
    
    def navigate_from_bar(self):
        self.process_url(self.url_bar.text().strip())

    def process_url(self, text):
        browser = self.tabs.currentWidget()
        if text.lower().startswith("navi://"):
            self.handle_internal_pages(text, browser)
            return
        
        if text.lower().endswith(".pw-navi"):
            data = self.data['sites'].get(text.lower())
            if data:
                browser.setHtml(data['html_content'], QUrl(f"local://{text}/"))
                return
        
        url = QUrl(text)
        if "." not in text and " " in text:
            url = QUrl(f"https://www.google.com/search?q={text.replace(' ', '+')}")
        elif "://" not in text:
            url = QUrl("https://" + text)
        browser.setUrl(url)

    def update_url_bar(self, i):
        if i >= 0: self.update_bar_text(self.tabs.widget(i).url().toString())

    def update_url_bar_from_tab(self, q, browser):
        if browser == self.tabs.currentWidget():
            self.update_bar_text(q.toString())
        if q.scheme() == "navi":
            self.handle_internal_pages(q.toString(), browser)

    def update_bar_text(self, url):
        if url.startswith("local://navi/"):
            clean = url.replace("local://navi/", "navi://").rstrip("/")
            self.url_bar.setText(clean)
        elif not url.startswith("local://"):
            self.url_bar.setText(url)

    # --- Internal Pages Logic ---
    def handle_internal_pages(self, url, browser):
        cmd = url.lower().replace("navi://", "").strip("/")
        dm = self.data['dark_mode']
        
        if cmd == "" or cmd == "home":
            browser.setHtml(InternalPages.home(dm), QUrl("local://navi/"))
        elif cmd == "info":
            html = f"""<html><head><style>{InternalPages.css(dm)}</style></head><body>
            <div class="container">
                <h1>About Navi</h1>
                <div class="card">
                    <p>Version: Ultimate 1.0</p>
                    <p>A lightweight, custom-engine browser for developers.</p>
                    <a href="https://discord.gg/64um79VVMa" class="btn" style="background:#5865F2">Join Discord</a>
                </div>
            </div></body></html>"""
            browser.setHtml(html, QUrl("local://navi/info"))
        elif cmd == "pw":
            self.render_site_manager(browser)
        elif cmd == "cws":
            self.render_extension_manager(browser)
        elif cmd == "proxy":
            self.render_proxy_manager(browser)
        elif cmd == "pw/new":
            self.builder_window = WebsiteBuilderWindow(self)
            self.builder_window.show()
        elif cmd.startswith("pw/edit/"):
            self.builder_window = WebsiteBuilderWindow(self, url.split("/")[-1])
            self.builder_window.show()
        elif cmd.startswith("pw/delete/"):
            d = url.split("/")[-1]
            if d in self.data['sites']: del self.data['sites'][d]
            self.save_to_disk()
            self.render_site_manager(browser)

    def render_site_manager(self, browser):
        dm = self.data['dark_mode']
        rows = ""
        for d, val in self.data['sites'].items():
            rows += f"""
            <div class="card" style="display:flex; justify-content:space-between; align-items:center;">
                <div><b>{val['title']}</b><br><small>{d}</small></div>
                <div>
                    <a href="{d}" class="btn">Visit</a>
                    <a href="navi://pw/edit/{d}" class="btn" style="background:#fd7e14">Edit</a>
                    <a href="navi://pw/delete/{d}" class="btn btn-danger">Delete</a>
                </div>
            </div>"""
        html = f"""<html><head><style>{InternalPages.css(dm)}</style></head><body>
        <div class="container">
            <h1>My Sites</h1>
            <a href="navi://pw/new" class="btn" style="background:#198754">+ New Website</a><br><br>
            {rows}
        </div></body></html>"""
        browser.setHtml(html, QUrl("local://navi/pw"))

    def render_extension_manager(self, browser):
        dm = self.data['dark_mode']
        rows = ""
        for k, v in self.data['extensions'].items():
            color = "#198754" if v['active'] else "#dc3545"
            status = "Active" if v['active'] else "Inactive"
            rows += f"""
            <div class="card" style="border-left: 5px solid {color}">
                <h3>{k} <small>({status})</small></h3>
                <pre>{v['code'][:60]}...</pre>
                <button class="btn" onclick="window.location='navi://cws/toggle/{k}'">Toggle</button>
                <button class="btn btn-danger" onclick="window.location='navi://cws/delete/{k}'">Delete</button>
            </div>"""
        html = f"""<html><head><style>{InternalPages.css(dm)}</style></head><body>
        <div class="container">
            <h1>Extensions</h1>
            <div class="card">
                <h3>New Script</h3>
                <input id="name" placeholder="Name (e.g., DarkMode)"><br>
                <textarea id="code" style="height:100px" placeholder="document.body.style.background='black';"></textarea>
                <button class="btn" onclick="save()">Install</button>
            </div>
            {rows}
        </div>
        <script>
        function save() {{
            var n = document.getElementById('name').value;
            var c = document.getElementById('code').value;
            if(n && c) window.location = 'navi://cws/save/'+encodeURIComponent(n)+'/'+encodeURIComponent(c);
        }}
        </script></body></html>"""
        browser.setHtml(html, QUrl("local://navi/cws"))

    def render_proxy_manager(self, browser):
        dm = self.data['dark_mode']
        p = self.data['proxy']
        html = f"""<html><head><style>{InternalPages.css(dm)}</style></head><body>
        <div class="container">
            <h1>Proxy Config</h1>
            <div class="card">
                <label>Service:</label>
                <select id="type">
                    <option value="Google" {'selected' if p['type']=='Google' else ''}>Google Cloud</option>
                    <option value="Cloudflare" {'selected' if p['type']=='Cloudflare' else ''}>Cloudflare</option>
                </select>
                <label>API Key:</label>
                <input id="key" value="{p['key']}">
                <label>Target URL:</label>
                <input id="url" placeholder="https://example.com">
                <button class="btn" onclick="run()">Connect</button>
            </div>
        </div>
        <script>
        function run() {{
            var t = document.getElementById('type').value;
            var k = document.getElementById('key').value;
            var u = document.getElementById('url').value;
            if(u) window.location = 'navi://proxy/run/'+t+'/'+encodeURIComponent(k)+'/'+encodeURIComponent(u);
        }}
        </script></body></html>"""
        browser.setHtml(html, QUrl("local://navi/proxy"))

    # --- Action Handlers ---
    def toggle_theme(self):
        self.data['dark_mode'] = not self.data['dark_mode']
        self.save_to_disk()
        self.apply_theme()
        self.reload_page() # Reload to update internal page CSS

    def apply_theme(self):
        if self.data['dark_mode']:
            self.setStyleSheet(ModernStyles.dark_mode())
        else:
            self.setStyleSheet(ModernStyles.light_mode())

    # --- URL Handling Logic for CWS/Proxy ---
    def update_url_bar_from_tab(self, q, browser):
        url = q.toString()
        if "navi://cws/save/" in url:
            try:
                parts = url.split("/save/")[1].split("/")
                n = QUrl.fromPercentEncoding(parts[0].encode())
                c = QUrl.fromPercentEncoding(parts[1].encode())
                self.data['extensions'][n] = {'code': c, 'active': True}
                self.save_to_disk()
                self.render_extension_manager(browser)
            except: pass
            return
        if "navi://cws/toggle/" in url:
            n = url.split("/toggle/")[-1]
            if n in self.data['extensions']:
                self.data['extensions'][n]['active'] = not self.data['extensions'][n]['active']
                self.save_to_disk()
            self.render_extension_manager(browser)
            return
        if "navi://cws/delete/" in url:
            n = url.split("/delete/")[-1]
            if n in self.data['extensions']:
                del self.data['extensions'][n]
                self.save_to_disk()
            self.render_extension_manager(browser)
            return
        if "navi://proxy/run/" in url:
            try:
                parts = url.split("/run/")[1].split("/")
                self.data['proxy']['type'] = parts[0]
                self.data['proxy']['key'] = QUrl.fromPercentEncoding(parts[1].encode())
                target = QUrl.fromPercentEncoding(parts[2].encode())
                self.save_to_disk()
                QMessageBox.information(self, "Proxy", f"Simulating Connection via {parts[0]}...")
                browser.setUrl(QUrl(target))
            except: pass
            return

        if browser == self.tabs.currentWidget():
            self.update_bar_text(url)
        if url.startswith("navi://"):
            self.handle_internal_pages(url, browser)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    QApplication.setApplicationName("Navi Browser")
    window = NaviBrowser()
    window.show()
    sys.exit(app.exec_())


