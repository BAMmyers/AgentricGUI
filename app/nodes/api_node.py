
from app.nodes.base_node import BaseNode
import requests
import json
from PyQt5.QtWidgets import QPushButton


class APINode(BaseNode):
    NODE_NAME = 'API'

    def __init__(self):
        super().__init__()
        self.add_input('in')
        self.add_output('out')
        self.add_text_input('api_name', 'API Name', text='Gemini')
        #self.add_text_input('api_key_ref', 'API Key (Settings)', text='API Key') # Commented out for now

        # Add a button to trigger the API call
        self.action_button = QPushButton('Get Models', self.view)
        self.action_button.clicked.connect(self.call_api)
        self.add_custom_widget(self.action_button)

        # Add a text output to show results
        self.add_text_output('output_text', 'Result', text="")

    def call_api(self):
        # Get the API key from the settings (using the main window)
        main_window = self.graph.window()  # Access the main window
        api_key = main_window.api_key_input.text()

        if not api_key:
            self.set_property('output_text', "Error: API Key not set in settings.")
            return

        url = "https://generativelanguage.googleapis.com/v1beta/models?key=" + api_key

        try:
            response = requests.get(url)
            response.raise_for_status()  # Raise an exception for bad status codes

            data = response.json()
            model_names = [model['name'] for model in data['models']]
            self.set_property('output_text', "Models:\n" + '\n'.join(model_names))  # Line length adjusted

        except requests.exceptions.RequestException as e:
            self.set_property('output_text', f"Error: {e}")  # Line length adjusted
        except json.JSONDecodeError as e:
            self.set_property('output_text', f"Error decoding JSON: {e}")  # Line length adjusted
        except Exception as e:
            self.set_property('output_text', f"An unexpected error occurred: {e}")  # Line length adjusted
