import asyncio
import os
import sys

# Add the parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from solders.keypair import Keypair
from src.ticket_system import TicketSystem

async def main():
    print("\n=== Testing Ticket System ===\n")
    
    # Create a new wallet
    wallet = Keypair()
    print("Wallet address:", wallet.pubkey())
    
    # Instructions for airdrop
    print("\nFollow these steps:")
    print("1. Copy and run this command to airdrop SOL:")
    print(f"solana airdrop 2 {wallet.pubkey()} --url devnet")
    print("\n2. Wait for confirmation of the airdrop")
    print("3. Press Enter to continue with the test...")
    
    input()  # Wait for user to press Enter
    
    # Initialize ticket system
    ticket_system = TicketSystem()
    
    try:
        # Create a ticket
        print("\nCreating a ticket...")
        ticket_price = 1_000_000_000  # 1 SOL
        create_result = await ticket_system.create_ticket(wallet, ticket_price)
        
        if not create_result["success"]:
            print("Failed to create ticket:", create_result["error"])
            return
            
        print("Ticket created successfully!")
        print("Ticket public key:", create_result["ticket_pubkey"])
        
        # Verify the ticket
        print("\nVerifying ticket...")
        verify_result = await ticket_system.verify_ticket(create_result["ticket_pubkey"])
        
        if not verify_result["valid"]:
            print("Ticket verification failed:", verify_result["error"])
            return
            
        print("Ticket verified successfully!")
        print("Ticket balance:", verify_result["balance"], "lamports")
        
        # Use the ticket
        print("\nUsing ticket...")
        use_result = await ticket_system.use_ticket(create_result["ticket_pubkey"], wallet)
        
        if not use_result["success"]:
            print("Failed to use ticket:", use_result["error"])
            return
            
        print("Ticket used successfully!")
        print("Transaction ID:", use_result["transaction_id"])
        
    except Exception as e:
        print("An error occurred:", str(e))
    
    finally:
        # Close the connection
        await ticket_system.close()

if __name__ == "__main__":
    asyncio.run(main()) 