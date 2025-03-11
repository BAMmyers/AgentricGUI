from app.nodes.base_node import BaseNode
from PyQt5.QtWidgets import QComboBox
import json

class AgentNode(BaseNode):
    NODE_NAME = 'Agent'

    def __init__(self):
        super().__init__()

        # Remove default ports from base class
        self.delete_input(0)  # Remove default input
        self.delete_output(0)  # Remove default output
        
        # Create specific ports for agent
        self.add_input('instruction', label='Instruction')
        self.add_input('context', label='Context', required=False)
        self.add_output('response', label='Response')
        self.add_output('error', label='Error')

        # Add properties for agent configuration
        self.add_text_input('name', 'Agent Name', text='MyAgent')
        self.add_text_input('purpose', 'Purpose', text='General Assistant')
        self.add_checkbox('internet_access', 'Internet Access', True)
        
        # Add agent type selector
        self.agent_type_combo = QComboBox()
        self.agent_type_combo.addItems([
            'General Assistant',
            'Code Generator',
            'Data Analyzer',
            'Task Planner'
        ])
        self.add_custom_widget(self.agent_type_combo)
        
        # Add system prompt input
        self.add_text_input('system_prompt', 'System Prompt', 
                           text='You are a helpful AI assistant.')

    def process(self, input_data: dict) -> dict:
        """
        Process the input data and generate agent response.
        
        Args:
            input_data (dict): Contains 'instruction' and optional 'context'
            
        Returns:
            dict: Contains 'response' or 'error'
        """
        try:
            # Get agent configuration
            agent_name = self.get_property('name')
            agent_type = self.agent_type_combo.currentText()
            system_prompt = self.get_property('system_prompt')
            internet_access = self.get_property('internet_access')
            
            # Get input data
            instruction = input_data.get('instruction', '')
            context = input_data.get('context', '')
            
            if not instruction:
                raise ValueError("No instruction provided")
            
            # Prepare agent message
            message = {
                "role": "system",
                "content": system_prompt
            }
            
            if context:
                message["context"] = context
                
            message["instruction"] = instruction
            
            # Log the processing
            self.logger.info(f"Processing with agent {agent_name} ({agent_type})")
            self.logger.debug(f"Input message: {json.dumps(message, indent=2)}")
            
            # TODO: Implement actual agent processing logic here
            # For now, return a simple response
            response = {
                "response": f"Agent {agent_name} ({agent_type}) received instruction: {instruction}"
            }
            
            if context:
                response["response"] += f"\nWith context: {context}"
            
            return response
            
        except Exception as e:
            self.logger.error(f"Error in agent processing: {str(e)}")
            return {"error": str(e)}
