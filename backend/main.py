from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import List, Optional
import openai
import os
from dotenv import load_dotenv

app = FastAPI(title="AI Agent Chatbot", description="A chatbot for answering grant-related questions")

# Configure Azure OpenAI
client = openai.AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version=os.getenv("AZURE_OPENAI_VERSION", "2025-01-01-preview"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
)

class ChatMessage(BaseModel):
    message: str
    conversation_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    conversation_id: str

# In-memory conversation storage (in production, use a database)
conversations = {}

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(chat_message: ChatMessage):
    try:
        # Create system message for grant expertise
        system_message = """You are an AI assistant specialized in helping with grant discovery, matching, and sales strategy for public sector organizations.

**IMPORTANT: Format all responses using proper HTML tags for display in web interface**

**Response Formatting Guidelines:**
- Use HTML tags: <strong>bold text</strong>, <em>italic text</em>, <h3>Section Headers</h3>
- Structure with: <ol><li>Numbered lists</li></ol> and <ul><li>Bullet points</li></ul>
- Use <p>paragraphs</p> for text blocks
- Start with direct answers, then organized details
- Keep sections clearly separated with HTML structure

**Required Response Structure:**
<h3>Direct Answer</h3>
<p>Start with the immediate, clear response to the query.</p>

<h3>Available Grant Options</h3>
<ol>
<li><strong>Grant Name</strong>: Brief description</li>
</ol>

<h3>Eligibility Requirements</h3>
<ul>
<li>Specific requirement</li>
</ul>

<h3>Application Process</h3>
<ol>
<li>Step one</li>
<li>Step two</li>
</ol>

Use proper HTML structure throughout for maximum readability in the web interface."""

        # Get or create conversation
        conversation_id = chat_message.conversation_id or "default"
        if conversation_id not in conversations:
            conversations[conversation_id] = []

        # Add user message to conversation
        conversations[conversation_id].append({"role": "user", "content": chat_message.message})

        # Keep only last 10 messages for context
        if len(conversations[conversation_id]) > 10:
            conversations[conversation_id] = conversations[conversation_id][-10:]

        # Create Azure OpenAI chat completion
        response = client.chat.completions.create(
            model=os.getenv("AZURE_OPENAI_MODEL", "gpt-4"),
            messages=[
                {"role": "system", "content": system_message}
            ] + conversations[conversation_id],
            max_tokens=1000,
            temperature=0.7
        )

        assistant_response = response.choices[0].message.content

        # Format response with HTML structure for better readability
        if "1." in assistant_response and "<h3>" not in assistant_response:
            # Convert numbered lists to HTML format
            lines = assistant_response.split('\n')
            formatted_response = ""

            for line in lines:
                if line.strip().startswith('1.') or line.strip().startswith('2.') or line.strip().startswith('3.'):
                    # Convert numbered items to HTML list
                    if '<ol>' not in formatted_response:
                        formatted_response += '<h3>Available Grant Options</h3><ol>'
                    formatted_response += f'<li>{line.strip()[2:].strip()}</li>'
                elif line.strip().startswith('- ') or line.strip().startswith('• '):
                    # Convert bullet points to HTML list
                    if '<ul>' not in formatted_response:
                        formatted_response += '<h3>Key Details</h3><ul>'
                    formatted_response += f'<li>{line.strip()[2:].strip()}</li>'
                elif line.strip() and not line.strip().startswith('<'):
                    # Regular paragraphs
                    formatted_response += f'<p>{line.strip()}</p>'
                else:
                    formatted_response += line

            # Close any open lists
            if '<ol>' in formatted_response and '</ol>' not in formatted_response:
                formatted_response += '</ol>'
            if '<ul>' in formatted_response and '</ul>' not in formatted_response:
                formatted_response += '</ul>'

            assistant_response = formatted_response

        # Add basic HTML structure if no formatting exists
        if '<h3>' not in assistant_response and '<p>' not in assistant_response:
            assistant_response = f"<p>{assistant_response.replace(chr(10), '</p><p>')}</p>"

        # Add assistant response to conversation
        conversations[conversation_id].append({"role": "assistant", "content": assistant_response})

        return ChatResponse(response=assistant_response, conversation_id=conversation_id)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    return {"message": "AI Agent Chatbot API is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
