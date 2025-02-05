import asyncio
from solders.keypair import Keypair
from rich.console import Console
import base58

console = Console()

def create_test_wallet():
    """Create a new test wallet and show details"""
    # Create new wallet
    wallet = Keypair()
    
    # Get wallet details
    address = str(wallet.pubkey())
    private_key_bytes = bytes(wallet.secret())
    private_key_hex = private_key_bytes.hex()
    private_key_base58 = base58.b58encode(private_key_bytes).decode('ascii')
    
    # Display wallet information
    console.print("\n[bold cyan]=== New Test Wallet Details ===[/bold cyan]")
    console.print("\n[yellow]Wallet Address:[/yellow]")
    console.print(address)
    
    console.print("\n[yellow]Private Key (Hex Format - 64 bytes/128 characters):[/yellow]")
    console.print(private_key_hex)
    
    console.print("\n[yellow]Private Key (Base58 Format):[/yellow]")
    console.print(private_key_base58)
    
    console.print("\n[bold green]Instructions:[/bold green]")
    console.print("1. Save both private key formats")
    console.print("2. You can use either format when asked for the private key")
    console.print("3. The hex format is 128 characters long")
    console.print("4. The Base58 format is shorter but equivalent")
    
    # Save to file
    wallet_data = {
        "address": address,
        "private_key_hex": private_key_hex,
        "private_key_base58": private_key_base58
    }
    
    import json
    with open("new_wallet.json", "w") as f:
        json.dump(wallet_data, f, indent=2)
    
    console.print("\n[green]Wallet details saved to new_wallet.json[/green]")
    
    # Show next steps
    console.print("\n[bold cyan]Next Steps:[/bold cyan]")
    console.print("1. Add SOL to this wallet:")
    console.print(f"   solana airdrop 1 {address} --url devnet")
    console.print("2. Run the ticket demo:")
    console.print("   python examples/client_demo.py")
    console.print("3. Choose option 2 (Use existing wallet address)")
    console.print("4. When asked for private key, use either format shown above")

if __name__ == "__main__":
    create_test_wallet() 