from PyQt5.QtWidgets import (QMainWindow, QTabWidget, QWidget, QVBoxLayout,
                             QLabel, QPushButton, QLineEdit, QFileDialog,
                             QFormLayout, QTextEdit, QDockWidget, QHBoxLayout,
                             QComboBox, QMessageBox)
import logging
from PyQt5.QtCore import Qt
from NodeGraphQt import NodeGraph, setup_context_menu
from app.nodes.agent_node import AgentNode
from app.nodes.api_node import APINode
from app.nodes.base_node import BaseNode
from app.utils import call_gemini_assistant, check_for_updates
import json
import os
import uuid
import sys

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

        # Add toolbar for flow control
        toolbar = QWidget()
        toolbar_layout = QHBoxLayout(toolbar)
        toolbar_layout.setContentsMargins(10, 10, 10, 10)
        
        # Run flow button
        self.run_flow_btn = QPushButton("Run Flow")
        self.run_flow_btn.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                border: none;
                padding: 8px 15px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
            QPushButton:pressed {
                background-color: #219a52;
            }
        """)
        self.run_flow_btn.clicked.connect(self.execute_flow)
        toolbar_layout.addWidget(self.run_flow_btn)
        
        # Reset flow button
        self.reset_flow_btn = QPushButton("Reset")
        self.reset_flow_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                padding: 8px 15px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
            QPushButton:pressed {
                background-color: #a93226;
            }
        """)
        self.reset_flow_btn.clicked.connect(self.reset_flow)
        toolbar_layout.addWidget(self.reset_flow_btn)
        
        toolbar_layout.addStretch()
        self.create_tab_layout.addWidget(toolbar)

        # Create the node graph
        self.graph = NodeGraph()
        self.graph_widget = self.graph.widget
        self.create_tab_layout.addWidget(self.graph_widget)
        setup_context_menu(self.graph)

        # Register custom nodes
        self.graph.register_node(AgentNode)
        self.graph.register_node(APINode)
        self.graph.register_node(BaseNode)
        
        # Initialize flow engine
        from app.flow_engine import FlowEngine
        self.flow_engine = FlowEngine(self.graph)

        # --- Console Tab Setup ---
        self.console_tab_layout = QVBoxLayout(self.console_tab)
        
        # Add console output
        self.console_output = QTextEdit()
        self.console_output.setReadOnly(True)
        self.console_output.setStyleSheet("""
            QTextEdit {
                background-color: #2c3e50;
                color: #ecf0f1;
                font-family: monospace;
                padding: 10px;
                border: none;
            }
        """)
        self.console_tab_layout.addWidget(self.console_output)
        
        # Setup logging to console
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger('AgentricGUI')
        
        # Custom handler to redirect logs to console widget
        class QTextEditHandler(logging.Handler):
            def __init__(self, widget):
                super().__init__()
                self.widget = widget

            def emit(self, record):
                msg = self.format(record)
                self.widget.append(msg)
        
        console_handler = QTextEditHandler(self.console_output)
        console_handler.setFormatter(
            logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        )
        self.logger.addHandler(console_handler)

        # --- Settings Tab Setup ---
        self.settings_tab_layout = QFormLayout(self.settings_tab)
        self.api_key_input = QLineEdit()
        self.settings_tab_layout.addRow("API Key:", self.api_key_input)

        # Experience Level Dropdown
        self.experience_level_combo = QComboBox()
        self.experience_level_combo.addItems(["Novice", "Moderate", "Expert"])
        self.experience_level_combo.currentTextChanged.connect(
            self.update_ui_for_experience_level)
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
        self.assistant_output.setReadOnly(True)
        self.assistant_layout.addWidget(self.assistant_output)

        # --- Load settings on startup ---
        self.load_settings()

        # --- Check for updates and kill switch ---
        self.check_for_updates_and_kill_switch()

        self.update_ui_for_experience_level()
        self.setup_initial_nodes()
        
        # Log startup complete
        self.logger.info("AgentricGUI initialized successfully")

    def setup_initial_nodes(self):
        """Create initial nodes in the graph."""
        try:
            # Create an agent node
            agent_node = self.graph.create_node(
                'agentric.AgentNode',
                name='MyAgent',
                pos=[0, 0]
            )
            
            # Create an API node
            api_node = self.graph.create_node(
                'agentric.APINode',
                name='GeminiAPI',
                pos=[300, 0]
            )
            
            self.logger.info("Initial nodes created successfully")
            
        except Exception as e:
            self.logger.error(f"Error creating initial nodes: {str(e)}")

    def execute_flow(self):
        """Execute the current node graph flow."""
        try:
            self.logger.info("Starting flow execution...")
            self.console_output.clear()
            
            # Validate connections
            if not self.flow_engine.validate_connections():
                self.logger.error("Flow validation failed - check node connections")
                return
            
            # Run the flow
            success = self.flow_engine.run_flow()
            
            if success:
                self.logger.info("Flow execution completed successfully")
            else:
                self.logger.error("Flow execution failed - check console for details")
                
        except Exception as e:
            self.logger.error(f"Error executing flow: {str(e)}")

    def reset_flow(self):
        """Reset the flow state of all nodes."""
        try:
            self.flow_engine.reset_flow()
            self.console_output.clear()
            self.logger.info("Flow reset complete")
        except Exception as e:
            self.logger.error(f"Error resetting flow: {str(e)}")

    def save_settings(self):
        settings = {
            "api_key": self.api_key_input.text(),
            "experience_level": self.experience_level_combo.currentText(),
            "installation_id": self.installation_id
        }
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Settings",
                                                    os.path.join(".", "settings.json"),
                                                    "JSON Files (*.json)")
        if file_path:
            with open(file_path, 'w') as f:
                json.dump(settings, f)
            print(f"Settings saved to {file_path}")

    def load_settings(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Load Settings",
                                                    os.path.join(".", "settings.json"),
                                                    "JSON Files (*.json)")
        if file_path:
            try:
                with open(file_path, 'r') as f:
                    settings = json.load(f)
                    self.api_key_input.setText(settings.get("api_key", ""))
                    self.experience_level_combo.setCurrentText(settings.get("experience_level", "Novice"))
                    self.installation_id = settings.get("installation_id", str(uuid.uuid4()))

                print(f"Settings loaded from {file_path}")
            except FileNotFoundError:
                print("Settings file not found. Creating with defaults.")
                self.installation_id = str(uuid.uuid4())
                self.save_settings()
            except json.JSONDecodeError:
                print("Invalid JSON format in settings file.")
                self.installation_id = str(uuid.uuid4())
                self.save_settings()

        else:
            self.installation_id = str(uuid.uuid4())
            self.save_settings()

    def send_to_assistant(self):
        user_input = self.assistant_input.toPlainText()
        if user_input.strip() == "":
            return

        self.assistant_output.append(f"You: {user_input}")
        self.assistant_input.clear()

        try:
            response = call_gemini_assistant(user_input, self.graph)
            if not response:
                self.assistant_output.append("Assistant: No response received.")
            else:
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
        else:
            self.setup_expert_graph()

    def setup_novice_graph(self):
        self.graph.clear()
        self.graph.create_node('agentric.AgentNode', name='MyAgent', pos=[0, 0]).set_property('purpose', 'Respond to questions')

    def setup_moderate_graph(self):
        self.graph.clear()
        self.graph.create_node('agentric.AgentNode', name='MyAgent', pos=[0, 0])
        self.graph.create_node('agentric.APINode', name='GeminiAPI', pos=[300, 0])

    def setup_expert_graph(self):
        self.graph.clear()
        self.graph.create_node('agentric.AgentNode', name='MyAgent', pos=[0, 0])
        self.graph.create_node('agentric.APINode', name='GeminiAPI', pos=[300, 0])

    def check_for_updates_and_kill_switch(self):
        latest_version, update_url, blacklist = check_for_updates(self.installation_id)

        if latest_version is None:
            print("Error checking for updates.")
            return

        if blacklist is True:
            QMessageBox.critical(self, "Application Disabled",
                                 "This installation of AgentricGUI has been disabled due to a violation of the Terms of Service. "
                                 "Please contact support for more information.")
            sys.exit()

        current_version = "0.0.1"
        if latest_version > current_version:
            msg_box = QMessageBox()
            msg_box.setWindowTitle("Update Available")
            msg_box.setText(f"A new version ({latest_version}) is available.  Do you want to update?")
            msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            msg_box.setDefaultButton(QMessageBox.Yes)
            msg_box.setDetailedText(f"Update URL: {update_url}")

            if msg_box.exec_() == QMessageBox.Yes:
                import webbrowser
                webbrowser.open(update_url)
</create_file>
