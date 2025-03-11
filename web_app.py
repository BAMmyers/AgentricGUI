from flask import Flask, render_template, jsonify, request
import logging
import json
import os

app = Flask(__name__)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/execute_flow', methods=['POST'])
def execute_flow():
    try:
        data = request.json
        # TODO: Implement flow execution
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
        settings = request.json
        with open('settings.json', 'w') as f:
            json.dump(settings, f)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/load_settings', methods=['GET'])
def load_settings():
    try:
        if os.path.exists('settings.json'):
            with open('settings.json', 'r') as f:
                settings = json.load(f)
        else:
            settings = {
                'api_key': '',
                'experience_level': 'Novice'
            }
        return jsonify(settings)
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    os.makedirs('templates', exist_ok=True)
    app.run(host='0.0.0.0', port=8000, debug=True)
