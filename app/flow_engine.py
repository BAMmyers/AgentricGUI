from typing import Dict, List, Set
import logging

class FlowEngine:
    def __init__(self, graph):
        self.graph = graph
        self.logger = logging.getLogger('FlowEngine')
        self.execution_order = []
        self.processed_nodes = set()

    def get_node_dependencies(self) -> Dict[str, Set[str]]:
        """Build a dependency map of nodes based on connections."""
        dependencies = {}
        for node in self.graph.all_nodes():
            dependencies[node.id] = set()
            # Get all nodes connected to this node's input ports
            for port in node.input_ports():
                for connected_port in port.connected_ports():
                    dependencies[node.id].add(connected_port.node.id)
        return dependencies

    def topological_sort(self, dependencies: Dict[str, Set[str]]) -> List[str]:
        """Sort nodes in topological order for execution."""
        visited = set()
        temp_mark = set()
        order = []

        def visit(node_id):
            if node_id in temp_mark:
                raise ValueError("Circular dependency detected")
            if node_id not in visited:
                temp_mark.add(node_id)
                for dep in dependencies[node_id]:
                    visit(dep)
                temp_mark.remove(node_id)
                visited.add(node_id)
                order.insert(0, node_id)

        for node_id in dependencies:
            if node_id not in visited:
                visit(node_id)

        return order

    def run_flow(self) -> bool:
        """Execute the node graph flow."""
        try:
            # Get dependencies and sort nodes
            dependencies = self.get_node_dependencies()
            self.execution_order = self.topological_sort(dependencies)
            
            # Store intermediate results
            results = {}
            
            # Execute nodes in order
            for node_id in self.execution_order:
                node = self.graph.get_node_by_id(node_id)
                
                # Collect input data from connected nodes
                input_data = {}
                for input_port in node.input_ports():
                    connected_ports = input_port.connected_ports()
                    if connected_ports:
                        # Get data from the connected node's output
                        connected_node = connected_ports[0].node
                        if connected_node.id in results:
                            input_data[input_port.name()] = results[connected_node.id]

                try:
                    # Process the node
                    self.logger.info(f"Processing node: {node.name()}")
                    output = node.process(input_data)
                    results[node_id] = output
                    self.processed_nodes.add(node_id)
                    
                    # Update node visual state (e.g., border color to indicate success)
                    node.set_property('status', 'success')
                    
                except Exception as e:
                    self.logger.error(f"Error processing node {node.name()}: {str(e)}")
                    node.set_property('status', 'error')
                    return False

            return True

        except Exception as e:
            self.logger.error(f"Flow execution error: {str(e)}")
            return False

    def reset_flow(self):
        """Reset the flow state."""
        self.execution_order = []
        self.processed_nodes.clear()
        for node in self.graph.all_nodes():
            node.set_property('status', '')

    def get_node_output(self, node_id: str) -> dict:
        """Get the output data for a specific node."""
        if node_id in self.processed_nodes:
            node = self.graph.get_node_by_id(node_id)
            return node.get_property('output_data', {})
        return {}

    def validate_connections(self) -> bool:
        """Validate that all required connections are present."""
        for node in self.graph.all_nodes():
            # Check if required input ports have connections
            for port in node.input_ports():
                if port.required and not port.connected_ports():
                    self.logger.error(f"Node {node.name()} missing required input connection on port {port.name()}")
                    return False
        return True
