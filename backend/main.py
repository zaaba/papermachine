from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
import json
from pathlib import Path
from settings import GPT_API_KEY

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://zaaba.github.io"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

import openai
openai.api_key = GPT_API_KEY

CONVERSATION_FILE = Path("conversation_store.json")
if not CONVERSATION_FILE.exists():
    CONVERSATION_FILE.write_text("{}")

def load_conversations():
    import json
    if not CONVERSATION_FILE.exists() or CONVERSATION_FILE.stat().st_size == 0:
        return {}  # Return an empty dictionary if the file is missing or empty
    try:
        with open(CONVERSATION_FILE, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        print("Warning: conversation_store.json is corrupted. Resetting file.")
        with open(CONVERSATION_FILE, "w") as f:
            f.write("{}")  # Reset the file
        return {}  # Return an empty dictionary


def save_conversations(data):
    import json
    with open(CONVERSATION_FILE, "w") as f:
        json.dump(data, f, indent=2)

# ADD THIS MODEL:
from pydantic import BaseModel

class ChatRequest(BaseModel):
    session_id: str
    prompt: str

@app.post("/chat")
async def chat(request: ChatRequest):
    data = load_conversations()
    conversation = data.get(request.session_id, [
        {"role": "system", "content": "You are an academic writing assistant helping users develop research papers."}
    ])

    conversation.append({"role": "user", "content": request.prompt})

    import requests
    headers = {
        "Authorization": f"Bearer {GPT_API_KEY}",
        "Content-Type": "application/json",
    }

    response = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers=headers,
        json={"model": "gpt-3.5-turbo", "messages": conversation},
    )

    if response.status_code == 200:
        assistant_reply = response.json()["choices"][0]["message"]["content"]
        conversation.append({"role": "assistant", "content": assistant_reply})

        # Save updated conversation
        data[request.session_id] = conversation
        save_conversations(data)

        return {"response": assistant_reply}
    else:
        return {"response": "API Error: " + response.text}
