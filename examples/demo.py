import asyncio
from solana.keypair import Keypair
from src.ticket_client import TicketClient

async def demo():
    # Initialize client
    client = TicketClient()
    
    # Create a test wallet (in real usage, you'd want to manage keys securely)
    organizer = Keypair()
    
    # Create an event
    event_result = await client.create_event(
        payer=organizer,
        event_name="Python Conference 2024",
        total_tickets=100,
        price_per_ticket=1000000  # 1 SOL
    )
    
    if event_result["success"]:
        print(f"Event created! Event public key: {event_result['event_pubkey']}")
        
        # Get event info
        event_info = await client.get_event_info(event_result["event_pubkey"])
        print(f"Event info: {event_info}")
        
        # Create a buyer wallet
        buyer = Keypair()
        
        # Buy a ticket
        ticket_result = await client.buy_ticket(
            payer=buyer,
            event_pubkey=event_result["event_pubkey"]
        )
        
        if ticket_result["success"]:
            print(f"Ticket purchased! Ticket public key: {ticket_result['ticket_pubkey']}")
            
            # Validate ticket
            is_valid = await client.validate_ticket(ticket_result["ticket_pubkey"])
            print(f"Ticket is valid: {is_valid}")
    
    # Clean up
    await client.client.close()

if __name__ == "__main__":
    asyncio.run(demo()) 