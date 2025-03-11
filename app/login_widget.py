from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                            QLineEdit, QPushButton, QMessageBox, QInputDialog)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QIcon
import sqlite3
import hashlib

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

        hashed_password = self.hash_password(password)

        if self.authenticate_user(username, hashed_password):
            self.accept()
        else:
            QMessageBox.warning(self, "Login Error", 
                              "Invalid username or password.")

    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()

    def authenticate_user(self, username, hashed_password):
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, hashed_password))
        user = cursor.fetchone()
        conn.close()
        return user is not None

    def handle_register(self):
        username, ok1 = QInputDialog.getText(self, "Register", "Enter username:")
        if not ok1 or not username:
            return

        password, ok2 = QInputDialog.getText(self, "Register", "Enter password:", QLineEdit.Password)
        if not ok2 or not password:
            return

        hashed_password = self.hash_password(password)

        if self.save_user_credentials(username, hashed_password):
            QMessageBox.information(self, "Register", "Registration successful!")
        else:
            QMessageBox.warning(self, "Register Error", "Username already exists.")

    def handle_forgot_password(self):
        username, ok = QInputDialog.getText(self, "Password Recovery", "Enter username:")
        if not ok or not username:
            return

        new_password, ok = QInputDialog.getText(self, "Password Recovery", "Enter new password:", QLineEdit.Password)
        if not ok or not new_password:
            return

        hashed_password = self.hash_password(new_password)

        if self.update_user_password(username, hashed_password):
            QMessageBox.information(self, "Password Recovery", "Password updated successfully!")
        else:
            QMessageBox.warning(self, "Password Recovery Error", "Username not found.")

    def save_user_credentials(self, username, hashed_password):
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        finally:
            conn.close()

    def update_user_password(self, username, hashed_password):
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET password=? WHERE username=?", (hashed_password, username))
        conn.commit()
        updated = cursor.rowcount > 0
        conn.close()
        return updated

# Author: Brandon Myers
# GitHub: https://github.com/BAMmyers/AgentricGUI.git
