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
        console.print("2. Import existing wallet (with private key)")
        console.print("3. View wallet details")
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
        private_key = base58.b58decode(data["private_key"])
        wallet = Keypair.from_bytes(private_key)
        return wallet
    except Exception as e:
        if isinstance(e, FileNotFoundError):
            console.print("[yellow]No wallet file found. Please create or import a wallet first.[/yellow]")
        else:
            console.print(f"[red]Error loading wallet: {str(e)}[/red]")
        return None

def create_new_wallet():
    """Create a new wallet and save details"""
    wallet = Keypair()
    console.print(f"\n[green]New wallet created![/green]")
    console.print(f"[yellow]Address: {wallet.pubkey()}[/yellow]")
    
    # Show private key (only for development/testing)
    private_key = base58.b58encode(bytes(wallet.secret())).decode('ascii')
    console.print(f"[red]SAVE THIS PRIVATE KEY (for testing only):[/red]")
    console.print(f"[red]{private_key}[/red]")
    
    # Save wallet details
    save_wallet(wallet)
    return wallet

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
        console.print("[green]✓ Wallet loaded successfully[/green]")
        return wallet
    return None

def get_sol_amount():
    """Get desired SOL amount from user"""
    while True:
        console.print("\n[cyan]Enter SOL amount to use:[/cyan]")
        console.print("[yellow]Recommended amounts:[/yellow]")
        console.print("- Minimum: 0.00001 SOL")
        console.print("- Standard: 0.001 SOL")
        console.print("- Maximum: 2.0 SOL")
        try:
            amount = float(input("Amount in SOL: ").strip())
            if 0.00001 <= amount <= 2.0:  # Much lower minimum limit
                if amount < 0.001:
                    console.print("[yellow]Warning: Very small amount. Transaction might fail due to rent costs.[/yellow]")
                    console.print("Do you want to continue? (y/n)")
                    if input().lower() == 'y':
                        return amount
                else:
                    return amount
            console.print("[red]Please enter an amount between 0.00001 and 2.0 SOL[/red]")
        except ValueError:
            console.print("[red]Please enter a valid number[/red]")

async def check_wallet_balance(client, pubkey):
    """Check if wallet has enough SOL"""
    try:
        balance = await client.get_balance(pubkey)
        return balance.value
    except Exception as e:
        console.print(f"[red]Error checking balance: {str(e)}[/red]")
        return 0

async def wait_for_balance(client, pubkey, required_balance, max_attempts=5):
    """Wait for wallet to receive SOL"""
    for i in range(max_attempts):
        balance = await check_wallet_balance(client, pubkey)
        if balance >= required_balance:
            return True
        if i < max_attempts - 1:
            console.print(f"[yellow]Waiting for SOL... Current balance: {balance/1_000_000_000} SOL[/yellow]")
            await asyncio.sleep(5)  # Wait 5 seconds between checks
    return False

async def demonstrate_ticket_systems(wallet: Keypair):
    """Client demonstration of both traditional and NFT ticket systems"""
    console.print("\n[bold cyan]🎫 Solana Ticketing System Demonstration[/bold cyan]")
    console.print("\nThis demo will showcase two ticketing approaches:")
    console.print("1. [green]Traditional Tickets[/green]: Simple and efficient")
    console.print("2. [blue]NFT Tickets[/blue]: Enhanced features with blockchain verification\n")

    console.print(f"[yellow]Using Wallet Address:[/yellow] {wallet.pubkey()}")
    
    # Initialize both systems
    ticket_system = TicketSystem()
    nft_minter = NFTTicketMinter()
    
    try:
        # Check wallet balance
        balance = await check_wallet_balance(nft_minter.client, wallet.pubkey())
        console.print(f"\n[green]Current wallet balance: {balance/1_000_000_000} SOL[/green]")
        
        try:
            # Check if wallet has private key by attempting to access it
            wallet.secret()
        except Exception:
            console.print("\n[red]This is a read-only wallet. For the demo, you need a wallet with a private key.[/red]")
            console.print("[yellow]Please use option 2 to import an existing wallet instead.[/yellow]")
            return

        # Check wallet balance with smaller minimum
        required_balance = 10_000  # 0.00001 SOL minimum
        console.print(f"\n[yellow]Checking wallet balance (need {required_balance/1_000_000_000} SOL)...[/yellow]")
        
        balance = await check_wallet_balance(nft_minter.client, wallet.pubkey())
        console.print(f"\n[green]Current wallet balance: {balance/1_000_000_000} SOL[/green]")
        
        if balance < required_balance:
            console.print(f"\n[red]Insufficient balance. Please try these methods to get SOL:[/red]")
            console.print("1. Airdrop a small amount of SOL:")
            console.print(f"   solana airdrop 0.00001 {wallet.pubkey()} --url devnet")
            console.print("2. Try a different RPC endpoint:")
            console.print("   solana config set --url https://api.devnet.solana.com")
            console.print("3. Use Solana Faucet website:")
            console.print("   https://solfaucet.com")
            return

        # Create comparison table
        table = Table(title="Ticket System Comparison")
        table.add_column("Feature", style="cyan")
        table.add_column("Traditional Ticket", style="green")
        table.add_column("NFT Ticket", style="blue")
        
        # Step 1: Create tickets
        console.print("\n[bold]Step 1: Creating Tickets[/bold]")
        
        # Traditional ticket
        ticket_price = 1_000_000  # 0.001 SOL
        traditional_ticket = await ticket_system.create_ticket(wallet, ticket_price)
        
        if not traditional_ticket.get("success"):
            console.print(f"[red]Failed to create traditional ticket: {traditional_ticket.get('error')}[/red]")
            return
            
        console.print("[green]Traditional ticket created successfully![/green]")
        
        # NFT ticket
        event_name = "Solana Conference 2024"
        event_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
        seat_info = {
            "section": "VIP",
            "row": "A",
            "seat": "1"
        }
        
        nft_ticket = await nft_minter.create_nft_ticket(
            owner=wallet,
            event_name=event_name,
            event_date=event_date,
            seat_info=seat_info,
            price=float(ticket_price) / 1_000_000_000,
            image_url="https://example.com/ticket.png"
        )
        
        if not nft_ticket.get("success"):
            console.print(f"[red]Failed to create NFT ticket: {nft_ticket.get('error')}[/red]")
            return
            
        console.print("[green]NFT ticket created successfully![/green]")
        
        # Add creation results to table
        table.add_row(
            "Creation",
            "✅ Simple account creation",
            "✅ NFT minting with metadata"
        )
        table.add_row(
            "Storage",
            f"Account: {traditional_ticket.get('ticket_data', {}).get('owner', 'N/A')[:16]}...",
            f"NFT: {nft_ticket.get('nft_address', 'N/A')[:16]}..."
        )
        
        # Step 2: Verify tickets
        console.print("\n[bold]Step 2: Verifying Tickets[/bold]")
        
        trad_verify = await ticket_system.verify_ticket(traditional_ticket["ticket_pubkey"])
        nft_verify = await nft_minter.verify_nft_ticket(nft_ticket["nft_address"])
        
        table.add_row(
            "Verification",
            "✅ Balance-based verification" if trad_verify.get("valid") else "❌ Verification failed",
            "✅ On-chain metadata verification" if nft_verify.get("valid") else "❌ Verification failed"
        )
        
        # Step 3: Show ticket details
        console.print("\n[bold]Step 3: Ticket Details[/bold]")
        
        # Create ticket detail panels
        trad_panel = Panel(
            f"""
            [green]Traditional Ticket Details[/green]
            Ticket ID: {traditional_ticket.get('ticket_pubkey', 'N/A')[:16]}...
            Price: {ticket_price/1_000_000_000} SOL
            Status: {'Valid' if trad_verify.get('valid') else 'Invalid'}
            """,
            title="Traditional Ticket"
        )
        
        nft_panel = Panel(
            f"""
            [blue]NFT Ticket Details[/blue]
            NFT Address: {nft_ticket.get('nft_address', 'N/A')[:16]}...
            Event: {event_name}
            Date: {event_date}
            Seat: Section {seat_info['section']}, Row {seat_info['row']}, Seat {seat_info['seat']}
            Price: {ticket_price/1_000_000_000} SOL
            Status: {'Valid' if nft_verify.get('valid') else 'Invalid'}
            """,
            title="NFT Ticket"
        )
        
        # Display panels side by side
        layout = Layout()
        layout.split_row(
            Layout(trad_panel, name="traditional"),
            Layout(nft_panel, name="nft")
        )
        console.print(layout)
        
        # Step 4: Use tickets
        console.print("\n[bold]Step 4: Using Tickets[/bold]")
        
        trad_use = await ticket_system.use_ticket(traditional_ticket["ticket_pubkey"], wallet)
        nft_use = await nft_minter.use_nft_ticket(wallet, nft_ticket["nft_address"])
        
        table.add_row(
            "Usage",
            "✅ Simple transfer back",
            "✅ Token burning with history"
        )
        
        # Step 5: Show history
        console.print("\n[bold]Step 5: Transaction History[/bold]")
        
        history = await nft_minter.get_ticket_history(nft_ticket["nft_address"])
        
        table.add_row(
            "History Tracking",
            "❌ Not available",
            "✅ Full transaction history"
        )
        
        if history["success"]:
            console.print("\n[blue]NFT Ticket History:[/blue]")
            for entry in history["history"]:
                console.print(f"  ▪ {entry['type']} at {datetime.fromtimestamp(entry['timestamp'])}")
        
        # Display final comparison table
        console.print("\n[bold]System Comparison Summary[/bold]")
        console.print(table)
        
        # Display benefits
        console.print("\n[bold]Key Benefits of NFT Tickets:[/bold]")
        console.print("✨ Enhanced security through blockchain verification")
        console.print("✨ Rich metadata storage (event details, seat info)")
        console.print("✨ Transaction history tracking")
        console.print("✨ Potential for secondary market trading")
        console.print("✨ Collectible value for special events")
        
        console.print("\n[bold green]Demo completed successfully! ✅[/bold green]")
        
    except Exception as e:
        console.print(f"\n[red]Demo failed: {str(e)}[/red]")
        console.print("\n[yellow]Troubleshooting tips:[/yellow]")
        console.print("1. Make sure you have enough SOL in your wallet")
        console.print("2. Check your internet connection")
        console.print("3. Try using a different RPC endpoint")
        raise
        
    finally:
        # Clean up
        await ticket_system.close()
        await nft_minter.close()

if __name__ == "__main__":
    console.print("\n=== Solana Ticketing System Client Demo ===")
    
    while True:
        # Get wallet choice
        wallet_choice = get_wallet_choice()
        wallet = None
        
        # Handle wallet operations
        if wallet_choice == '1':
            wallet = create_new_wallet()
            break
        elif wallet_choice == '2':
            wallet = import_existing_wallet()
            if wallet:
                break
        else:
            wallet = view_wallet_details()
            if wallet:
                break
            console.print("\n[yellow]Would you like to try another option? (y/n)[/yellow]")
            if input().lower() != 'y':
                console.print("[red]Exiting demo. Please run again to create or import a wallet.[/red]")
                sys.exit(1)
            continue
    
    if not wallet:
        console.print("[red]No wallet available. Please create or import a wallet to continue.[/red]")
        sys.exit(1)
    
    # Get desired SOL amount
    sol_amount = get_sol_amount()
    lamports_amount = int(sol_amount * 1_000_000_000)
    
    # Show airdrop instructions
    console.print(f"\n[yellow]Make sure you have at least {sol_amount} SOL in your wallet before continuing.[/yellow]")
    console.print(f"Run this command to airdrop SOL (you may need to run multiple times):")
    console.print(f"[cyan]solana airdrop {sol_amount} {wallet.pubkey()} --url devnet[/cyan]")
    
    # Additional helpful information
    console.print("\n[yellow]Tips:[/yellow]")
    console.print("1. If airdrop fails, try smaller amounts (0.001 SOL)")
    console.print("2. You can use multiple airdrops to reach your target amount")
    console.print("3. Check your balance with:")
    console.print(f"[cyan]solana balance {wallet.pubkey()} --url devnet[/cyan]")
    
    # Wait for user to get SOL
    input("\nPress Enter after you have airdropped SOL to continue...")
    
    # Run the demo
    async def run_demo():
        ticket_system = TicketSystem()
        client = ticket_system.client
        balance = await check_wallet_balance(client, wallet.pubkey())
        
        if balance < lamports_amount:
            console.print(f"\n[red]Insufficient balance: {balance/1_000_000_000} SOL[/red]")
            console.print(f"[red]Required balance: {sol_amount} SOL[/red]")
            await ticket_system.close()
            return
            
        await demonstrate_ticket_systems(wallet)
    
    asyncio.run(run_demo()) 