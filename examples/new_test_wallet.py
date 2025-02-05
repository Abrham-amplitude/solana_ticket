from solders.keypair import Keypair
from rich.console import Console
import base58
import json

console = Console()

def create_new_test_wallet():
    """Create a new test wallet with all key formats"""
    # Create new wallet
    wallet = Keypair()
    
    # Get all formats
    address = str(wallet.pubkey())
    secret_bytes = bytes(wallet.secret())  # This gets all 64 bytes
    hex_key = secret_bytes.hex()  # This will be 128 characters
    base58_key = base58.b58encode(secret_bytes).decode('ascii')
    
    # Display all information
    console.print("\n[bold cyan]=== New Test Wallet Details ===[/bold cyan]")
    
    console.print("\n[yellow]Wallet Address:[/yellow]")
    console.print(address)
    
    console.print("\n[yellow]Private Key (Hex Format - 128 characters):[/yellow]")
    console.print(hex_key)
    console.print(f"Length: {len(hex_key)} characters")
    
    console.print("\n[yellow]Private Key (Base58 Format):[/yellow]")
    console.print(base58_key)
    
    # Save to file
    wallet_data = {
        "wallet_address": address,
        "private_key_hex": hex_key,
        "private_key_base58": base58_key
    }
    
    with open("test_wallet.json", "w") as f:
        json.dump(wallet_data, f, indent=2)
    
    console.print("\n[green]Wallet details saved to test_wallet.json[/green]")
    
    # Show next steps
    console.print("\n[bold cyan]Next Steps:[/bold cyan]")
    console.print("1. Add SOL to this wallet:")
    console.print(f"   solana airdrop 1 {address} --url devnet")
    console.print("2. Run the ticket demo:")
    console.print("   python examples/client_demo.py")
    console.print("3. Choose option 2 (Use existing wallet address)")
    console.print(f"4. Enter this address: {address}")
    console.print("5. When asked for private key, use the hex format (128 characters) shown above")

if __name__ == "__main__":
    create_new_test_wallet() 