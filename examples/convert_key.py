import base58
from rich.console import Console
from solders.keypair import Keypair

console = Console()

def convert_private_key():
    """Convert private key between formats"""
    console.print("\n[bold cyan]=== Private Key Format Converter ===[/bold cyan]")
    
    # Get the base58 private key
    console.print("\n[yellow]Enter your base58 private key:[/yellow]")
    console.print("Example: 8wXGYtzwGEvmmdYWrmi8cCsz7euyCHqA4Kas5FhjUUPf")
    base58_key = input().strip()
    
    try:
        # Convert base58 to bytes
        key_bytes = base58.b58decode(base58_key)
        
        # Create a keypair from the bytes
        keypair = Keypair.from_bytes(key_bytes)
        
        # Get the full secret key in hex format (this will be 128 characters)
        hex_key = bytes(keypair.secret()).hex()
        
        console.print("\n[green]Conversion successful![/green]")
        console.print("\n[yellow]Your private key in different formats:[/yellow]")
        console.print(f"\n[cyan]Base58 Format (original):[/cyan]")
        console.print(base58_key)
        console.print(f"\n[cyan]Hex Format (64 bytes/128 characters):[/cyan]")
        console.print(hex_key)
        
        # Verify the length
        console.print(f"\n[green]Hex key length: {len(hex_key)} characters[/green]")
        if len(hex_key) == 128:
            console.print("[green]✓ Correct length for hex format[/green]")
            console.print("\n[bold cyan]You can use this hex key in the ticket demo[/bold cyan]")
        else:
            console.print("[red]⚠ Unexpected length for hex format[/red]")
            
        # Also show the wallet address for verification
        console.print(f"\n[yellow]Wallet Address (for verification):[/yellow]")
        console.print(str(keypair.pubkey()))
            
        # Save to file
        import json
        data = {
            "wallet_address": str(keypair.pubkey()),
            "base58_key": base58_key,
            "hex_key": hex_key
        }
        with open("converted_key.json", "w") as f:
            json.dump(data, f, indent=2)
        console.print("\n[green]Key formats saved to converted_key.json[/green]")
        
    except Exception as e:
        console.print(f"\n[red]Error converting key: {str(e)}[/red]")
        console.print("[yellow]Make sure you entered the correct base58 private key[/yellow]")
        console.print("[yellow]The private key should be the one shown when you created the wallet[/yellow]")

if __name__ == "__main__":
    convert_private_key() 