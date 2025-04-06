# iGain Chatbot API

This is a simple Flask API for the iGain chatbot application.

## Setup

1. Make sure you have Python installed (3.7+ recommended)

2. Create a virtual environment (optional but recommended):

```bash
# On macOS/Linux
python -m venv venv
source venv/bin/activate

# On Windows
python -m venv venv
venv\Scripts\activate
```

3. Install the required packages:

```bash
pip install -r requirements.txt
```

## Running the API

To start the Flask server, run:

```bash
python app.py
```

The server will start on `http://localhost:5000`.

## API Endpoints

- `GET /api/chatbot-data` - Get initial chatbot data
- `POST /api/send-message` - Send a message to the chatbot
  - Request body: `{ "message": "Your message here" }`
  - Response: `{ "response": "Bot response here" }`

## Development

You can modify the `app.py` file to add your own chatbot logic or connect to external services. 