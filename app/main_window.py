from PyQt5.QtWidgets import (QMainWindow, QTabWidget, QWidget, QVBoxLayout,
                             QLabel, QPushButton, QLineEdit, QFileDialog,
                             QCheckBox, QFormLayout, QTextEdit, QDockWidget,
                             QComboBox, QMessageBox)  # Added QMessageBox
from PyQt5.QtCore import Qt
from NodeGraphQt import NodeGraph, setup_context_menu
from app.nodes.agent_node import AgentNode
from app.nodes.api_node import APINode
from app.nodes.base_node import BaseNode
from app.utils import call_gemini_assistant, check_for_updates  # Import check_for_updates
import json
import os
import uuid  # Import the uuid module


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("AgentricGUI")

        # --- Main Layout ---
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)

        # --- Tab Widget ---
        self.tab_widget = QTabWidget()
        self.main_layout.addWidget(self.tab_widget)

        # Create tabs
        self.create_tab = QWidget()
        self.console_tab = QWidget()
        self.settings_tab = QWidget()

        self.tab_widget.addTab(self.create_tab, "Create")
        self.tab_widget.addTab(self.console_tab, "Console")
        self.tab_widget.addTab(self.settings_tab, "Settings")

        # --- Create Tab Setup ---
        self.create_tab_layout = QVBoxLayout(self.create_tab)
        self.create_tab_layout.setContentsMargins(0, 0, 0, 0)

        # Create the node graph
        self.graph = NodeGraph()
        self.graph_widget = self.graph.widget
        self.create_tab_layout.addWidget(self.graph_widget)
        setup_context_menu(self.graph)

        # Register custom nodes
        self.graph.register_node(AgentNode)
        self.graph.register_node(APINode)
        self.graph.register_node(BaseNode)

        # --- Console Tab Setup ---
        self.console_tab_layout = QVBoxLayout(self.console_tab)
        self.console_label = QLabel("Console Output Will Appear Here")
        self.console_tab_layout.addWidget(self.console_label)

        # --- Settings Tab Setup ---
        self.settings_tab_layout = QFormLayout(self.settings_tab)
        self.api_key_input = QLineEdit()
        self.settings_tab_layout.addRow("API Key:", self.api_key_input)

        # Experience Level Dropdown
        self.experience_level_combo = QComboBox()
        self.experience_level_combo.addItems(["Novice", "Moderate", "Expert"])
        self.experience_level_combo.currentTextChanged.connect(self.update_ui_for_experience_level)  # Connect to a slot
        self.settings_tab_layout.addRow("Experience Level:", self.experience_level_combo)

        self.save_settings_button = QPushButton("Save Settings")
        self.save_settings_button.clicked.connect(self.save_settings)
        self.settings_tab_layout.addRow(self.save_settings_button)

        self.load_settings_button = QPushButton("Load Settings")
        self.load_settings_button.clicked.connect(self.load_settings)
        self.settings_tab_layout.addRow(self.load_settings_button)

        # --- Assistant Panel (Dock Widget) ---
        self.assistant_dock = QDockWidget("AI Assistant", self)
        self.addDockWidget(Qt.RightDockWidgetArea, self.assistant_dock)
        self.assistant_widget = QWidget()
        self.assistant_layout = QVBoxLayout(self.assistant_widget)
        self.assistant_dock.setWidget(self.assistant_widget)


        self.assistant_input = QTextEdit()
        self.assistant_input.setPlaceholderText("Ask the AI assistant...")
        self.assistant_layout.addWidget(self.assistant_input)

        self.send_button = QPushButton("Send")
        self.send_button.clicked.connect(self.send_to_assistant)
        self.assistant_layout.addWidget(self.send_button)

        self.assistant_output = QTextEdit()
        self.assistant_output.setReadOnly(True)  # Make the output read-only
        self.assistant_layout.addWidget(self.assistant_output)


        # --- Load settings on startup ---
        self.load_settings()

        # --- Check for updates and kill switch ---
        self.check_for_updates_and_kill_switch()


        self.update_ui_for_experience_level()
        # Initial Node setup (Example)
        self.setup_initial_nodes()

    def setup_initial_nodes(self):
        agent_node = self.graph.create_node('agentric.AgentNode', name='MyAgent', pos=[0, 0])
        api_node = self.graph.create_node('agentric.APINode', name='GeminiAPI', pos=[300, 0])

    def save_settings(self):
        settings = {
            "api_key": self.api_key_input.text(),
            "experience_level": self.experience_level_combo.currentText(),
            "installation_id": self.installation_id  # Save the installation ID
        }
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Settings", os.path.join(".", "settings.json"), "JSON Files (*.json)")
        if file_path:
            with open(file_path, 'w') as f:
                json.dump(settings, f)
            print(f"Settings saved to {file_path}")

    def load_settings(self):
        #  Load settings, and generate a unique ID if it doesn't exist
        file_path, _ = QFileDialog.getOpenFileName(self, "Load Settings", os.path.join(".", "settings.json"), "JSON Files (*.json)")
        if file_path:
            try:
                with open(file_path, 'r') as f:
                    settings = json.load(f)
                    self.api_key_input.setText(settings.get("api_key", ""))
                    self.experience_level_combo.setCurrentText(settings.get("experience_level", "Novice"))
                    # Load or generate installation ID
                    self.installation_id = settings.get("installation_id", str(uuid.uuid4()))

                print(f"Settings loaded from {file_path}")
            except FileNotFoundError:
                print("Settings file not found. Creating with defaults.")
                self.installation_id = str(uuid.uuid4()) # Generate on first run
                self.save_settings() # Save defaults
            except json.JSONDecodeError:
                print("Invalid JSON format in settings file.")
                self.installation_id = str(uuid.uuid4()) # Generate on error
                self.save_settings()

        else: #If no file selected, generate an ID
             self.installation_id = str(uuid.uuid4())
             self.save_settings()


    def send_to_assistant(self):
        user_input = self.assistant_input.toPlainText()
        if user_input.strip() == "":
            return

        self.assistant_output.append(f"You: {user_input}")
        self.assistant_input.clear()

        try:
            response = call_gemini_assistant(user_input, self.api_key_input.text(), self.graph)
            self.assistant_output.append(f"Assistant: {response}")
        except Exception as e:
            self.assistant_output.append(f"Assistant: Error: {e}")

    def update_ui_for_experience_level(self):
        experience_level = self.experience_level_combo.currentText()

        for node in self.graph.all_nodes():
            if node.type_ == 'agentric.APINode':
                if experience_level == "Novice":
                    node.action_button.setVisible(False)
                else:
                    node.action_button.setVisible(True)

        if experience_level == "Novice":
            self.setup_novice_graph()
        elif experience_level == "Moderate":
            self.setup_moderate_graph()
        else:  # Expert
           self.setup_expert_graph()

    def setup_novice_graph(self):
        self.graph.clear()
        agent_node = self.graph.create_node('agentric.AgentNode', name='MyAgent', pos=[0, 0])
        agent_node.set_property('purpose', 'Respond to questions')

    def setup_moderate_graph(self):
        self.graph.clear()
        agent_node = self.graph.create_node('agentric.AgentNode', name='MyAgent', pos=[0, 0])
        api_node = self.graph.create_node('agentric.APINode', name='GeminiAPI', pos=[300, 0])
    def setup_expert_graph(self):
        self.graph.clear()
        # The expert level can start with an empty graph, or you can add some
        # basic nodes if you prefer.
        agent_node = self.graph.create_node('agentric.AgentNode', name='MyAgent', pos=[0, 0])
        api_node = self.graph.create_node('agentric.APINode', name='GeminiAPI', pos=[300, 0])

    def check_for_updates_and_kill_switch(self):
        latest_version, update_url, blacklist = check_for_updates(self.installation_id)

        if latest_version is None:  # Error checking for updates
            # Handle the error appropriately (e.g., show a message to the user)
            print("Error checking for updates.")
            return

        if blacklist is True:
             QMessageBox.critical(self, "Application Disabled",
                                 "This installation of AgentricGUI has been disabled due to a violation of the Terms of Service. "
                                 "Please contact support for more information.")
             sys.exit() #Exit program

        current_version = "0.0.1"  # Replace with your actual versioning scheme
        if latest_version > current_version:
            msg_box = QMessageBox()
            msg_box.setWindowTitle("Update Available")
            msg_box.setText(f"A new version ({latest_version}) is available.  Do you want to update?")
            msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            msg_box.setDefaultButton(QMessageBox.Yes)
            msg_box.setDetailedText(f"Update URL: {update_url}") #Show details with URL

            if msg_box.exec_() == QMessageBox.Yes:
                # Open the update URL in the user's default web browser
                import webbrowser
                webbrowser.open(update_url)
