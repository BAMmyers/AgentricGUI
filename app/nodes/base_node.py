from NodeGraphQt import BaseNode as _BaseNode

from PyQt5.QtWidgets import QPushButton, QLabel
from PyQt5.QtCore import Qt
import logging

class BaseNode(_BaseNode):  # Use a different name to avoid conflicts
    __identifier__ = 'agentric'  # Unique identifier for our nodes

    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Add status properties
        self.add_property('status', '')  # success, error, processing
        self.add_property('error_message', '')
        self.add_property('output_data', {})
        
        # Add status indicator
        self.status_label = QLabel('')
        self.status_label.setAlignment(Qt.AlignCenter)
        self.add_custom_widget(self.status_label)
        
        # Add execute button
        self.execute_btn = QPushButton('Execute')
        self.execute_btn.clicked.connect(self.execute)
        self.add_custom_widget(self.execute_btn)
        
        self.setup_default_ports()

    def setup_default_ports(self):
        """Setup default input and output ports."""
        # Default input port
        input_port = self.add_input('input')
        input_port.required = True  # Mark as required for validation
        
        # Default output port
        self.add_output('output')

    def process(self, input_data: dict) -> dict:
        """
        Process the node's input data and return output.
        To be implemented by child classes.
        
        Args:
            input_data (dict): Data from connected input ports
            
        Returns:
            dict: Output data to be passed to connected nodes
        """
        raise NotImplementedError("Process method must be implemented by child class")

    def execute(self):
        """
        Execute this node individually.
        Useful for testing and debugging.
        """
        try:
            self.set_property('status', 'processing')
            self.status_label.setText('Processing...')
            
            # Collect input data from connected nodes
            input_data = {}
            for port in self.input_ports():
                connected_ports = port.connected_ports()
                if connected_ports:
                    connected_node = connected_ports[0].node
                    input_data[port.name()] = connected_node.get_property('output_data', {})
            
            # Process the node
            output = self.process(input_data)
            
            # Store the output
            self.set_property('output_data', output)
            self.set_property('status', 'success')
            self.status_label.setText('✓')
            self.status_label.setStyleSheet('color: green;')
            
        except Exception as e:
            self.logger.error(f"Error executing node: {str(e)}")
            self.set_property('status', 'error')
            self.set_property('error_message', str(e))
            self.status_label.setText('✗')
            self.status_label.setStyleSheet('color: red;')

    def update_status_display(self):
        """Update the visual status of the node."""
        status = self.get_property('status')
        if status == 'success':
            self.status_label.setText('✓')
            self.status_label.setStyleSheet('color: green;')
        elif status == 'error':
            self.status_label.setText('✗')
            self.status_label.setStyleSheet('color: red;')
        elif status == 'processing':
            self.status_label.setText('...')
            self.status_label.setStyleSheet('color: blue;')
        else:
            self.status_label.setText('')
            self.status_label.setStyleSheet('')
