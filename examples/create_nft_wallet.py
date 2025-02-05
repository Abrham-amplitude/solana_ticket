from solders.keypair import Keypair
from rich.console import Console
import base58
import json
import os

console = Console()

def create_nft_wallet():
    """Create a new wallet specifically for NFT tickets"""
    # Create new wallet
    wallet = Keypair()
    
    # Get the hex format private key (this is what NFT tickets need)
    hex_private_key = bytes(wallet.secret()).hex()
    
    # Also get base58 format for completeness
    base58_private_key = base58.b58encode(bytes(wallet.secret())).decode('ascii')
    
    # Display information
    console.print("\n[bold cyan]=== New NFT Wallet Created ===[/bold cyan]")
    
    console.print("\n[yellow]1. Wallet Address:[/yellow]")
    console.print(str(wallet.pubkey()))
    
    console.print("\n[yellow]2. Private Key (USE THIS FOR NFT TICKETS):[/yellow]")
    console.print("[cyan]" + hex_private_key + "[/cyan]")
    console.print(f"Length: {len(hex_private_key)} characters (should be 128)")
    
    # Save to file
    wallet_data = {
        "wallet_address": str(wallet.pubkey()),
        "private_key_hex": hex_private_key,
        "private_key_base58": base58_private_key
    }
    
    # Create directory if it doesn't exist
    os.makedirs('wallets', exist_ok=True)
    wallet_file = os.path.join('wallets', 'nft_wallet.json')
    
    with open(wallet_file, "w") as f:
        json.dump(wallet_data, f, indent=2)
    
    console.print(f"\n[green]✓ Wallet details saved to {wallet_file}[/green]")
    
    # Show next steps
    console.print("\n[bold cyan]Next Steps:[/bold cyan]")
    console.print("1. Add SOL to your wallet:")
    console.print(f"   solana airdrop 1 {wallet.pubkey()} --url devnet")
    console.print("\n2. Wait 15 seconds, then check your balance:")
    console.print(f"   solana balance {wallet.pubkey()} --url devnet")
    console.print("\n3. Once you have SOL, run the ticket demo:")
    console.print("   python examples/client_demo.py")
    console.print("\n4. In the demo:")
    console.print("   a. Choose option 2 (Use existing wallet address)")
    console.print(f"   b. Enter this address: {wallet.pubkey()}")
    console.print("   c. When asked for private key, copy and paste the hex key shown above")
    
    console.print("\n[bold red]IMPORTANT:[/bold red]")
    console.print("1. Save your private key! You'll need it for NFT tickets")
    console.print("2. Make sure you have at least 0.002 SOL before buying NFT tickets")
    console.print("3. Always use the hex format private key (128 characters) for NFT operations")

if __name__ == "__main__":
    console.print("\n=== NFT Wallet Creator ===")
    console.print("This script will create a new wallet with the correct private key format for NFT tickets")
    create_nft_wallet() 