from NodeGraphQt import BaseNode as _BaseNode

class BaseNode(_BaseNode):  # Use a different name to avoid conflicts
    __identifier__ = 'agentric'  # Unique identifier for our nodes

    def __init__(self):
        super().__init__()
        # Example of adding a custom property
        self.add_property('my_custom_property', 'default_value')
