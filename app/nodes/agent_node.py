from app.nodes.base_node import BaseNode

class AgentNode(BaseNode):
    NODE_NAME = 'Agent'

    def __init__(self):
        super().__init__()

        # Create input and output ports
        self.add_input('in')
        self.add_output('out')

        # Add properties for agent name and purpose
        self.add_text_input('name', 'Agent Name', text='MyAgent')
        self.add_text_input('purpose', 'Purpose', text='General Assistant')
        self.add_checkbox('internet_access', 'Internet Access', True)
