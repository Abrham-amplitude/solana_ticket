import openai
from typing import Dict, List, Optional
import os
from openai import AsyncOpenAI

class TicketingAIAssistant:
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the AI assistant with OpenAI API key"""
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key is required. Set it in the environment or pass it to the constructor.")
        self.client = AsyncOpenAI(api_key=self.api_key)
        
        # Define allowed topics for context checking
        self.allowed_topics = [
            "solana", "blockchain", "wallet", "sol", "crypto", "token", "nft",
            "transaction", "airdrop", "devnet", "testnet", "mainnet", "ticket",
            "smart contract", "web3", "dapp", "decentralized", "public key",
            "private key", "balance", "lamports", "account", "signature"
        ]
        
        # Predefined common queries and responses
        self.common_queries = {
            "get_sol": {
                "question": "How do I get SOL?",
                "answer": """To get SOL on devnet:
1. First, make sure you're on devnet:
   solana config set --url https://api.devnet.solana.com
2. Then airdrop SOL to your wallet:
   solana airdrop 1 YOUR_WALLET_ADDRESS
3. You can verify your balance with:
   solana balance YOUR_WALLET_ADDRESS"""
            },
            "check_balance": {
                "question": "How do I check my wallet balance?",
                "answer": """To check your SOL balance:
1. Use this command:
   solana balance YOUR_WALLET_ADDRESS --url devnet
2. Make sure you replace YOUR_WALLET_ADDRESS with your actual wallet address"""
            },
            "zero_sol": {
                "question": "What do I do if I see 0 SOL?",
                "answer": """If you have 0 SOL:
1. Try requesting a smaller amount (1 SOL instead of 2)
2. Wait a few minutes between requests
3. Make sure you're on devnet
4. Try using a different RPC endpoint
5. If issues persist, try creating a new wallet"""
            },
            "what_is_solana": {
                "question": "What is Solana?",
                "answer": """Solana is a high-performance blockchain platform that offers:
1. Fast transactions (up to 65,000 TPS)
2. Low transaction costs
3. Smart contract support
4. Ideal for decentralized applications (dApps)
Our ticketing system uses Solana for secure and efficient ticket management."""
            },
            "ticket_security": {
                "question": "How secure are the tickets?",
                "answer": """Our tickets are secured by Solana blockchain technology:
1. Each ticket is a unique account on the Solana blockchain
2. Tickets can't be duplicated or forged
3. All transactions are recorded and verifiable
4. Ownership is cryptographically proven
5. Smart contracts ensure proper ticket usage"""
            },
            "lamports": {
                "question": "What are lamports?",
                "answer": """Lamports are the smallest unit of SOL, similar to how cents relate to dollars:
1. 1 SOL = 1,000,000,000 lamports (1 billion lamports)
2. Named after Leslie Lamport, a computer scientist
3. Used for precise calculations in Solana transactions
4. All transaction fees are calculated in lamports
5. Helps avoid floating-point precision issues in blockchain operations"""
            }
        }

    def _is_relevant_query(self, query: str) -> bool:
        """Check if the query is relevant to Solana/blockchain context"""
        query_lower = query.lower()
        return any(topic in query_lower for topic in self.allowed_topics)
    
    async def get_response(self, user_query: str) -> str:
        """Get AI response for user query"""
        try:
            # First check if it matches any predefined queries
            for query_info in self.common_queries.values():
                if query_info["question"].lower() in user_query.lower():
                    return query_info["answer"]
            
            # Check if query is relevant to our context
            if not self._is_relevant_query(user_query):
                return """I apologize, but I can only assist with questions related to:
1. Solana blockchain
2. Wallet management
3. SOL tokens and transactions
4. Our ticketing system
5. Blockchain-related topics

Please rephrase your question to focus on these topics."""
            
            # If relevant, use OpenAI
            response = await self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": """You are a specialized assistant for a Solana-based ticketing system.
                    ONLY answer questions related to Solana blockchain, wallet management, SOL tokens, and the ticketing system.
                    If a question is not related to these topics, politely decline to answer and suggest staying on topic.
                    Keep responses concise, technical, and focused on Solana/blockchain concepts."""},
                    {"role": "user", "content": user_query}
                ],
                max_tokens=150,
                temperature=0.7
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"I apologize, but I encountered an error: {str(e)}. Please try rephrasing your question."
    
    def get_common_queries(self) -> List[str]:
        """Get list of common queries"""
        return [info["question"] for info in self.common_queries.values()]
    
    def get_wallet_setup_guide(self) -> str:
        """Get step-by-step wallet setup guide"""
        return """Solana Wallet Setup Guide:
1. Install Solana CLI tools from https://docs.solana.com/cli/install-solana-cli-tools
2. Create a new wallet:
   - Run the test script: python examples/test_tickets.py
   - Copy your wallet address
3. Get SOL:
   - Run: solana airdrop 1 YOUR_WALLET_ADDRESS --url devnet
4. Verify your balance:
   - Run: solana balance YOUR_WALLET_ADDRESS --url devnet
5. You're ready to create tickets!"""
    
    def get_ticket_creation_guide(self) -> str:
        """Get step-by-step ticket creation guide"""
        return """Creating a Ticket:
1. Make sure you have SOL in your wallet
2. Run the test script: python examples/test_tickets.py
3. Follow the prompts to:
   - Create a ticket
   - Verify the ticket
   - Use the ticket when ready
4. Keep your ticket's public key safe!""" 