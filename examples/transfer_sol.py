import asyncio
import os
import sys
from solders.keypair import Keypair
from solana.rpc.async_api import AsyncClient
from solana.transaction import Transaction
from solders.system_program import TransferParams, transfer
from rich.console import Console
import base58

# Add the parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

console = Console()

async def transfer_sol():
    """Transfer SOL from existing wallet to new test wallet"""
    # Create new test wallet
    new_wallet = Keypair()
    console.print(f"\n[green]Created new test wallet:[/green]")
    console.print(f"[yellow]Address: {new_wallet.pubkey()}[/yellow]")
    console.print(f"[red]Private Key: {base58.b58encode(bytes(new_wallet.secret())).decode('ascii')}[/red]")
    console.print("[yellow]SAVE THIS PRIVATE KEY! You'll need it for testing.[/yellow]")
    
    # Show transfer instructions
    console.print("\n[cyan]To transfer SOL to this test wallet:[/cyan]")
    console.print("1. Open Solana CLI in a new terminal")
    console.print(f"2. Run this command to transfer 0.002 SOL:")
    console.print(f"[white]solana transfer {new_wallet.pubkey()} 0.002 --from YOUR_KEYPAIR_PATH --url devnet[/white]")
    console.print("\nOr use these alternative methods:")
    console.print("1. Use Phantom wallet to send SOL")
    console.print("2. Use Solana Explorer to send SOL")
    console.print("3. Use any other Solana wallet that can send SOL")
    
    # Wait for transfer
    console.print("\n[cyan]After sending SOL, check the balance:[/cyan]")
    console.print(f"solana balance {new_wallet.pubkey()} --url devnet")
    
    # Save wallet details
    data = {
        "pubkey": str(new_wallet.pubkey()),
        "private_key": base58.b58encode(bytes(new_wallet.secret())).decode('ascii')
    }
    with open("test_wallet.json", 'w') as f:
        import json
        json.dump(data, f)
    console.print(f"\n[green]Wallet details saved to test_wallet.json[/green]")

if __name__ == "__main__":
    asyncio.run(transfer_sol()) 