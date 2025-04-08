# iGain
## AI Chatbot to help users find lost packages

### Try it out:

https://igain-prathjs-projects.vercel.app/

(If the chatbot is stuck in loading state, refresh it after 15-30 seconds)

### Deployment:

System requirements:
- Python3 installed
- Node.js installed

To deploy locally, you need an OpenAI API key with credits loaded. Create a .env file in the project's root directory, and then create this variable, replacing api_key with your own:

OPENAI_API_KEY="api_key"

Then create a .env.local file in the project's root directory, and then create this variable:

NEXT_PUBLIC_API_URL=http://localhost:5328

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

### Approach taken:

The web app that houses the chatbot is built on the Next.JS framework for seamless development and deployment. The chatbot functionality is built using Python, and FastAPI to create a microservice in the backend that can be accessed by Next.

The chatbot uses the OpenAI API to access its GPT model, which it uses to determine which course of action or branch that the chatbot should go with depending on the user's input. This can account for edge cases and nuance in the user's text.

### Bot in Action

<img width="351" alt="Screenshot 2025-04-07 at 6 26 27 PM" src="https://github.com/user-attachments/assets/705273f4-db3c-475e-8913-b9cf05e49bc9" /> <img width="351" alt="Screenshot 2025-04-07 at 6 31 16 PM" src="https://github.com/user-attachments/assets/909b87d8-b0d5-4cdb-99c0-c8b2e85ac252" /> <img width="351" alt="Screenshot 2025-04-07 at 6 32 37 PM" src="https://github.com/user-attachments/assets/9f43c289-9bb2-4f1d-8d31-4603281cd535" /> <img width="351" alt="Screenshot 2025-04-07 at 6 39 04 PM" src="https://github.com/user-attachments/assets/3f6b306d-da41-4507-bc5a-9c41d6ecf242" />




