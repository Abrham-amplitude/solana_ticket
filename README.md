# Solana Ticketing System with AI Assistant

A blockchain-based ticketing system built on Solana with an integrated AI assistant for user support.

## Table of Contents

1. [System Overview](#system-overview)
2. [Features](#features)
3. [Prerequisites](#prerequisites)
4. [Installation](#installation)
5. [Configuration](#configuration)
6. [Usage](#usage)
7. [AI Assistant](#ai-assistant)
8. [Architecture](#architecture)
9. [Troubleshooting](#troubleshooting)

## System Overview

This system combines Solana blockchain technology with AI assistance to provide a secure and user-friendly ticketing solution. Tickets are represented as Solana accounts, ensuring authenticity and preventing duplication.

### Key Components:

- Solana blockchain for ticket management
- OpenAI-powered assistant for user support
- Flask web interface
- Python-based backend

## Features

### Ticket Management

- Create digital tickets on Solana blockchain
- Verify ticket authenticity
- Transfer ticket ownership
- Mark tickets as used
- Track ticket history

### AI Assistant Capabilities

- Guided wallet setup
- SOL management assistance
- Ticket creation help
- Blockchain concept explanations
- Context-aware responses

### Security Features

- Blockchain-based verification
- Cryptographic ownership proof
- Tamper-proof tickets
- Secure transactions

## Prerequisites

- Python 3.8+
- Solana CLI tools
- Node.js and npm
- OpenAI API key

## Installation

1. Clone the repository:

```bash
git clone https://github.com/Abrham-amplitude/solana_ticket.git
cd solana
```

2. Create and activate virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Set up environment variables:

```bash
cp .env.example .env
# Edit .env with your OpenAI API key
```

## Configuration

### Solana Network Setup

1. Configure Solana for devnet:

```bash
solana config set --url https://api.devnet.solana.com
```

2. Create a wallet:

```bash
solana-keygen new
```

3. Get devnet SOL:

```bash
solana airdrop 1 [YOUR-WALLET-ADDRESS]
```

### Environment Variables

```env
OPENAI_API_KEY=your_api_key_here
SOLANA_NETWORK=devnet
RPC_URL=https://api.devnet.solana.com
```

## Usage

### Starting the System

1. Run the Flask application:

```bash
python src/app.py
```

2. Access the web interface:

```
http://localhost:5000
```

### Creating Tickets

1. Ensure wallet has sufficient SOL
2. Run the test script:

```bash
python examples/test_tickets.py
```

### Verifying Tickets

```bash
python examples/verify_ticket.py
```

## AI Assistant

### Available Commands

The AI assistant understands queries about:

- Solana blockchain
- Wallet management
- SOL tokens
- Ticket operations
- Blockchain concepts

### Common Queries

1. Getting SOL:

```
How do I get SOL?
```

2. Checking balance:

```
How do I check my wallet balance?
```

3. Understanding Lamports:

```
What are lamports?
```

### Response Types

1. Predefined Responses

   - Common blockchain queries
   - Frequent ticket operations
   - Setup instructions

2. Dynamic Responses
   - Context-aware answers
   - Technical explanations
   - Troubleshooting help

## Architecture

### System Components

1. **Ticket System (`src/ticket_system.py`)**

   - Handles ticket creation
   - Manages verification
   - Processes usage

2. **AI Assistant (`src/ai_assistant.py`)**

   - Processes user queries
   - Provides guided assistance
   - Maintains context awareness

3. **Web Interface (`src/app.py`)**
   - Flask-based frontend
   - User interaction handling
   - Response rendering

### Data Flow

1. Ticket Creation:

```
User -> Web Interface -> Ticket System -> Solana Blockchain
```

2. AI Assistance:

```
User Query -> AI Assistant -> OpenAI API -> Formatted Response
```

## Troubleshooting

### Common Issues

1. **Zero SOL Balance**

   - Try smaller airdrop amounts
   - Wait between requests
   - Verify devnet connection

2. **Transaction Errors**

   - Check wallet balance
   - Verify network connection
   - Ensure proper permissions

3. **AI Assistant Issues**
   - Verify API key
   - Check query relevance
   - Ensure proper formatting

### Support Resources

- Solana Documentation: https://docs.solana.com
- OpenAI Documentation: https://platform.openai.com/docs
- Project Issues: [GitHub Issues Link]

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit changes
4. Push to the branch
5. Create Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Solana Development Team
- OpenAI API Team
- Contributors and Testers
