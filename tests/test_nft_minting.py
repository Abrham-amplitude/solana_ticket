import pytest
import asyncio
from solders.keypair import Keypair
from src.nft_ticket_minter import NFTTicketMinter
from datetime import datetime, timedelta

@pytest.mark.asyncio
async def test_nft_ticket_creation():
    """Test creating an NFT ticket"""
    # Initialize minter
    minter = NFTTicketMinter()
    
    # Create test wallet
    wallet = Keypair()
    
    # Test event details
    event_details = {
        "name": "Test Concert",
        "date": (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d"),
        "seat": {
            "section": "Main",
            "row": "B",
            "seat": "12"
        },
        "price": 1.5
    }
    
    try:
        # Create NFT ticket
        result = await minter.create_nft_ticket(
            owner=wallet,
            event_name=event_details["name"],
            event_date=event_details["date"],
            seat_info=event_details["seat"],
            price=event_details["price"]
        )
        
        # Verify success
        assert result["success"] is True
        assert result["nft_address"] is not None
        assert result["metadata_address"] is not None
        
        # Verify ticket details
        verify_result = await minter.verify_nft_ticket(result["nft_address"])
        assert verify_result["valid"] is True
        assert verify_result["event_name"] == event_details["name"]
        assert verify_result["event_date"] == event_details["date"]
        
        print("\nTest Results:")
        print(f"NFT Address: {result['nft_address']}")
        print(f"Metadata Address: {result['metadata_address']}")
        print(f"Owner: {result['owner']}")
        print("\nMetadata:")
        print(f"Event: {verify_result['event_name']}")
        print(f"Date: {verify_result['event_date']}")
        print(f"Seat: Section {verify_result['seat_info']['section']}, "
              f"Row {verify_result['seat_info']['row']}, "
              f"Seat {verify_result['seat_info']['seat']}")
        
    finally:
        await minter.close()

@pytest.mark.asyncio
async def test_nft_ticket_lifecycle():
    """Test the complete lifecycle of an NFT ticket"""
    minter = NFTTicketMinter()
    wallet = Keypair()
    
    try:
        # 1. Create ticket
        create_result = await minter.create_nft_ticket(
            owner=wallet,
            event_name="Lifecycle Test Event",
            event_date=datetime.now().strftime("%Y-%m-%d"),
            seat_info={"section": "Test", "row": "1", "seat": "1"},
            price=1.0
        )
        assert create_result["success"] is True
        
        # 2. Verify ticket
        verify_result = await minter.verify_nft_ticket(create_result["nft_address"])
        assert verify_result["valid"] is True
        
        # 3. Get history
        history_result = await minter.get_ticket_history(create_result["nft_address"])
        assert history_result["success"] is True
        
        # 4. Use ticket
        use_result = await minter.use_nft_ticket(wallet, create_result["nft_address"])
        assert use_result["success"] is True
        
        # 5. Verify ticket is now invalid
        final_verify = await minter.verify_nft_ticket(create_result["nft_address"])
        assert final_verify["valid"] is False
        
        print("\nLifecycle Test Results:")
        print("✅ Ticket Creation")
        print("✅ Ticket Verification")
        print("✅ History Tracking")
        print("✅ Ticket Usage")
        print("✅ Post-Usage Verification")
        
    finally:
        await minter.close()

def main():
    """Run the tests"""
    print("\n=== NFT Ticket System Tests ===\n")
    
    # Run creation test
    print("Running NFT Ticket Creation Test...")
    asyncio.run(test_nft_ticket_creation())
    
    print("\nRunning NFT Ticket Lifecycle Test...")
    asyncio.run(test_nft_ticket_lifecycle())
    
if __name__ == "__main__":
    main() 