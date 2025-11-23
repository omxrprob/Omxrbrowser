import sys
from PyQt5.QtCore import QUrl, Qt, QSize
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QToolBar, QAction, QLineEdit,
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTextEdit,
    QMessageBox, QTabWidget, QComboBox, QCheckBox, QMenu, QSplitter
)
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage, QWebEngineProfile
from PyQt5.QtGui import QIcon, QKeySequence

# --- Internal Page Generator ---
class InternalPages:
    @staticmethod
    def get_home_html():
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Navi Browser</title>
            <style>
                body { font-family: 'Segoe UI', sans-serif; text-align: center; padding-top: 50px; background-color: #fff; color: #333; }
                h1 { font-size: 3em; color: #007bff; margin-bottom: 10px; }
                .search-box { padding: 12px; width: 400px; border: 2px solid #ddd; border-radius: 25px; font-size: 16px; outline: none; }
                .search-box:focus { border-color: #007bff; }
                .links { margin-top: 20px; }
                a { color: #666; text-decoration: none; margin: 0 10px; font-weight: 500; }
                a:hover { color: #007bff; }
            </style>
        </head>
        <body>
            <h1>Navi Browser</h1>
            <p>The browser built for you.</p>
            <div class="links">
                <a href="Navi://pw">My Sites</a> •
                <a href="Navi://cws">Extensions</a> •
                <a href="Navi://proxy">Proxy</a> •
                <a href="Navi://info">Info</a>
            </div>
        </body>
        </html>
        """

    @staticmethod
    def get_info_html():
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Navi Info</title>
            <style>
                body { font-family: 'Segoe UI', sans-serif; line-height: 1.6; padding: 40px; max-width: 800px; margin: 0 auto; }
                h1 { border-bottom: 2px solid #007bff; padding-bottom: 10px; color: #007bff; }
                .discord-box { background: #5865F2; color: white; padding: 20px; border-radius: 8px; text-align: center; margin: 20px 0; }
                .discord-box a { color: white; font-weight: bold; font-size: 1.2em; text-decoration: none; }
            </style>
        </head>
        <body>
            <h1>About Navi Browser</h1>
            <p>Navi is a lightweight, Python-based browser capable of internal website hosting, custom extension scripting, and proxy management.</p>
            
            <h2>Community</h2>
            <div class="discord-box">
                <p>Join our Community!</p>
                <a href="https://discord.gg/64um79VVMa">Click to Join Discord Server</a>
            </div>

            <h2>Documentation (Navi://)</h2>
            <ul>
                <li><b>Navi://pw</b> - Personal Website Builder. Create HTML/CSS/JS sites locally.</li>
                <li><b>Navi://cws</b> - Custom Web Store. Inject your own JavaScript into pages.</li>
                <li><b>Navi://proxy</b> - Configure API keys for web proxying.</li>
            </ul>
        </body>
        </html>
        """

# --- Website Builder Window ---
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
        
        # Inputs
        self.domain_input = QLineEdit()
        self.domain_input.setPlaceholderText("site-name")
        if self.domain_to_edit: 
            self.domain_input.setReadOnly(True)
        layout.addWidget(QLabel("Domain Name (.pw-Navi added automatically):"))
        layout.addWidget(self.domain_input)

        self.title_input = QLineEdit()
        layout.addWidget(QLabel("Page Title:"))
        layout.addWidget(self.title_input)

        self.content_input = QTextEdit()
        self.content_input.setPlaceholderText("<!DOCTYPE html>...")
        layout.addWidget(QLabel("HTML Content:"))
        layout.addWidget(self.content_input)

        save_btn = QPushButton("Save Site")
        save_btn.clicked.connect(self.save_data)
        save_btn.setStyleSheet("background: #2ECC71; color: white; padding: 8px; font-weight: bold;")
        layout.addWidget(save_btn)

        self.setLayout(layout)

    def load_data(self):
        if self.domain_to_edit:
            data = self.browser_main.personal_websites.get(self.domain_to_edit.lower())
            if data:
                self.domain_input.setText(self.domain_to_edit.replace(".pw-navi", ""))
                self.title_input.setText(data.get('title', ''))
                self.content_input.setText(data.get('html_content', ''))

    def save_data(self):
        prefix = self.domain_input.text().strip().lower()
        if not prefix: return
        full_domain = f"{prefix}.pw-navi"
        
        self.browser_main.personal_websites[full_domain] = {
            'domain': full_domain,
            'title': self.title_input.text().strip(),
            'html_content': self.content_input.toPlainText()
        }
        self.browser_main.add_new_tab(QUrl(f"local://{full_domain}/"))
        self.close()

# --- Browser Tab Class ---
class BrowserTab(QWebEngineView):
    def __init__(self, parent_window):
        super().__init__()
        self.parent_window = parent_window
        self.page().loadFinished.connect(self.inject_user_scripts)

    def inject_user_scripts(self, ok):
        if not ok: return
        # Inject all active extensions (JS)
        for name, script_data in self.parent_window.extensions.items():
            if script_data['active']:
                print(f"Injecting extension: {name}")
                self.page().runJavaScript(script_data['code'])

    def createWindow(self, _type):
        # Handle target="_blank" by creating a new tab
        return self.parent_window.add_new_tab()

# --- Main Browser Window ---
class NaviBrowser(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Navi Browser Ultimate")
        self.resize(1200, 800)
        self.setStyleSheet("QMainWindow { background-color: #ffffff; } QTabWidget::pane { border: 0; }")

        # Data Storage
        self.personal_websites = {}
        self.extensions = {} # Format: {'name': {'code': '...', 'active': True}}
        self.proxy_settings = {'type': 'None', 'key': '', 'url': ''}
        self.dark_mode = False

        # Default Site
        self.personal_websites['welcome.pw-navi'] = {
            'title': 'Welcome',
            'html_content': InternalPages.get_home_html() # Pre-load home structure
        }

        self.setup_ui()
        # Load Home
        self.add_new_tab(QUrl("local://navi/"))

    def setup_ui(self):
        # Toolbar
        self.toolbar = QToolBar()
        self.toolbar.setMovable(False)
        self.toolbar.setStyleSheet("QToolBar { background: #f0f0f0; border-bottom: 1px solid #ccc; padding: 5px; }")
        self.addToolBar(self.toolbar)

        # Actions
        self.toolbar.addAction("←", self.go_back)
        self.toolbar.addAction("→", self.go_forward)
        self.toolbar.addAction("⟳", self.reload_page)
        self.toolbar.addAction("🏠", self.go_home)

        # URL Bar
        self.url_bar = QLineEdit()
        self.url_bar.setPlaceholderText("Search or enter address...")
        self.url_bar.setStyleSheet("padding: 6px; border-radius: 4px; border: 1px solid #ccc;")
        self.url_bar.returnPressed.connect(self.navigate_from_bar)
        self.toolbar.addWidget(self.url_bar)

        # Add Tab Button
        add_tab_btn = QAction("+", self)
        add_tab_btn.triggered.connect(lambda: self.add_new_tab())
        self.toolbar.addAction(add_tab_btn)

        # Settings Menu
        settings_btn = QPushButton("☰")
        settings_btn.setFlat(True)
        settings_menu = QMenu()
        
        toggle_dark = QAction("Toggle Dark Mode", self)
        toggle_dark.triggered.connect(self.toggle_theme)
        settings_menu.addAction(toggle_dark)
        
        settings_btn.setMenu(settings_menu)
        self.toolbar.addWidget(settings_btn)

        # Tabs System
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.tabs.currentChanged.connect(self.update_url_bar)
        self.setCentralWidget(self.tabs)

    # --- Tab Management ---
    def add_new_tab(self, qurl=None, label="New Tab"):
        if qurl is None:
            qurl = QUrl("local://navi/")

        browser = BrowserTab(self)
        browser.setUrl(qurl)
        
        # Connect signals
        browser.urlChanged.connect(lambda q, b=browser: self.update_url_bar_from_tab(q, b))
        browser.titleChanged.connect(lambda t, b=browser: self.update_tab_title(t, b))
        
        i = self.tabs.addTab(browser, label)
        self.tabs.setCurrentIndex(i)
        return browser

    def close_tab(self, i):
        if self.tabs.count() < 2:
            return # Don't close last tab
        self.tabs.removeTab(i)

    def update_tab_title(self, title, browser):
        index = self.tabs.indexOf(browser)
        if index != -1:
            self.tabs.setTabText(index, title[:15] + "..." if len(title) > 15 else title)

    # --- Navigation Logic ---
    def go_back(self): self.tabs.currentWidget().back()
    def go_forward(self): self.tabs.currentWidget().forward()
    def reload_page(self): self.tabs.currentWidget().reload()
    def go_home(self): self.tabs.currentWidget().setUrl(QUrl("local://navi/"))

    def navigate_from_bar(self):
        text = self.url_bar.text().strip()
        self.process_url(text)

    def process_url(self, text):
        browser = self.tabs.currentWidget()
        
        # Internal Navi Protocols
        if text.lower().startswith("navi://"):
            self.handle_internal_pages(text, browser)
            return

        # Personal Sites
        if text.lower().endswith(".pw-navi"):
            data = self.personal_websites.get(text.lower())
            if data:
                browser.setHtml(data['html_content'], QUrl(f"local://{text}/"))
                return

        # Standard Web
        url = QUrl(text)
        if "." not in text and " " in text:
            url = QUrl(f"https://www.google.com/search?q={text.replace(' ', '+')}")
        elif "://" not in text:
            url = QUrl("https://" + text)
        
        browser.setUrl(url)

    def update_url_bar(self, index):
        if index >= 0:
            url = self.tabs.widget(index).url().toString()
            self.update_bar_text(url)

    def update_url_bar_from_tab(self, q, browser):
        if browser == self.tabs.currentWidget():
            self.update_bar_text(q.toString())
            
            # Intercept clicks on Navi:// links inside pages
            if q.toString().lower().startswith("navi://"):
                self.handle_internal_pages(q.toString(), browser)

    def update_bar_text(self, url_str):
        if url_str.startswith("local://navi/"):
            clean = url_str.replace("local://navi/", "navi://").rstrip("/")
            self.url_bar.setText(clean)
        elif not url_str.startswith("local://"):
            self.url_bar.setText(url_str)

    # --- Internal Page Handlers ---
    def handle_internal_pages(self, url, browser):
        cmd = url.lower().replace("navi://", "").strip("/")
        
        if cmd == "" or cmd == "home":
            browser.setHtml(InternalPages.get_home_html(), QUrl("local://navi/"))
        elif cmd == "info":
            browser.setHtml(InternalPages.get_info_html(), QUrl("local://navi/info"))
        elif cmd == "pw":
            self.load_site_manager(browser)
        elif cmd == "cws":
            self.load_extension_manager(browser)
        elif cmd == "proxy":
            self.load_proxy_manager(browser)
        # Commands
        elif cmd == "pw/new":
            self.builder_window = WebsiteBuilderWindow(self)
            self.builder_window.show()
        elif cmd.startswith("pw/edit/"):
            domain = url.split("/")[-1]
            self.builder_window = WebsiteBuilderWindow(self, domain)
            self.builder_window.show()
        elif cmd.startswith("pw/delete/"):
            domain = url.split("/")[-1]
            self.delete_site(domain)

    # --- Special Page Generators ---
    
    def load_site_manager(self, browser):
        rows = ""
        for d, data in self.personal_websites.items():
            rows += f"""
            <div style='padding:10px; border-bottom:1px solid #eee; display:flex; justify-content:space-between;'>
                <b><a href='{d}'>{data['title']} ({d})</a></b>
                <div>
                    <a href='navi://pw/edit/{d}' style='color:orange; margin-right:10px;'>Edit</a>
                    <a href='navi://pw/delete/{d}' style='color:red;'>Delete</a>
                </div>
            </div>"""
            
        html = f"""<h1>Personal Websites</h1><a href='navi://pw/new'><button style='padding:10px; background:#2ECC71; color:white; border:none;'>+ New Site</button></a><br><br>{rows}"""
        browser.setHtml(self.wrap_internal(html), QUrl("local://navi/pw"))

    def load_extension_manager(self, browser):
        # Create a form to add JS
        js_list = ""
        for name, data in self.extensions.items():
            status = "Active" if data['active'] else "Inactive"
            color = "green" if data['active'] else "red"
            js_list += f"""
            <div style='background:#f9f9f9; padding:10px; margin:5px; border-left: 4px solid {color};'>
                <h3>{name} <span style='font-size:0.6em; color:{color};'>({status})</span></h3>
                <pre style='background:#eee; padding:5px;'>{data['code'][:50]}...</pre>
                <button onclick="window.location='navi://cws/toggle/{name}'">Toggle</button>
                <button onclick="window.location='navi://cws/delete/{name}'">Delete</button>
            </div>
            """
            
        html = f"""
        <h1>Navi Extensions (CWS)</h1>
        <p>Inject custom JavaScript into every page.</p>
        <div style="border:1px solid #ddd; padding:15px;">
            <h3>Create New Extension</h3>
            <input id="ex_name" placeholder="Extension Name"><br><br>
            <textarea id="ex_code" style="width:100%; height:100px;" placeholder="document.body.style.background = 'yellow';"></textarea><br>
            <button onclick="saveExt()">Save Extension</button>
        </div>
        <script>
        function saveExt() {{
            var name = document.getElementById('ex_name').value;
            var code = document.getElementById('ex_code').value;
            // Quick hack to send data via URL for python to catch
            window.location = 'navi://cws/save/' + encodeURIComponent(name) + '/' + encodeURIComponent(code);
        }}
        </script>
        <hr>
        {js_list}
        """
        browser.setHtml(self.wrap_internal(html), QUrl("local://navi/cws"))

    def load_proxy_manager(self, browser):
        html = f"""
        <h1>Navi Proxy Configuration</h1>
        <p>Configure an API to route traffic (Simulation/Headers).</p>
        <div style="background:#f0f8ff; padding:20px; border-radius:10px;">
            <label>Proxy API Type:</label>
            <select id="ptype">
                <option value="Google" {'selected' if self.proxy_settings['type']=='Google' else ''}>Google Cloud</option>
                <option value="Cloudflare" {'selected' if self.proxy_settings['type']=='Cloudflare' else ''}>Cloudflare</option>
            </select><br><br>
            <input id="pkey" placeholder="API Key" value="{self.proxy_settings['key']}" style="width:300px;"><br><br>
            <input id="purl" placeholder="Target URL to Proxy" style="width:300px;"><br><br>
            <button onclick="saveProxy()">Go with Proxy</button>
        </div>
        <script>
        function saveProxy() {{
            var type = document.getElementById('ptype').value;
            var key = document.getElementById('pkey').value;
            var url = document.getElementById('purl').value;
            window.location = 'navi://proxy/run/' + type + '/' + encodeURIComponent(key) + '/' + encodeURIComponent(url);
        }}
        </script>
        """
        browser.setHtml(self.wrap_internal(html), QUrl("local://navi/proxy"))

    # --- Logic for CWS/Proxy Data Handling ---
    def update_url_bar_from_tab(self, q, browser):
        url = q.toString()
        
        # Intercept Extension Saving
        if "navi://cws/save/" in url:
            parts = url.split("/save/")
            if len(parts) > 1:
                args = parts[1].split("/")
                name = QUrl.fromPercentEncoding(args[0].encode())
                code = QUrl.fromPercentEncoding(args[1].encode())
                self.extensions[name] = {'code': code, 'active': True}
                self.load_extension_manager(browser)
                return

        if "navi://cws/toggle/" in url:
            name = url.split("/toggle/")[-1]
            if name in self.extensions:
                self.extensions[name]['active'] = not self.extensions[name]['active']
            self.load_extension_manager(browser)
            return
            
        if "navi://cws/delete/" in url:
            name = url.split("/delete/")[-1]
            if name in self.extensions: del self.extensions[name]
            self.load_extension_manager(browser)
            return

        # Intercept Proxy Running
        if "navi://proxy/run/" in url:
            parts = url.split("/run/")
            args = parts[1].split("/")
            self.proxy_settings['type'] = args[0]
            self.proxy_settings['key'] = QUrl.fromPercentEncoding(args[1].encode())
            target_url = QUrl.fromPercentEncoding(args[2].encode())
            
            # Simulate Proxy by loading url with modified headers (conceptual)
            # In a real app, we'd use QWebEngineUrlRequestInterceptor
            QMessageBox.information(self, "Proxy Active", f"Using {args[0]} API.\nKey: {self.proxy_settings['key'][:5]}***\nLoading: {target_url}")
            browser.setUrl(QUrl(target_url))
            return

        # Normal updates
        if browser == self.tabs.currentWidget():
            self.update_bar_text(url)
            if url.lower().startswith("navi://"):
                self.handle_internal_pages(url, browser)

    def delete_site(self, domain):
        if domain in self.personal_websites:
            del self.personal_websites[domain]
            self.load_site_manager(self.tabs.currentWidget())

    def toggle_theme(self):
        self.dark_mode = not self.dark_mode
        if self.dark_mode:
            self.setStyleSheet("""
                QMainWindow, QTabWidget, QWidget { background-color: #2b2b2b; color: #ffffff; }
                QLineEdit { background: #444; color: #fff; border: 1px solid #555; }
                QToolBar { background: #333; border-bottom: 1px solid #111; }
            """)
        else:
            self.setStyleSheet("QMainWindow { background-color: #ffffff; }")

    def wrap_internal(self, content):
        return f"<html><body style='font-family:sans-serif; padding:20px; color:{'#fff' if self.dark_mode else '#000'}'>{content}</body></html>"

if __name__ == '__main__':
    app = QApplication(sys.argv)
    QApplication.setApplicationName("Navi Browser")
    window = NaviBrowser()
    window.show()
    sys.exit(app.exec_())

