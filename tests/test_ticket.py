import pytest
import asyncio
from solana.keypair import Keypair
from src.ticket_client import TicketClient

@pytest.mark.asyncio
async def test_create_ticket():
    # Create a new client
    client = TicketClient()
    
    # Generate a new keypair for testing
    payer = Keypair()
    
    # You'll need to airdrop some SOL to this account on devnet
    # before running the test
    
    # Create a ticket
    result = await client.create_ticket(
        payer=payer,
        event_id=1,
        price=1000000  # 1 SOL in lamports
    )
    
    assert result['result'] is not None

    # Clean up
    await client.client.close() 