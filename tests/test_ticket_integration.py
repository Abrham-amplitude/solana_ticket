import pytest
import asyncio
import os
import sys
from datetime import datetime, timedelta

# Add the parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from solders.keypair import Keypair
from src.ticket_system import TicketSystem
from src.nft_ticket_minter import NFTTicketMinter

async def check_wallet_balance(client, pubkey):
    """Check if wallet has enough SOL"""
    balance = await client.get_balance(pubkey)
    return balance.value

async def test_ticket_integration():
    """Test the integration between traditional tickets and NFT tickets"""
    # Create a new wallet for testing
    wallet = Keypair()
    
    # Initialize both systems
    ticket_system = TicketSystem()
    nft_minter = NFTTicketMinter()
    
    try:
        # Add a delay to ensure balance update is reflected
        await asyncio.sleep(10)
        
        # Check wallet balance
        balance = await check_wallet_balance(nft_minter.client, wallet.pubkey())
        print(f"\nWallet balance after delay: {balance/1_000_000_000} SOL")
        
        if balance < 2_000_000_000:  # Need at least 2 SOL
            print(f"\nInsufficient balance: {balance/1_000_000_000} SOL")
            print("Please airdrop at least 2 SOL to continue")
            print(f"solana airdrop 2 {wallet.pubkey()} --url devnet")
            return
            
        print(f"\nWallet balance: {balance/1_000_000_000} SOL")
        
        # Step 1: Create a traditional ticket
        print("\nStep 1: Creating traditional ticket...")
        ticket_price = 1_000_000_000  # 1 SOL
        traditional_ticket = await ticket_system.create_ticket(wallet, ticket_price)
        
        assert traditional_ticket["success"], f"Failed to create traditional ticket: {traditional_ticket.get('error')}"
        print("Traditional ticket created successfully!")
        print(f"Ticket public key: {traditional_ticket['ticket_pubkey']}")
        
        # Step 2: Create an NFT version of the same ticket
        print("\nStep 2: Creating NFT ticket...")
        event_name = "Test Event"
        event_date = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
        seat_info = {
            "section": "Main",
            "row": "A",
            "seat": "1"
        }
        
        nft_ticket = await nft_minter.create_nft_ticket(
            owner=wallet,
            event_name=event_name,
            event_date=event_date,
            seat_info=seat_info,
            price=float(ticket_price) / 1_000_000_000,  # Convert lamports to SOL
            image_url="https://example.com/ticket.png"
        )
        
        assert nft_ticket["success"], f"Failed to create NFT ticket: {nft_ticket.get('error')}"
        print("NFT ticket created successfully!")
        print(f"NFT Address: {nft_ticket['nft_address']}")
        print(f"Data Account: {nft_ticket['data_account']}")
        print(f"Token Account: {nft_ticket['token_account']}")
        
        # Step 3: Verify both tickets
        print("\nStep 3: Verifying tickets...")
        
        # Verify traditional ticket
        trad_verify = await ticket_system.verify_ticket(traditional_ticket["ticket_pubkey"])
        assert trad_verify["valid"], "Traditional ticket verification failed"
        print("Traditional ticket verified successfully!")
        
        # Verify NFT ticket
        nft_verify = await nft_minter.verify_nft_ticket(nft_ticket["nft_address"])
        assert nft_verify["valid"], "NFT ticket verification failed"
        print("NFT ticket verified successfully!")
        
        # Step 4: Use both tickets
        print("\nStep 4: Using tickets...")
        
        # Use traditional ticket
        trad_use = await ticket_system.use_ticket(traditional_ticket["ticket_pubkey"], wallet)
        assert trad_use["success"], f"Failed to use traditional ticket: {trad_use.get('error')}"
        print("Traditional ticket used successfully!")
        
        # Use NFT ticket
        nft_use = await nft_minter.use_nft_ticket(wallet, nft_ticket["nft_address"])
        assert nft_use["success"], f"Failed to use NFT ticket: {nft_use.get('error')}"
        print("NFT ticket used successfully!")
        
        # Step 5: Verify tickets are now used
        print("\nStep 5: Verifying used status...")
        
        # Verify traditional ticket is used (should be invalid now)
        trad_verify_after = await ticket_system.verify_ticket(traditional_ticket["ticket_pubkey"])
        assert not trad_verify_after["valid"], "Traditional ticket should be invalid after use"
        print("Traditional ticket confirmed as used!")
        
        # Verify NFT ticket is used
        nft_verify_after = await nft_minter.verify_nft_ticket(nft_ticket["nft_address"])
        assert not nft_verify_after["valid"], "NFT ticket should be invalid after use"
        print("NFT ticket confirmed as used!")
        
        # Step 6: Get NFT ticket history
        print("\nStep 6: Getting NFT ticket history...")
        history = await nft_minter.get_ticket_history(nft_ticket["nft_address"])
        assert history["success"], "Failed to get NFT ticket history"
        
        print("\nNFT Ticket History:")
        for entry in history["history"]:
            print(f"- {entry['type']} at {datetime.fromtimestamp(entry['timestamp'])}")
        
        print("\nIntegration test completed successfully! ✅")
        
    except Exception as e:
        print(f"\nTest failed: {str(e)}")
        raise
        
    finally:
        # Clean up
        await ticket_system.close()
        await nft_minter.close()

if __name__ == "__main__":
    # Run the test
    print("\n=== Running Ticket Integration Test ===")
    
    # Create wallet and show address
    wallet = Keypair()
    print(f"\nTest wallet address: {wallet.pubkey()}")
    print("\nMake sure you have at least 2 SOL in your wallet before continuing.")
    print(f"Run this command to airdrop SOL: solana airdrop 2 {wallet.pubkey()} --url devnet")
    input("\nPress Enter after you have airdropped SOL to continue...")
    
    asyncio.run(test_ticket_integration())