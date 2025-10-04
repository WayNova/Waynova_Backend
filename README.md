# AI Agent - Grant Intelligence Chatbot

A modern, AI-powered chatbot designed to answer questions about grants, eligibility, and sales strategies for public sector organizations. Built with a beautiful frontend that matches the Waynova.ai design aesthetic.

## Features

- **Grant Discovery & Matching**: Find relevant grants for specific needs and locations
- **Buyer Qualification**: Check eligibility and identify target organizations
- **Sales Strategy**: Get insights on prioritization and targeting approaches
- **Document Generation**: Create buyer-ready materials for grant opportunities
- **Modern UI**: Clean, responsive design matching Waynova.ai's aesthetic

## Quick Start

### 1. Setup Environment

```bash
# Clone or navigate to the project directory
cd "ai agent"

# Copy environment template
cp .env.example .env

# Edit .env and add your OpenAI API key
# Get your API key from: https://platform.openai.com/api-keys
```

### 2. Install Dependencies

```bash
# Install backend dependencies
pip install -r backend/requirements.txt

# Install main app dependencies
pip install -r requirements.txt
```

### 3. Run the Application

#### Option A: Run Both Services (Recommended)
```bash
# Terminal 1: Start the FastAPI backend
cd backend
python main.py

# Terminal 2: Start the Flask frontend server
cd ..
python app.py
```

#### Option B: Run with Single Command (Alternative)
```bash
# Install uvicorn for the backend
pip install uvicorn[standard]

# Run the backend in background
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000 &

# Run the frontend
cd ..
python app.py
```

### 4. Access the Application

Open your browser and go to: `http://localhost:3000`

## Project Structure

```
ai agent/
├── backend/
│   ├── main.py              # FastAPI backend with chat endpoint
│   └── requirements.txt      # Backend dependencies
├── frontend/
│   └── index.html           # Main chat interface
├── app.py                   # Flask frontend server
├── requirements.txt         # Main app dependencies
├── .env.example            # Environment variables template
└── README.md               # This file
```

## API Endpoints

### Chat Endpoint
- **URL**: `POST /api/chat`
- **Body**:
  ```json
  {
    "message": "What grants are available for school security?",
    "conversation_id": "optional-conversation-id"
  }
  ```
- **Response**:
  ```json
  {
    "response": "AI-generated response...",
    "conversation_id": "unique-conversation-id"
  }
  ```

## Example Questions

The chatbot can answer questions like:

**Grant Discovery / Matching:**
- "What grants are available right now for school security cameras in Pennsylvania?"
- "Are there any federal grants open for EMS equipment in rural areas?"
- "Which active grants could fund body-worn cameras for police departments in Texas?"

**Buyer Qualification / Targeting:**
- "Does Springfield Fire Department have any grants they're eligible for this year?"
- "Which school districts in Ohio have recently won safety grants?"
- "How much funding has the local police department received in the past three years?"

**Sales Strategy / Prioritization:**
- "Which of my target accounts have the highest confidence score for grant eligibility?"
- "If I'm selling gunshot detection technology, which grants should I bring up with buyers?"
- "Who in a school district usually manages grants — should I talk to the superintendent or facilities director?"

**Practical / Workflow Help:**
- "Can you generate a buyer-ready one-pager for the Homeland Security school safety grant?"

## Technology Stack

- **Backend**: FastAPI (Python)
- **Frontend**: Vanilla JavaScript with Tailwind CSS
- **AI**: OpenAI GPT-3.5-turbo
- **Styling**: Tailwind CSS (matching Waynova.ai design)
- **Icons**: Font Awesome

## Customization

### Adding New Features

1. **Backend**: Extend `main.py` with new endpoints
2. **Frontend**: Modify `index.html` for UI changes
3. **Styling**: Update Tailwind classes to match your brand

### Environment Variables

- `OPENAI_API_KEY`: Your OpenAI API key (required)

## Deployment

### Local Development
The app runs on:
- Frontend: `http://localhost:3000`
- Backend API: `http://localhost:8000`

### Production Deployment
For production, consider:
1. Using a production WSGI server (Gunicorn)
2. Setting up a reverse proxy (Nginx)
3. Using environment-specific configuration files
4. Adding authentication and rate limiting

## Support

For issues or questions:
1. Check the console for error messages
2. Verify your OpenAI API key is correctly set
3. Ensure all dependencies are installed

## License

This project is created for demonstration purposes.
