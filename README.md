# iGain
## AI Chatbot to help users find lost packages

### System requirements:
Python3 installed

### Deployment:
To deploy locally, you need an OpenAI API key with credits loaded. Create a .env file in the project's root directory, and then create this variable, replacing api_key with your own:

OPENAI_API_KEY="api_key"

Then, start the backend FastAPI server by traversing to the api folder and the running the app.py file.

```bash
cd api

python3 app.py
```

Then, cd to chatbotv2, and run the development server:

```bash
npm run dev
# or
yarn dev
# or
pnpm dev
# or
bun dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.

### Vercel link:



### Approach taken:

The web app that houses the chatbot is built on the Next.JS framework for seamless development and deployment. The chatbot functionality is built using Python, and FastAPI to create a microservice in the backend that can be accessed by Next.

The chatbot uses the OpenAI API to access its GPT model, which it uses to determine which course of action or branch that the chatbot should go with depending on the user's input. This can account for edge cases and nuance in the user's text.

### Bot in Action