import asyncio
import os
import sys
import json
from datetime import datetime, timedelta
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.layout import Layout
import time
from solders.keypair import Keypair
from solders.pubkey import Pubkey
import base58

# Add the parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.ticket_system import TicketSystem
from src.nft_ticket_minter import NFTTicketMinter

console = Console()

def get_wallet_choice():
    """Get user's choice for wallet handling"""
    while True:
        console.print("\n[cyan]Choose wallet option:[/cyan]")
        console.print("1. Create new wallet")
        console.print("2. Use existing wallet address")
        console.print("3. View saved wallet")
        choice = input("\nEnter choice (1, 2, or 3): ").strip()
        
        if choice in ['1', '2', '3']:
            return choice
        console.print("[red]Invalid choice. Please enter 1, 2, or 3.[/red]")

def save_wallet(wallet: Keypair, filename: str = "wallet.json"):
    """Save wallet details to file"""
    try:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(filename) if os.path.dirname(filename) else '.', exist_ok=True)
        
        data = {
            "pubkey": str(wallet.pubkey()),
            "private_key": base58.b58encode(bytes(wallet.secret())).decode('ascii')
        }
        with open(filename, 'w') as f:
            json.dump(data, f)
        console.print(f"\n[green]Wallet saved successfully![/green]")
        console.print(f"[yellow]Wallet public key: {wallet.pubkey()}[/yellow]")
        console.print(f"[yellow]Wallet file: {os.path.abspath(filename)}[/yellow]")
    except Exception as e:
        console.print(f"[red]Error saving wallet: {str(e)}[/red]")

def load_wallet(filename: str = "wallet.json") -> Keypair:
    """Load wallet from file"""
    try:
        if not os.path.exists(filename):
            console.print(f"\n[yellow]No saved wallet found.[/yellow]")
            console.print("[cyan]Please choose option 1 to create a new wallet[/cyan]")
            console.print("[cyan]or option 2 to import an existing wallet.[/cyan]")
            return None
            
        with open(filename, 'r') as f:
            data = json.load(f)
        
        # Try loading from base58 format
        try:
            base58_key = data.get("private_key")
            if not base58_key:
                raise ValueError("No private key found in wallet file")
                
            private_key_bytes = base58.b58decode(base58_key)
            # Handle both 32-byte and 64-byte private keys
            if len(private_key_bytes) == 32:
                # Convert 32-byte private key to keypair
                wallet = Keypair.from_seed(private_key_bytes)
            elif len(private_key_bytes) == 64:
                # Use full 64-byte private key
                wallet = Keypair.from_bytes(private_key_bytes)
            else:
                raise ValueError(f"Invalid private key length: {len(private_key_bytes)} bytes (expected 32 or 64)")
            
            # Verify the public key matches
            if str(wallet.pubkey()) != data["pubkey"]:
                console.print("[red]Error: Public key mismatch[/red]")
                return None
                
            console.print(f"\n[green]Loaded wallet successfully[/green]")
            return wallet
            
        except Exception as e:
            console.print(f"[red]Error loading private key: {str(e)}[/red]")
            return None
            
    except Exception as e:
        console.print(f"[red]Error loading wallet: {str(e)}[/red]")
        return None

def create_new_wallet():
    """Create a new wallet and save details"""
    # Create new wallet using the default Keypair generation
    wallet = Keypair()
    
    # Get the seed bytes (32 bytes)
    seed_bytes = bytes(wallet.secret())[:32]
    
    console.print(f"\n[green]New wallet created![/green]")
    console.print(f"[yellow]Address: {wallet.pubkey()}[/yellow]")
    
    # Save wallet details with 32-byte private key
    data = {
        "pubkey": str(wallet.pubkey()),
        "private_key": base58.b58encode(seed_bytes).decode('ascii')
    }
    
    try:
        with open("wallet.json", 'w') as f:
            json.dump(data, f, indent=2)
        console.print("\n[green]Wallet saved successfully![/green]")
        console.print(f"[yellow]Wallet public key: {wallet.pubkey()}[/yellow]")
        console.print(f"[yellow]Wallet file: {os.path.abspath('wallet.json')}[/yellow]")
        
        # Show the private key
        console.print("\n[bold cyan]Private Key (SAVE THIS):[/bold cyan]")
        console.print(data["private_key"])
        
        return wallet
    except Exception as e:
        console.print(f"[red]Error saving wallet: {str(e)}[/red]")
        return None

def import_existing_wallet():
    """Import existing wallet using private key"""
    while True:
        console.print("\n[cyan]Enter your wallet's private key (base58 format):[/cyan]")
        console.print("[yellow]Note: You can get this by:[/yellow]")
        console.print("1. Creating a new wallet (option 1) and copying the private key")
        console.print("2. Using 'solana-keygen' command line tool")
        console.print("3. Exporting from a wallet like Phantom or Sollet")
        
        private_key = input("\nPrivate key: ").strip()
        try:
            decoded_key = base58.b58decode(private_key)
            if len(decoded_key) != 64:
                raise ValueError(f"Invalid key length: {len(decoded_key)}. Expected: 64 bytes")
            wallet = Keypair.from_bytes(decoded_key)
            console.print(f"[green]Wallet imported successfully![/green]")
            console.print(f"[yellow]Address: {wallet.pubkey()}[/yellow]")
            
            # Save wallet details
            save_wallet(wallet)
            return wallet
        except Exception as e:
            console.print(f"[red]Invalid private key: {str(e)}[/red]")
            console.print("\n[yellow]Tips:[/yellow]")
            console.print("1. Make sure you're using the full private key")
            console.print("2. The key should be in base58 format")
            console.print("3. Try creating a new wallet first to see the correct format")
            retry = input("\nTry again? (y/n): ").lower()
            if retry != 'y':
                return None

def view_wallet_details():
    """View saved wallet details"""
    wallet = load_wallet()
    if wallet:
        console.print("\n[bold cyan]Wallet Details:[/bold cyan]")
        console.print(f"[yellow]Public Key: {wallet.pubkey()}[/yellow]")
        
        # Show the private key format
        try:
            with open("wallet.json", 'r') as f:
                data = json.load(f)
            if "private_key" in data:
                console.print("\n[yellow]Private Key (Base58 Format):[/yellow]")
                console.print(data["private_key"])
        except Exception:
            pass
            
        console.print("\n[green]✓ Wallet loaded successfully[/green]")
        return wallet
    return None

def use_existing_wallet_address():
    """Use an existing wallet address"""
    while True:
        console.print("\n[cyan]Enter your wallet address:[/cyan]")
        address = input().strip()
        try:
            pubkey = Pubkey.from_string(address)
            console.print(f"[green]Using wallet: {pubkey}[/green]")
            return pubkey
        except ValueError:
            console.print("[red]Invalid wallet address. Please try again.[/red]")
            retry = input("Try again? (y/n): ").lower()
            if retry != 'y':
                return None

async def check_and_display_balance(client, pubkey):
    """Check and display wallet balance"""
    try:
        balance = await client.get_balance(pubkey)
        sol_balance = balance.value / 1_000_000_000
        console.print(f"\n[green]Current wallet balance: {sol_balance} SOL[/green]")
        return balance.value
    except Exception as e:
        console.print(f"[red]Error checking balance: {str(e)}[/red]")
        return 0

async def demonstrate_ticket_systems(wallet_address: Pubkey):
    """Client demonstration of both traditional and NFT ticket systems"""
    console.print("\n[bold cyan]🎫 Solana Ticketing System Demonstration[/bold cyan]")
    console.print("\nThis demo will showcase two ticketing approaches:")
    console.print("1. [green]Traditional Tickets[/green]: Simple and efficient")
    console.print("2. [blue]NFT Tickets[/blue]: Enhanced features with blockchain verification\n")

    console.print(f"[yellow]Using Wallet Address:[/yellow] {wallet_address}")
    
    # Initialize ticket system
    ticket_system = TicketSystem()
    
    try:
        while True:
            # Check wallet balance
            balance = await check_and_display_balance(ticket_system.client, wallet_address)
            
            # Calculate minimum required balance
            ticket_price = 100_000  # 0.0001 SOL for the ticket
            min_required = ticket_price + 100_000  # Additional 0.0001 SOL for fees
            
            if balance < min_required:
                console.print(f"\n[red]Insufficient balance. Minimum required: {min_required/1_000_000_000} SOL[/red]")
                console.print("\n[yellow]To add SOL to your wallet:[/yellow]")
                console.print("1. Open a new terminal")
                console.print(f"2. Run: solana airdrop 1 {wallet_address} --url devnet")
                console.print(f"3. Check balance: solana balance {wallet_address} --url devnet")
                console.print("\nWould you like to:")
                console.print("1. Check balance again")
                console.print("2. Exit")
                choice = input("\nEnter choice (1-2): ").strip()
                
                if choice == "2":
                    return
                continue
            
            # Show ticket options
            console.print("\n[bold]Available Operations:[/bold]")
            console.print("1. View ticket details")
            console.print("2. Verify ticket")
            console.print("3. Check ticket history")
            console.print("4. Buy new ticket")
            console.print("5. Check balance")
            console.print("6. Exit")
            
            choice = input("\nEnter your choice (1-6): ")
            
            if choice == "1":
                # View ticket details
                console.print("\n[bold]Ticket Details:[/bold]")
                console.print(f"Wallet Address: {wallet_address}")
                console.print(f"Available Balance: {balance/1_000_000_000} SOL")
                console.print(f"Minimum Ticket Price: {ticket_price/1_000_000_000} SOL")
            
            elif choice == "2":
                # Verify ticket
                ticket_address = input("\nEnter ticket address to verify: ")
                try:
                    ticket_pubkey = Pubkey.from_string(ticket_address)
                    verify_result = await ticket_system.verify_ticket(ticket_pubkey)
                    if verify_result["valid"]:
                        console.print("[green]✓ Ticket is valid![/green]")
                        console.print(f"Ticket Balance: {verify_result['balance']/1_000_000_000} SOL")
                    else:
                        console.print(f"[red]× Invalid ticket: {verify_result.get('error', 'Unknown error')}[/red]")
                except ValueError:
                    console.print("[red]Invalid ticket address format[/red]")
                
            elif choice == "3":
                # Check history
                console.print("\n[bold]Transaction History:[/bold]")
                console.print("This feature requires the NFT ticket address.")
                nft_address = input("Enter NFT ticket address (or press Enter to skip): ")
                if nft_address.strip():
                    try:
                        nft_pubkey = Pubkey.from_string(nft_address)
                        nft_minter = NFTTicketMinter()
                        history = await nft_minter.get_ticket_history(nft_pubkey)
                        if history["success"]:
                            for entry in history["history"]:
                                console.print(f"- {entry['type']} at {datetime.fromtimestamp(entry['timestamp'])}")
                        else:
                            console.print(f"[red]Error getting history: {history.get('error')}[/red]")
                        await nft_minter.close()
                    except ValueError:
                        console.print("[red]Invalid NFT address format[/red]")
                    
            elif choice == "4":
                # Buy new ticket
                console.print("\n[bold]Buy New Ticket[/bold]")
                console.print("\nSelect ticket type:")
                console.print("1. Traditional Ticket (0.0001 SOL)")
                console.print("2. NFT Ticket (0.001 SOL)")
                
                ticket_choice = input("\nEnter choice (1-2): ")
                
                if ticket_choice == "1":
                    # Traditional ticket
                    price = 100_000  # 0.0001 SOL
                    console.print(f"\n[yellow]Creating traditional ticket for {price/1_000_000_000} SOL...[/yellow]")
                    
                    # Get private key if not already loaded
                    private_key = None
                    if os.path.exists("wallet.json"):
                        try:
                            with open("wallet.json", 'r') as f:
                                data = json.load(f)
                                private_key = base58.b58decode(data["private_key"])
                        except Exception:
                            pass
                    
                    if not private_key:
                        console.print("\n[yellow]To buy a ticket, you need your wallet's private key.[/yellow]")
                        console.print("Enter your private key (or press Enter to cancel):")
                        key_input = input().strip()
                        if not key_input:
                            return
                        try:
                            private_key = base58.b58decode(key_input)
                        except Exception:
                            console.print("[red]Invalid private key format[/red]")
                            return
                    
                    try:
                        wallet = Keypair.from_bytes(private_key)
                        if str(wallet.pubkey()) != str(wallet_address):
                            console.print("[red]Private key does not match wallet address[/red]")
                            return
                            
                        result = await ticket_system.create_ticket(wallet, price)
                        if result["success"]:
                            console.print("\n[green]✓ Ticket purchased successfully![/green]")
                            console.print(f"Ticket Address: {result['ticket_pubkey']}")
                            console.print("[yellow]SAVE THIS TICKET ADDRESS![/yellow]")
                        else:
                            console.print(f"\n[red]Failed to purchase ticket: {result.get('error')}[/red]")
                    except Exception as e:
                        console.print(f"[red]Error purchasing ticket: {str(e)}[/red]")
                
                elif ticket_choice == "2":
                    # NFT ticket
                    price = 1_000_000  # 0.001 SOL
                    console.print(f"\n[yellow]Creating NFT ticket for {price/1_000_000_000} SOL...[/yellow]")
                    
                    # First try to load wallet from file
                    wallet = None
                    try:
                        wallet = load_wallet()
                    except Exception as e:
                        console.print(f"[red]Error loading wallet: {str(e)}[/red]")
                    
                    if not wallet:
                        console.print("\n[yellow]To buy an NFT ticket, you need your wallet's private key.[/yellow]")
                        console.print("[yellow]Enter your private key in base58 format.[/yellow]")
                        console.print("\nEnter private key (or press Enter to cancel):")
                        key_input = input().strip()
                        if not key_input:
                            continue
                            
                        try:
                            # Try base58 decode
                            private_key_bytes = base58.b58decode(key_input)
                                
                            # Handle both 32-byte and 64-byte private keys
                            if len(private_key_bytes) == 32:
                                wallet = Keypair.from_seed(private_key_bytes)
                            elif len(private_key_bytes) == 64:
                                wallet = Keypair.from_bytes(private_key_bytes)
                            else:
                                raise ValueError(f"Invalid key length: {len(private_key_bytes)} bytes (expected 32 or 64)")
                            
                            # Verify the keypair matches the wallet address
                            if str(wallet.pubkey()) != str(wallet_address):
                                raise ValueError("Private key does not match wallet address")
                                
                        except Exception as e:
                            console.print(f"[red]Invalid private key: {str(e)}[/red]")
                            continue
                    
                    if not wallet:
                        console.print("[red]No valid wallet available. Cannot proceed with purchase.[/red]")
                        continue
                    
                    try:
                        nft_minter = NFTTicketMinter()
                        
                        # Check balance first
                        balance = await check_and_display_balance(nft_minter.client, wallet_address)
                        if balance < price + 5_000_000:  # Add extra for fees (0.005 SOL for safety)
                            console.print(f"[red]Insufficient balance for NFT ticket and fees[/red]")
                            console.print(f"Required: {(price + 5_000_000)/1_000_000_000} SOL")
                            console.print(f"Current: {balance/1_000_000_000} SOL")
                            return
                        
                        event_name = "Solana Event 2024"
                        event_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
                        seat_info = {
                            "section": "VIP",
                            "row": "A",
                            "seat": "1"
                        }
                        
                        console.print("\n[yellow]Creating NFT ticket...[/yellow]")
                        result = await nft_minter.create_nft_ticket(
                            owner=wallet,
                            event_name=event_name,
                            event_date=event_date,
                            seat_info=seat_info,
                            price=price/1_000_000_000
                        )
                        
                        if result["success"]:
                            console.print("\n[green]✓ NFT Ticket purchased successfully![/green]")
                            console.print(f"NFT Address: {result['nft_address']}")
                            console.print(f"Token Account: {result['token_account']}")
                            console.print("\n[yellow]Ticket Details:[/yellow]")
                            console.print(f"Event: {event_name}")
                            console.print(f"Date: {event_date}")
                            console.print(f"Section: {seat_info['section']}")
                            console.print(f"Row: {seat_info['row']}")
                            console.print(f"Seat: {seat_info['seat']}")
                            console.print("\n[bold yellow]SAVE THESE ADDRESSES![/bold yellow]")
                        else:
                            console.print(f"\n[red]Failed to purchase NFT ticket: {result['error']}[/red]")
                            
                        await nft_minter.close()
                    except Exception as e:
                        console.print(f"[red]Error purchasing NFT ticket: {str(e)}[/red]")
                        console.print("\n[yellow]Troubleshooting tips:[/yellow]")
                        console.print("1. Make sure you have enough SOL (at least 0.006 SOL)")
                        console.print("2. Check that your private key is in base58 format")
                        console.print("3. Try creating a new wallet first to see the correct format")
                        console.print("4. Try again in a few seconds")
                else:
                    console.print("[red]Invalid choice[/red]")
            
            elif choice == "5":
                # Just continue the loop to check balance again
                continue
                
            elif choice == "6":
                break
                
            else:
                console.print("[red]Invalid choice[/red]")
            
            console.print("\nPress Enter to continue...")
            input()
        
    except Exception as e:
        console.print(f"\n[red]Error: {str(e)}[/red]")
    finally:
        await ticket_system.close()

if __name__ == "__main__":
    console.print("\n=== Solana Ticketing System Client Demo ===")
    
    # Get wallet choice
    wallet_choice = get_wallet_choice()
    wallet_address = None
    
    if wallet_choice == '1':
        # Create new wallet
        wallet = create_new_wallet()
        wallet_address = wallet.pubkey()
        
        # Show airdrop instructions and wait for user
        console.print("\n[yellow]Before continuing, you need to add SOL to your wallet:[/yellow]")
        console.print("1. Open a new terminal")
        console.print(f"2. Run: solana airdrop 1 {wallet_address} --url devnet")
        console.print(f"3. Check balance: solana balance {wallet_address} --url devnet")
        console.print("\nPress Enter after you have added SOL to continue...")
        input()
        
    elif wallet_choice == '2':
        # Use existing wallet address
        wallet_address = use_existing_wallet_address()
    else:
        # View saved wallet
        wallet = view_wallet_details()
        if wallet:
            wallet_address = wallet.pubkey()
    
    if not wallet_address:
        console.print("[red]No wallet address available. Please try again.[/red]")
        sys.exit(1)
    
    # Run the demo with the wallet address
    asyncio.run(demonstrate_ticket_systems(wallet_address)) 