# Quick Start Guide - Solana Ticketing System

This guide will help you get started with the Solana Ticketing System quickly.

## 1. Initial Setup (5 minutes)

### Install Required Software

```bash
# Install Python 3.8+
# Install Solana CLI tools
# Install Git
```

### Clone and Setup Project

```bash
# Clone repository
git clone [repository-url]
cd solana-ticketing

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Unix/MacOS

# Install dependencies
pip install -r requirements.txt
```

## 2. Configuration (2 minutes)

### Set Up Environment

1. Copy `.env.example` to `.env`
2. Add your OpenAI API key to `.env`:

```env
OPENAI_API_KEY=your_api_key_here
```

### Configure Solana

```bash
# Set to devnet
solana config set --url https://api.devnet.solana.com
```

## 3. Get Test SOL (2 minutes)

```bash
# Create a new wallet
python examples/get_wallet.py

# Airdrop SOL (copy the command shown in the output)
solana airdrop 1 YOUR_WALLET_ADDRESS --url devnet

# Verify balance
solana balance YOUR_WALLET_ADDRESS --url devnet
```

## 4. Start the System (1 minute)

```bash
# Start the web interface
python src/app.py

# Open in browser
http://localhost:5000
```

## 5. Create Your First Ticket (3 minutes)

```bash
# Run the test script
python examples/test_tickets.py

# Follow the prompts to:
# 1. Create a ticket
# 2. Verify the ticket
# 3. Use the ticket
```

## Common Commands

### Wallet Management

```bash
# Check balance
solana balance YOUR_WALLET_ADDRESS --url devnet

# Get more SOL
solana airdrop 1 YOUR_WALLET_ADDRESS --url devnet
```

### Ticket Operations

```bash
# Create ticket
python examples/test_tickets.py

# Verify ticket
python examples/verify_ticket.py
```

## Getting Help

1. Use the AI Assistant in the web interface
2. Common questions to ask:
   - "How do I get SOL?"
   - "What are lamports?"
   - "How do I check my balance?"

## Troubleshooting Tips

### No SOL in Wallet?

1. Try smaller amounts (1 SOL instead of 2)
2. Wait between requests
3. Verify you're on devnet

### Transaction Failed?

1. Check SOL balance
2. Ensure proper wallet permissions
3. Verify network connection

### AI Assistant Not Responding?

1. Check OpenAI API key in .env
2. Verify internet connection
3. Ensure question is blockchain-related

## Next Steps

1. Explore the full documentation in README.md
2. Try creating multiple tickets
3. Experiment with ticket verification
4. Learn about Solana blockchain concepts through the AI assistant
