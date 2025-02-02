import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from solders.pubkey import Pubkey
from src.ticket_system import TicketSystem

async def verify_existing_ticket(ticket_pubkey_str: str):
    system = TicketSystem()
    try:
        # Convert string to Pubkey
        ticket_pubkey = Pubkey.from_string(ticket_pubkey_str)
        
        # Verify the ticket
        print("Verifying ticket...")
        verify_result = await system.verify_ticket(ticket_pubkey)
        
        if verify_result["valid"]:
            print("Ticket is valid!")
            print(f"Ticket balance: {verify_result['balance'] / 1000000000} SOL")
        else:
            print(f"Ticket is invalid: {verify_result.get('error', 'Unknown error')}")
            
    finally:
        await system.close()

def main():
    ticket_pubkey = input("Enter ticket public key to verify: ")
    asyncio.run(verify_existing_ticket(ticket_pubkey))

if __name__ == "__main__":
    main() 