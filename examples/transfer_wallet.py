import asyncio
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solana.rpc.async_api import AsyncClient
from solana.transaction import Transaction
from solders.system_program import TransferParams, transfer
from rich.console import Console
import base58
import json

console = Console()

async def check_balance(client, pubkey):
    """Check wallet balance"""
    try:
        balance = await client.get_balance(pubkey)
        return balance.value / 1_000_000_000  # Convert lamports to SOL
    except Exception as e:
        console.print(f"[red]Error checking balance: {str(e)}[/red]")
        return 0

async def transfer_sol():
    """Create new wallet and transfer SOL from existing wallet"""
    # Create new wallet
    new_wallet = Keypair()
    console.print(f"\n[green]Created new wallet:[/green]")
    console.print(f"[yellow]Address: {new_wallet.pubkey()}[/yellow]")
    
    # Get the hex format private key (this will be 128 characters)
    hex_key = bytes(new_wallet.secret()).hex()
    console.print(f"\n[yellow]Private Key (Hex Format - 128 characters):[/yellow]")
    console.print(hex_key)
    console.print(f"Length: {len(hex_key)} characters")
    
    # Initialize client
    client = AsyncClient("https://api.devnet.solana.com")
    
    try:
        # Source wallet (the one with 0.008 SOL)
        source_wallet = "AuoBjcHWmFtimbVfVsHUdZ7gpbBGjhNPjiuULQun4vd5"
        source_pubkey = Pubkey.from_string(source_wallet)
        
        # Check source wallet balance
        source_balance = await check_balance(client, source_pubkey)
        console.print(f"\n[cyan]Source wallet balance: {source_balance} SOL[/cyan]")
        
        if source_balance > 0:
            console.print("\n[yellow]To transfer SOL to the new wallet:[/yellow]")
            console.print(f"1. Open a new terminal")
            console.print(f"2. Run this command:")
            console.print(f"[white]solana transfer {new_wallet.pubkey()} 0.005 --from YOUR_KEYPAIR_PATH --url devnet[/white]")
            console.print(f"\nOr use these alternatives:")
            console.print("1. Use Phantom wallet to send SOL")
            console.print("2. Use Solana Explorer to send SOL")
            console.print(f"3. Use any other Solana wallet to send SOL to: {new_wallet.pubkey()}")
        
        # Save wallet details
        wallet_data = {
            "wallet_address": str(new_wallet.pubkey()),
            "private_key_hex": hex_key,
            "private_key_base58": base58.b58encode(bytes(new_wallet.secret())).decode('ascii')
        }
        
        with open("new_wallet.json", "w") as f:
            json.dump(wallet_data, f, indent=2)
        console.print(f"\n[green]Wallet details saved to new_wallet.json[/green]")
        
        # Show next steps
        console.print("\n[bold cyan]Next Steps:[/bold cyan]")
        console.print("1. Transfer SOL to the new wallet using one of the methods above")
        console.print("2. Run the ticket demo:")
        console.print("   python examples/client_demo.py")
        console.print("3. Choose option 2 (Use existing wallet address)")
        console.print(f"4. Enter this address: {new_wallet.pubkey()}")
        console.print("5. When asked for private key, use the hex format (128 characters) shown above")
        
    finally:
        await client.close()

if __name__ == "__main__":
    console.print("\n=== Solana Wallet Transfer Helper ===")
    console.print("This script will create a new wallet and help you transfer SOL to it")
    asyncio.run(transfer_sol()) 