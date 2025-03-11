from flask import Flask, render_template, jsonify, request
import logging
import json
import os

app = Flask(__name__)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Default data
DEFAULT_NODES = [
    {'id': 1, 'name': 'Agent Node', 'x': 100, 'y': 100},
    {'id': 2, 'name': 'API Node', 'x': 300, 'y': 100}
]

DEFAULT_SETTINGS = {
    'apiKey': '',
    'experienceLevel': 'Novice'
}

# In-memory storage
nodes = DEFAULT_NODES.copy()
connections = []
settings = DEFAULT_SETTINGS.copy()

@app.route('/')
def index():
    # Fix the template data passing
    return render_template('index.html', nodes=nodes, connections=connections, settings=settings)

@app.route('/api/execute_flow', methods=['POST'])
def execute_flow():
    try:
        data = request.json
        flow_nodes = data.get('nodes', [])
        flow_connections = data.get('connections', [])
        
        logger.info(f"Executing flow with {len(flow_nodes)} nodes and {len(flow_connections)} connections")
        
        return jsonify({
            'success': True,
            'message': 'Flow executed successfully'
        })
    except Exception as e:
        logger.error(f"Error executing flow: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/save_settings', methods=['POST'])
def save_settings():
    try:
        global settings
        settings = request.json
        logger.info("Settings saved successfully")
        return jsonify({'success': True})
    except Exception as e:
        logger.error(f"Error saving settings: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/load_settings', methods=['GET'])
def load_settings():
    try:
        return jsonify(settings)
    except Exception as e:
        logger.error(f"Error loading settings: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

    app.run(host='0.0.0.0', port=8000, debug=True)
