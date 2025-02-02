import asyncio
import os
import sys

# Add the parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from solders.keypair import Keypair
from src.ticket_system import TicketSystem

async def main():
    print("\n=== Solana Ticket System Test ===\n")
    
    # Create a new wallet
    wallet = Keypair()
    print("New wallet created!")
    print("Wallet address:", wallet.pubkey())
    
    # Instructions for airdrop
    print("\nBefore creating a ticket, you need SOL in your wallet.")
    print("Follow these steps:")
    print("1. Copy and run this command in a new terminal to airdrop SOL:")
    print(f"solana airdrop 2 {wallet.pubkey()} --url devnet")
    print("\n2. Run this command to verify your balance:")
    print(f"solana balance {wallet.pubkey()} --url devnet")
    print("\n3. Make sure you see 2 SOL in your balance")
    print("4. Press Enter to continue with the test...")
    
    input()
    
    # Initialize ticket system
    ticket_system = TicketSystem()
    
    try:
        # Check balance first
        balance = await ticket_system.check_wallet_balance(wallet.pubkey())
        print(f"\nCurrent wallet balance: {balance/1000000000} SOL")
        
        if balance == 0:
            print("\nError: Your wallet has 0 SOL. Please airdrop SOL first and try again.")
            return
            
        # Create a ticket
        print("\nCreating a ticket...")
        ticket_price = 1_000_000_000  # 1 SOL
        create_result = await ticket_system.create_ticket(wallet, ticket_price)
        
        if not create_result["success"]:
            print("Failed to create ticket:", create_result["error"])
            return
            
        print("\nTicket created successfully! 🎉")
        print("Ticket public key:", create_result["ticket_pubkey"])
        print("Transaction ID:", create_result["transaction_id"])
        
        # Verify the ticket
        print("\nVerifying ticket...")
        verify_result = await ticket_system.verify_ticket(create_result["ticket_pubkey"])
        
        if not verify_result["valid"]:
            print("Ticket verification failed:", verify_result["error"])
            return
            
        print("Ticket verified successfully! ✅")
        print(f"Ticket balance: {verify_result['balance']/1000000000} SOL")
        
        # Ask user if they want to use the ticket
        print("\nWould you like to use the ticket now? (yes/no)")
        response = input().lower()
        
        if response == 'yes':
            print("\nUsing ticket...")
            use_result = await ticket_system.use_ticket(create_result["ticket_pubkey"], wallet)
            
            if not use_result["success"]:
                print("Failed to use ticket:", use_result["error"])
                return
                
            print("Ticket used successfully! 🎫")
            print("Transaction ID:", use_result["transaction_id"])
        
    except Exception as e:
        print("\nAn error occurred:", str(e))
        print("Please make sure:")
        print("1. You have enough SOL in your wallet")
        print("2. You're connected to devnet")
        print("3. The Solana network is responsive")
    
    finally:
        # Close the connection
        await ticket_system.close()

if __name__ == "__main__":
    asyncio.run(main()) 