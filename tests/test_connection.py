import asyncio
from solders.pubkey import Pubkey
from solana.rpc.async_api import AsyncClient

async def test_connection():
    try:
        # Initialize connection to devnet
        client = AsyncClient("https://api.devnet.solana.com")
        
        # Your wallet address
        wallet_address = Pubkey.from_string("6HwMTvLt691UE37GJuajEpwKm8bsgYagnTEtMquSd3JL")
        
        # Check connection and balance
        balance = await client.get_balance(wallet_address)
        print(f"Connection successful!")
        # Access balance value directly from the response
        print(f"Wallet balance: {balance.value / 1000000000} SOL")  # Convert lamports to SOL
        
        # Get latest blockhash using the correct method
        latest_blockhash = await client.get_latest_blockhash()
        print(f"Latest blockhash: {latest_blockhash.value.blockhash}")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await client.close()

def main():
    print("Testing Solana connection...")
    asyncio.run(test_connection())

if __name__ == "__main__":
    main()