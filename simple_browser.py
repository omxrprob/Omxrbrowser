import sys
from PyQt5.QtCore import QUrl, QRegExp
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QToolBar, QAction, QLineEdit,
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTextEdit
)
from PyQt5.QtWebEngineWidgets import QWebEngineView

# --- Personal Website Builder Window ---
class WebsiteBuilderWindow(QWidget):
    def __init__(self, browser_main):
        super().__init__()
        self.browser_main = browser_main
        self.setWindowTitle("Personal Website Builder (.pw-Navi)")
        self.setGeometry(200, 200, 600, 500)
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Domain Input
        domain_layout = QHBoxLayout()
        self.domain_input = QLineEdit()
        self.domain_input.setPlaceholderText("your-site-name")
        domain_layout.addWidget(QLabel("Domain:"))
        domain_layout.addWidget(self.domain_input)
        domain_layout.addWidget(QLabel(".pw-Navi (Required Suffix)"))
        layout.addLayout(domain_layout)

        # Title Input
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("My Awesome Personal Page")
        layout.addWidget(QLabel("Page Title:"))
        layout.addWidget(self.title_input)

        # Content Input (HTML Area)
        layout.addWidget(QLabel("Page Content (HTML/Text):"))
        self.content_input = QTextEdit()
        self.content_input.setPlaceholderText("Enter your text, images using <img> tags, or embedded iframes here...")
        layout.addWidget(self.content_input)

        # Save Button
        save_btn = QPushButton("Save & Preview Site")
        save_btn.setStyleSheet("background-color: #4CAF50; color: white; padding: 10px; font-weight: bold;")
        save_btn.clicked.connect(self.save_data)
        layout.addWidget(save_btn)

        self.setLayout(layout)

    def load_data(self):
        """Loads existing site data into the form."""
        data = self.browser_main.personal_website_data
        if data.get('domain'):
            # Strip the suffix for display in the input box
            self.domain_input.setText(data['domain'].replace(".pw-Navi", ""))
        self.title_input.setText(data.get('title', ''))
        self.content_input.setText(data.get('content', ''))

    def save_data(self):
        """Saves data to the main browser instance and triggers a preview."""
        domain_prefix = self.domain_input.text().strip().lower()
        
        if not domain_prefix:
            # Simple error handling (replacing the forbidden alert)
            self.title_input.setText("ERROR: Domain prefix cannot be empty.")
            return

        full_domain = f"{domain_prefix}.pw-Navi"

        self.browser_main.personal_website_data = {
            'domain': full_domain,
            'title': self.title_input.text().strip() or "Untitled Navi Page",
            'content': self.content_input.toPlainText().strip()
        }
        
        print(f"Personal Website saved to: {full_domain}")

        # Automatically navigate to the new custom domain after saving
        self.browser_main.url_bar.setText(full_domain)
        self.browser_main.navigate_to_url()
        self.close()

# --- Main Browser Application ---
class SimpleBrowser(QMainWindow):
    # Data structure to hold the single user-created website content (in-memory)
    # Default placeholder data
    personal_website_data = {
        'domain': 'welcome.pw-Navi',
        'title': 'Welcome to your Navi Site!',
        'content': '''
        <h1 style="color: #333; font-family: sans-serif;">Hello World!</h1>
        <p style="font-family: sans-serif;">This is your private, in-browser website. 
        Edit this content by clicking the 🌐 button in the toolbar.</p>
        <p style="font-family: sans-serif; color: #007bff;">Try adding an image URL here:</p>
        <img src="https://placehold.co/400x150/007bff/ffffff?text=Your+Image" alt="Placeholder" style="border-radius: 8px;">
        '''
    }

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Navi Browser")
        self.setGeometry(100, 100, 1200, 800)

        self.browser = QWebEngineView()
        self.browser.setUrl(QUrl("https://www.google.com"))
        self.setCentralWidget(self.browser)

        # --- Navbar Setup ---
        navbar = QToolBar("Navigation")
        navbar.setMovable(False)
        self.addToolBar(navbar)

        # Navigation Buttons
        back_btn = QAction("← Back", self); back_btn.triggered.connect(self.browser.back); navbar.addAction(back_btn)
        forward_btn = QAction("→ Forward", self); forward_btn.triggered.connect(self.browser.forward); navbar.addAction(forward_btn)
        reload_btn = QAction("⟳ Reload", self); reload_btn.triggered.connect(self.browser.reload); navbar.addAction(reload_btn)
        stop_btn = QAction("🛑 Stop", self); stop_btn.triggered.connect(self.browser.stop); navbar.addAction(stop_btn)
        home_btn = QAction("🏠 Home", self); home_btn.triggered.connect(self.navigate_home); navbar.addAction(home_btn)
        
        # New Feature Button
        builder_btn = QAction("🌐 Builder", self)
        builder_btn.triggered.connect(self.show_website_builder)
        navbar.addAction(builder_btn)

        # URL/Search Bar
        self.url_bar = QLineEdit()
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        navbar.addWidget(self.url_bar)

        # --- Signal Connections ---
        self.browser.urlChanged.connect(self.update_url)
        self.browser.titleChanged.connect(self.setWindowTitle)
        
        self.builder_window = None # Keep a reference to the builder window

    def show_website_builder(self):
        """Opens the personal website builder window."""
        # Prevent opening multiple builder windows
        if self.builder_window is None:
            self.builder_window = WebsiteBuilderWindow(self)
            self.builder_window.show()
        else:
            self.builder_window.show()
            self.builder_window.activateWindow()

    def generate_personal_site_html(self):
        """Generates the full HTML content for the personal site."""
        data = self.personal_website_data
        
        # Create a simple HTML document with embedded styles
        html_content = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{data['title']}</title>
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    background-color: #f4f7f6;
                    color: #333;
                    padding: 30px;
                    margin: 0;
                }}
                .container {{
                    max-width: 800px;
                    margin: 0 auto;
                    background-color: white;
                    padding: 20px;
                    border-radius: 12px;
                    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
                }}
                h1 {{ color: #007bff; border-bottom: 2px solid #007bff; padding-bottom: 10px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <p style="font-size: 0.8em; color: #888; text-align: right;">Viewing local site: {data['domain']}</p>
                {data['content']}
            </div>
        </body>
        </html>
        """
        return html_content

    def navigate_home(self):
        """Navigates to the default home page."""
        self.browser.setUrl(QUrl("https://www.google.com"))

    def navigate_to_url(self):
        """
        Navigates to the entered URL, performs a search, or loads the custom site.
        """
        url = self.url_bar.text().strip()
        
        # --- NEW FEATURE: Custom Domain Check ---
        if url.lower().endswith(".pw-navi"):
            domain = self.personal_website_data.get('domain', '').lower()
            if url.lower() == domain:
                html = self.generate_personal_site_html()
                # Load custom HTML directly into the browser
                self.browser.setHtml(html, QUrl(f"local://{domain}/")) # Use local URL to keep URL bar updated
                self.setWindowTitle(self.personal_website_data.get('title', 'Navi Site'))
                return

        # Regular navigation/search logic
        if url.startswith(("http://", "https://")):
            self.browser.setUrl(QUrl(url))
        elif "." in url:
            self.browser.setUrl(QUrl("http://" + url))
        else:
            search_query = url.replace(" ", "+")
            search_url = f"https://www.google.com/search?q={search_query}"
            self.browser.setUrl(QUrl(search_url))

    def update_url(self, q):
        """Updates the text in the address bar when the browser navigates."""
        url_str = q.toString()
        # Only update the URL bar if it's not our internal local URL representation
        if not url_str.startswith("local://"):
            self.url_bar.setText(url_str)
            self.url_bar.setCursorPosition(0)

if __name__ == '__main__':
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)

    QApplication.setApplicationName("Navi Browser")
    window = SimpleBrowser()
    window.show()
    try:
        sys.exit(app.exec_())
    except SystemExit:
        pass

