from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                            QLineEdit, QPushButton, QMessageBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QIcon

class LoginWidget(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Welcome to AgentricGUI")
        self.setMinimumWidth(400)
        self.setup_ui()
        self.apply_styles()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(40, 40, 40, 40)

        # Header
        header = QLabel("Welcome to AgentricGUI")
        header_font = QFont()
        header_font.setPointSize(16)
        header_font.setBold(True)
        header.setFont(header_font)
        header.setAlignment(Qt.AlignCenter)
        layout.addWidget(header)

        # Username/Email field
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Username or Email")
        layout.addWidget(self.username_input)

        # Password field
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password_input)

        # Login button
        self.login_btn = QPushButton("Login")
        self.login_btn.setMinimumHeight(40)
        self.login_btn.clicked.connect(self.handle_login)
        layout.addWidget(self.login_btn)

        # Bottom buttons container
        bottom_layout = QHBoxLayout()
        bottom_layout.setSpacing(10)

        # Register button
        self.register_btn = QPushButton("Register")
        self.register_btn.clicked.connect(self.handle_register)
        bottom_layout.addWidget(self.register_btn)

        # Forgot Password button
        self.forgot_btn = QPushButton("Forgot Password")
        self.forgot_btn.clicked.connect(self.handle_forgot_password)
        bottom_layout.addWidget(self.forgot_btn)

        layout.addLayout(bottom_layout)

    def apply_styles(self):
        # Modern flat style
        self.setStyleSheet("""
            QDialog {
                background-color: #ffffff;
            }
            QLabel {
                color: #2c3e50;
            }
            QLineEdit {
                padding: 10px;
                border: 2px solid #e0e0e0;
                border-radius: 5px;
                background-color: #f5f6fa;
                color: #2c3e50;
                font-size: 14px;
            }
            QLineEdit:focus {
                border-color: #3498db;
            }
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #2475a8;
            }
            #register_btn, #forgot_btn {
                background-color: #95a5a6;
            }
            #register_btn:hover, #forgot_btn:hover {
                background-color: #7f8c8d;
            }
        """)

    def handle_login(self):
        username = self.username_input.text()
        password = self.password_input.text()

        if not username or not password:
            QMessageBox.warning(self, "Login Error", 
                              "Please enter both username and password.")
            return

        # TODO: Implement actual authentication
        # For now, accept any non-empty credentials
        self.accept()

    def handle_register(self):
        QMessageBox.information(self, "Register", 
                              "Registration feature coming soon!")

    def handle_forgot_password(self):
        QMessageBox.information(self, "Password Recovery", 
                              "Password recovery feature coming soon!")
