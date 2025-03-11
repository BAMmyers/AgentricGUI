
from app.nodes.base_node import BaseNode
import requests
import json
from PyQt5.QtWidgets import QPushButton, QComboBox
from typing import Dict, Any

class APINode(BaseNode):
    NODE_NAME = 'API'

    def __init__(self):
        super().__init__()
        
        # Remove default ports from base class
        self.delete_input(0)
        self.delete_output(0)
        
        # Add specific ports
        self.add_input('prompt', label='Prompt')
        self.add_input('parameters', label='Parameters', required=False)
        self.add_output('response', label='Response')
        self.add_output('error', label='Error')

        # Add API configuration
        self.add_text_input('api_name', 'API Name', text='Gemini')
        self.add_text_input('endpoint', 'API Endpoint', 
                           text='https://generativelanguage.googleapis.com/v1beta/models')
        
        # Add model selector
        self.model_combo = QComboBox()
        self.model_combo.addItems([
            'gemini-pro',
            'gemini-pro-vision',
            'embedding-001'
        ])
        self.add_custom_widget(self.model_combo)

        # Add refresh models button
        self.refresh_btn = QPushButton('Refresh Models', self.view)
        self.refresh_btn.clicked.connect(self.refresh_models)
        self.add_custom_widget(self.refresh_btn)

        # Add a text output to show results
        self.add_text_output('output_text', 'Result', text="")

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process the input data and make API call.
        
        Args:
            input_data (dict): Contains 'prompt' and optional 'parameters'
            
        Returns:
            dict: Contains 'response' or 'error'
        """
        try:
            # Get API configuration
            main_window = self.graph.window()
            api_key = main_window.api_key_input.text()
            
            if not api_key:
                raise ValueError("API Key not set in settings")
            
            # Get input data
            prompt = input_data.get('prompt', '')
            parameters = input_data.get('parameters', {})
            
            if not prompt:
                raise ValueError("No prompt provided")
            
            # Prepare API request
            model = self.model_combo.currentText()
            endpoint = self.get_property('endpoint')
            
            url = f"{endpoint}/{model}:generateContent?key={api_key}"
            
            payload = {
                "contents": [{
                    "parts": [{
                        "text": prompt
                    }]
                }]
            }
            
            # Add any additional parameters
            if parameters:
                payload.update(parameters)
            
            # Make API call
            self.logger.info(f"Making API call to {model}")
            response = requests.post(url, json=payload)
            response.raise_for_status()
            
            data = response.json()
            
            # Update output text widget
            result = json.dumps(data, indent=2)
            self.set_property('output_text', result)
            
            return {"response": data}
            
        except requests.exceptions.RequestException as e:
            error_msg = f"API request failed: {str(e)}"
            self.logger.error(error_msg)
            self.set_property('output_text', error_msg)
            return {"error": error_msg}
            
        except Exception as e:
            error_msg = f"Error processing API node: {str(e)}"
            self.logger.error(error_msg)
            self.set_property('output_text', error_msg)
            return {"error": error_msg}

    def refresh_models(self):
        """Refresh the available models list from the API."""
        try:
            main_window = self.graph.window()
            api_key = main_window.api_key_input.text()
            
            if not api_key:
                raise ValueError("API Key not set in settings")
            
            endpoint = self.get_property('endpoint')
            url = f"{endpoint}?key={api_key}"
            
            response = requests.get(url)
            response.raise_for_status()
            
            data = response.json()
            model_names = [model['name'].split('/')[-1] for model in data['models']]
            
            # Update model combo box
            self.model_combo.clear()
            self.model_combo.addItems(model_names)
            
            # Update output text
            self.set_property('output_text', "Available Models:\n" + '\n'.join(model_names))
            
        except Exception as e:
            error_msg = f"Error refreshing models: {str(e)}"
            self.logger.error(error_msg)
            self.set_property('output_text', error_msg)
