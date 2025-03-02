from flask import Flask, request, jsonify
import requests
import json
import os
import datetime  # Import datetime
import logging  # Import logging

app = Flask(__name__)

# --- Logging Setup ---
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Load your Gemini API key from an environment variable
GEMINI_API_KEY = os.environ.get(""GEMINI_API_KEY"") # Set this in environment
if not GEMINI_API_KEY:
    raise ValueError(""GEMINI_API_KEY environment variable not set."")

GEMINI_API_URL = ""https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key="" + GEMINI_API_KEY


# --- Rate Limiting (Data Structures - Placeholder) ---
request_counts = {}  # Dictionary to track requests per installation_id
RATE_LIMIT = 10  # Example: 10 requests per minute
TIME_WINDOW = 60  # Seconds


@app.route('/gemini', methods=['POST'])
def gemini_proxy():
    try:
        data = request.get_json()
        prompt = data.get('prompt')
        installation_id = data.get('installation_id')

        if not prompt:
            return jsonify({'error': 'Missing prompt', 'status': 'error'}), 400
        if not installation_id:
            return jsonify({'error': 'Missing installation_id', 'status': 'error'}), 400

        # --- Basic Rate Limiting (Conceptual - Not Fully Implemented) ---
        now = datetime.datetime.now()
        if installation_id not in request_counts:
            request_counts[installation_id] = []
        # Remove old timestamps
        request_counts[installation_id] = [ts for ts in request_counts[installation_id] if (now - ts).total_seconds() < TIME_WINDOW]
        if len(request_counts[installation_id]) >= RATE_LIMIT:
            logging.warning(f""Rate limit exceeded for installation_id: {installation_id}"")  # Log the event
            return jsonify({'error': 'Rate limit exceeded', 'status': 'error'}), 429  # 429 Too Many Requests
        request_counts[installation_id].append(now)

        # --- Construct the request to the Gemini API ---
        headers = {'Content-Type': 'application/json'}
        payload = {
            ""contents"": [{
                ""parts"": [{""text"": prompt}]
            }]
        }

        # --- Forward the request to the Gemini API ---
        response = requests.post(GEMINI_API_URL, headers=headers, data=json.dumps(payload))
        response.raise_for_status()  # This will raise an exception for HTTP errors

        response_json = response.json()

        # --- Logging ---
        logging.info(f""Request from {installation_id}: prompt='{prompt[:50]}...' - Success"")  # Log a truncated prompt

        return jsonify({'data': response_json, 'status': 'success'}) #Return with status


    except requests.exceptions.RequestException as e:
        logging.error(f""Request Error: {e} - from installation_id: {installation_id}"")  # Log the error
        return jsonify({'error': f'Request Error: {e}', 'status': 'error'}), 500
    except Exception as e:
        logging.exception(f""Unexpected Error: {e} - from installation_id: {installation_id}"")  # Log the exception with traceback
        return jsonify({'error': str(e), 'status': 'error'}), 500
