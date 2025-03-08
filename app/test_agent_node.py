# import pytest

from app.nodes.agent_node import AgentNode

    
def test_agent_node_initialization():

    node = AgentNode()
    assert node.NODE_NAME == 'Agent'
    assert node.get_property('name') == 'MyAgent'
    assert node.get_property('purpose') == 'General Assistant'
    assert node.get_property('internet_access') is True

    
def test_agent_node_property_change():

    node = AgentNode()
    node.set_property('name', 'NewAgent')
    assert node.get_property('name') == 'NewAgent'
