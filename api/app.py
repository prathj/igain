from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import logging
from openai import OpenAI
from chatbot import ChatBot
from dotenv import load_dotenv
import os

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# create FastAPI app with increased timeouts
app = FastAPI()

# implemented CORS to prevent cross-domain requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# get API key here
load_dotenv()

API_KEY = os.getenv("OPENAI_API_KEY")

# initialize OpenAI client
try:
    client = OpenAI(
        api_key=API_KEY,
        timeout=60.0,  # increase timeout to 60 seconds to allow for backoff
        max_retries=0
    )
    logger.info("Testing OpenAI API connection...")
    test_response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": "Hello"}],
        max_tokens=5
    )
    logger.info(f"API connection successful: {test_response.model_dump_json(indent=2)}")
except Exception as e:
    logger.error(f"Error initializing OpenAI client: {str(e)}")
    client = None

# create a global ChatBot instance
bot = ChatBot(client)

# define request model for messages
class MessageRequest(BaseModel):
    message: str

# called by frontend to get initial greeting
@app.get("/api/chatbot-data")
async def get_chatbot_data():
    bot.reset()
    data = {
        "greeting": bot.state_greeting(""),
        "name": "iGain Package Tracker",
        "capabilities": [
            "Track packages with tracking numbers",
            "Provide real-time updates",
            "Help file support tickets"
        ]
    }
    return data

# called by frontent to get bot responses
@app.post("/api/send-message")
async def send_message(request: MessageRequest):
    try:
        message = request.message
        response = bot.process_input(message)
        return {"response": response}
    except Exception as e:
        logger.error(f"Error in send_message endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# checks status of OpenAI api connection
@app.get("/api/health")
async def health_check():
    if client is None:
        return {"status": "warning", "message": "API is running but OpenAI client initialization failed"}
    return {"status": "ok", "message": "API is running and OpenAI client is initialized"}

if __name__ == "__main__":
    logger.info("Starting FastAPI server on port 5328")
    uvicorn.run(app, host="0.0.0.0", port=5328)
