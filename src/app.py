from flask import Flask, render_template, request, jsonify
from ai_assistant import TicketingAIAssistant
import asyncio
import os
from dotenv import load_dotenv
import pathlib

# Load environment variables from .env file
env_path = pathlib.Path(__file__).parent.parent / '.env'
load_dotenv(env_path)

# Initialize Flask app
app = Flask(__name__)

# Get OpenAI API key from environment
api_key = os.getenv('OPENAI_API_KEY')
if not api_key:
    raise ValueError("OPENAI_API_KEY not found in environment variables")

# Initialize AI assistant with API key
ai_assistant = TicketingAIAssistant(api_key=api_key)

@app.route('/')
def home():
    """Render the home page"""
    common_queries = ai_assistant.get_common_queries()
    wallet_guide = ai_assistant.get_wallet_setup_guide()
    ticket_guide = ai_assistant.get_ticket_creation_guide()
    return render_template('index.html', 
                         common_queries=common_queries,
                         wallet_guide=wallet_guide,
                         ticket_guide=ticket_guide)

@app.route('/ask', methods=['POST'])
async def ask():
    """Handle user questions"""
    user_query = request.json.get('query', '')
    if not user_query:
        return jsonify({'error': 'No query provided'}), 400
        
    response = await ai_assistant.get_response(user_query)
    return jsonify({'response': response})

if __name__ == '__main__':
    app.run(debug=True) 