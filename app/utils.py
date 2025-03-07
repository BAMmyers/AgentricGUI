import requests
import json
import re
import packaging.version
import logging

# Create a logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Create a file handler and a stream handler
file_handler = logging.FileHandler('gemini_assistant.log')
stream_handler = logging.StreamHandler()

# Create a formatter and add it to the handlers
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
stream_handler.setFormatter(formatter)

# Add the handlers to the logger
logger.addHandler(file_handler)
logger.addHandler(stream_handler)

def call_gemini_assistant(prompt, node_graph=None):
    """
    Sends a prompt to the local Gemini proxy server, potentially with context
    from the node graph, and returns the response.

    Args:
        prompt: The text prompt.
        node_graph: The NodeGraphQt.NodeGraph object (optional).

    Returns:
        The text of the assistant's response.
    """
    response_text = ""
    try:
        # --- Node-based commands ---
        if node_graph:
            # Explain Node Command
            match = re.match(r'explain node (.+)', prompt, re.IGNORECASE)
            if match:
                node_name = match.group(1).strip()
                node = node_graph.get_node_by_name(node_name)
                if node:
                    properties = node.properties()
                    properties_formatted = "\n".join(
                        f"  {key}: {value}" for key, value in properties.items()
                    )
                    response_text = (
                        f"Node '{node_name}' ({node.type_}) has the following properties:\n"
                        f"{properties_formatted}"
                    )
                else:
                    response_text = f"Error: No node found with name '{node_name}'."

            # Change Node Property Command
            match = re.match(r'change (.+?) property (.+?) to (.+)', prompt, re.IGNORECASE)
            if match:
                node_name = match.group(1).strip()
                property_name = match.group(2).strip()
                new_value = match.group(3).strip()
                node = node_graph.get_node_by_name(node_name)

                if node:
                    try:
                        # Check if the property exists
                        if property_name not in node.properties():
                            response_text = (
                                f"Error: Node '{node_name}' does not have property "
                                f"'{property_name}'."
                            )
                        else:
                            # Check data type, and convert string if necessary
                            current_value = node.get_property(property_name)
                            if isinstance(current_value, bool):
                                if new_value.lower() == 'true':
                                    new_value = True
                                elif new_value.lower() == 'false':
                                    new_value = False
                                else:
                                    response_text = (
                                        f"Error: Invalid value '{new_value}' for boolean "
                                        f"property '{property_name}'."
                                    )
                            elif isinstance(current_value, int):
                                try:
                                    new_value = int(new_value)
                                except ValueError:
                                    response_text = (
                                        f"Error: Invalid value '{new_value}' for integer "
                                        f"property '{property_name}'."
                                    )
                            elif isinstance(current_value, float):
                                try:
                                    new_value = float(new_value)
                                except ValueError:
                                    response_text = (
                                        f"Error: Invalid value '{new_value}' for float "
                                        f"property '{property_name}'."
                                    )

                            if response_text == "":
                                node.set_property(property_name, new_value)
                                response_text = (
                                    f"Successfully changed property '{property_name}' of "
                                    f"node '{node_name}' to '{new_value}'."
                                )
                    except Exception as e:
                        response_text = f"Error changing property: {e}"
                else:
                    response_text = f"Error: No node found with name '{node_name}'."

            # List Nodes
            match = re.match(r'list nodes', prompt, re.IGNORECASE)
            if match:
                nodes = node_graph.all_nodes()
                node_names = [node.name() for node in nodes]
                response_text = "Nodes:\n" + '\n'.join(node_names)

        if response_text != "":
            return response_text

        # --- Call Local Server ---
        main_window = node_graph.window()
        installation_id = main_window.installation_id
        url = "http://localhost:5000/gemini"  # URL of your local server

        headers = {'Content-Type': 'application/json'}
        data = {
            'prompt': prompt,
            'installation_id': installation_id  # Include installation ID
        }

        response = requests.post(url, headers=headers, data=json.dumps(data))
        response.raise_for_status()
        response_json = response.json()

        # Check for gemini errors coming through server
        if "error" in response_json:
            return f"Error from Gemini API: {response_json['error']}"

        # Get the text
        if 'candidates' in response_json and response_json['candidates']:
            if 'content' in response_json['candidates'][0] and response_json['candidates'][0]['content']['parts']:
                return response_json['candidates'][0]['content']['parts'][0]['text']
            else:
                return "Error: Could not find the response text."
        else:
            return "Error: Could not find candidates in the response."

    except requests.exceptions.RequestException as e:
        logger.error(f'Request Error: {e}')
        return f"Request Error: {e}"
    except (KeyError, IndexError) as e:
        logger.error(f'Error parsing response: {e}')
        return f"Error parsing response: {e}"
    except json.JSONDecodeError as e:
        logger.error(f'JSON Decode Error: {e}')
        return f"JSON Decode Error: {e}"
    except Exception as e:
        logger.error(f'An unexpected error occurred: {e}')
        return f"An unexpected error occurred: {e}"

def check_for_updates(installation_id):
    """
    Checks for updates and for a kill switch activation.

    Args:
        installation_id: The unique installation ID.

    Returns:
        A tuple: (latest_version, update_url, blacklisted).
        - latest_version: The latest version number (as a string), or None if an error occurred.
        - update_url: The URL to download the update, or None.
        - blacklisted: True if the installation is blacklisted, False otherwise.
    """
    update_url = "https://github.com/BAMmyers/AgentricGUI/releases"  # Replace with your actual update URL
    blacklist_url = "https://raw.githubusercontent.com/BAMmyers/AgentricGUI/main/blacklist.txt"  # REPLACE with your blacklist URL
    version_url = "https://raw.githubusercontent.com/BAMmyers/AgentricGUI/main/version.txt"  # REPLACE

    try:
        # Check for blacklist
        blacklist_response = requests.get(blacklist_url)
        blacklist_response.raise_for_status()
        blacklist = installation_id in blacklist_response.text

        # Check for updates
        version_response = requests.get(version_url)
        version_response.raise_for_status()
        latest_version_str = version_response.text.strip()
        latest_version = packaging.version.parse(latest_version_str)

        logger.info(f'Update check result: latest_version={latest_version}, update_url={update_url}, blacklisted={blacklisted}')
        return latest_version, update_url, blacklist

    except requests.exceptions.RequestException as e:
        logger.error(f'Update/blacklist check error: {e}')
        return None, None, False
    except Exception as e:
        logger.error(f'An unexpected error occurred during update/blacklist check: {e}')
        return None, None, False
