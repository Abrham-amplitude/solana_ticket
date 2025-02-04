import asyncio
import os
import sys
from datetime import datetime, timedelta

# Add the parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from solders.keypair import Keypair
from src.nft_ticket_minter import NFTTicketMinter

async def demonstrate_nft_ticketing():
    print("\n=== Solana NFT Ticket System Demo ===\n")
    
    # Create a new wallet for testing
    wallet = Keypair()
    print("Created new wallet for testing:")
    print(f"Address: {wallet.pubkey()}")
    
    # Instructions for getting SOL
    print("\nBefore creating NFT tickets, you need SOL in your wallet.")
    print("Follow these steps:")
    print("1. Copy and run this command in a new terminal to airdrop SOL:")
    print(f"solana airdrop 2 {wallet.pubkey()} --url devnet")
    print("\n2. Verify your balance:")
    print(f"solana balance {wallet.pubkey()} --url devnet")
    print("\n3. Press Enter when you have SOL in your wallet...")
    
    input()
    
    # Initialize NFT ticket minter
    minter = NFTTicketMinter()
    
    try:
        # Example event details
        event_name = "Solana Blockchain Conference 2024"
        event_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
        seat_info = {
            "section": "VIP",
            "row": "A",
            "seat": "1"
        }
        price = 2.5  # SOL
        
        # Create NFT ticket
        print("\nCreating NFT ticket...")
        create_result = await minter.create_nft_ticket(
            owner=wallet,
            event_name=event_name,
            event_date=event_date,
            seat_info=seat_info,
            price=price,
            image_url="https://example.com/ticket-image.png"
        )
        
        if not create_result["success"]:
            print("Failed to create NFT ticket:", create_result["error"])
            return
            
        print("\nNFT Ticket created successfully! 🎉")
        print(f"NFT Address: {create_result['nft_address']}")
        print(f"Metadata Address: {create_result['metadata_address']}")
        print("\nTicket Details:")
        print(f"Event: {event_name}")
        print(f"Date: {event_date}")
        print(f"Section: {seat_info['section']}")
        print(f"Row: {seat_info['row']}")
        print(f"Seat: {seat_info['seat']}")
        print(f"Price: {price} SOL")
        
        # Verify the NFT ticket
        print("\nVerifying NFT ticket...")
        verify_result = await minter.verify_nft_ticket(create_result["nft_address"])
        
        if not verify_result["valid"]:
            print("Ticket verification failed:", verify_result.get("error", "Unknown error"))
            return
            
        print("NFT Ticket verified successfully! ✅")
        
        # Get ticket history
        print("\nFetching ticket history...")
        history_result = await minter.get_ticket_history(create_result["nft_address"])
        
        if history_result["success"]:
            print("\nTicket History:")
            for entry in history_result["history"]:
                print(f"- {entry['type']} at {datetime.fromtimestamp(entry['timestamp'])}")
        
        # Ask if user wants to mark ticket as used
        print("\nWould you like to mark the ticket as used? (yes/no)")
        response = input().lower()
        
        if response == "yes":
            print("\nMarking ticket as used...")
            use_result = await minter.use_nft_ticket(wallet, create_result["nft_address"])
            
            if not use_result["success"]:
                print("Failed to use ticket:", use_result["error"])
                return
                
            print("Ticket marked as used successfully! 🎫")
            print(f"Transaction ID: {use_result['transaction_id']}")
            
            # Verify ticket is now invalid
            print("\nVerifying ticket status...")
            final_verify = await minter.verify_nft_ticket(create_result["nft_address"])
            if not final_verify["valid"]:
                print("Confirmed: Ticket is now marked as used ✅")
        
    except Exception as e:
        print("\nAn error occurred:", str(e))
        print("\nTroubleshooting tips:")
        print("1. Make sure you have enough SOL in your wallet")
        print("2. Verify you're connected to devnet")
        print("3. Check that all transactions are confirmed")
    
    finally:
        await minter.close()

def main():
    """Run the NFT ticket demonstration"""
    asyncio.run(demonstrate_nft_ticketing())

if __name__ == "__main__":
    main() 