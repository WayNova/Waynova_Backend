from flask import Flask, request, jsonify, render_template, send_from_directory
import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__, static_folder='../static', template_folder='../templates')

# Backend API URL
BACKEND_URL = "http://localhost:8000"

@app.route('/')
def index():
    return send_from_directory('frontend', 'index.html')

@app.route('/api/chat', methods=['POST'])
def chat_proxy():
    try:
        data = request.get_json()
        response = requests.post(f"{BACKEND_URL}/chat", json=data)
        return jsonify(response.json()), response.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/static/<path:path>')
def serve_static(path):
    return send_from_directory('static', path)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000, debug=True)
