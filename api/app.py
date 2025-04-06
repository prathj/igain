from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # This will enable CORS for all routes

@app.route('/api/chatbot-data', methods=['GET'])
def get_chatbot_data():
    # Mock data - you would replace this with your actual data processing logic
    data = {
        "greeting": "Hello! How can I help you today?",
        "name": "iGain Assistant",
        "capabilities": [
            "Answer customer service questions",
            "Provide product information",
            "Troubleshoot common issues"
        ]
    }
    return jsonify(data)

@app.route('/api/send-message', methods=['POST'])
def send_message():
    # Get the message from the request
    message = request.json.get('message', '')
    
    # Mock response - you would replace this with your actual chatbot logic
    response = f"You said: {message}. This is a mock response from the Flask backend."
    
    return jsonify({"response": response})

if __name__ == '__main__':
    app.run(debug=True, port=5000) 