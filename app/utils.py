import requests
import json
import logging

logger = logging.getLogger(__name__)

def call_gemini_assistant(prompt: str, graph=None) -> str:
    """
    Call the Gemini API with a prompt.
    
    Args:
        prompt (str): The user's input prompt
        graph: Optional node graph reference
        
    Returns:
        str: The assistant's response
    """
    try:
        # Get API key from main window if graph is provided
        api_key = None
        if graph and hasattr(graph, 'window'):
            main_window = graph.window()
            if hasattr(main_window, 'api_key_input'):
                api_key = main_window.api_key_input.text()

        if not api_key:
            return "Error: API key not set in settings"

        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={api_key}"
        
        payload = {
            "contents": [{
                "parts": [{
                    "text": prompt
                }]
            }]
        }

        response = requests.post(url, json=payload)
        response.raise_for_status()
        
        data = response.json()
        
        # Extract the response text from Gemini's response
        if 'candidates' in data and len(data['candidates']) > 0:
            candidate = data['candidates'][0]
            if 'content' in candidate and 'parts' in candidate['content']:
                parts = candidate['content']['parts']
                if len(parts) > 0 and 'text' in parts[0]:
                    return parts[0]['text']
        
        return "No valid response received from Gemini"

    except requests.exceptions.RequestException as e:
        logger.error(f"API request failed: {str(e)}")
        return f"Error making API request: {str(e)}"
    except Exception as e:
        logger.error(f"Error in call_gemini_assistant: {str(e)}")
        return f"Error: {str(e)}"

def check_for_updates(installation_id: str) -> tuple:
    """
    Check for updates and verify installation status.
    
    Args:
        installation_id (str): Unique identifier for this installation
        
    Returns:
        tuple: (latest_version, update_url, blacklist_status)
    """
    try:
        # For now, return dummy values
        # In production, this would make an actual API call to check updates
        return ("0.0.1", "https://github.com/BAMmyers/AgentricGUI/releases", False)
    except Exception as e:
        logger.error(f"Error checking for updates: {str(e)}")
        return (None, None, False)
