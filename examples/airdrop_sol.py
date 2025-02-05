import asyncio
import os
import sys
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solana.rpc.async_api import AsyncClient
from rich.console import Console
import base58
import time
import json

# Add the parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

console = Console()

async def request_airdrop(client, wallet_address, amount_sol=0.5):
    """Request airdrop with amount in SOL"""
    try:
        amount_lamports = int(amount_sol * 1_000_000_000)  # Convert SOL to lamports
        result = await client.request_airdrop(wallet_address, amount_lamports)
        await client.confirm_transaction(result.value)
        return True
    except Exception as e:
        console.print(f"[red]Airdrop failed: {str(e)}[/red]")
        return False

async def check_balance(client, wallet_address):
    """Check wallet balance"""
    try:
        balance = await client.get_balance(wallet_address)
        return balance.value / 1_000_000_000  # Convert lamports to SOL
    except Exception as e:
        console.print(f"[red]Error checking balance: {str(e)}[/red]")
        return 0

async def check_wallet_balance(wallet_address_str):
    """Check balance of any wallet address"""
    client = AsyncClient("https://api.devnet.solana.com")
    try:
        wallet_pubkey = Pubkey.from_string(wallet_address_str)
        balance = await check_balance(client, wallet_pubkey)
        console.print(f"[cyan]Wallet {wallet_address_str} balance: {balance} SOL[/cyan]")
        return balance
    finally:
        await client.close()

async def airdrop_with_retry():
    """Airdrop SOL with retries and delays"""
    # First, check if we have a wallet with balance
    known_wallets = [
        "AuoBjcHWmFtimbVfVsHUdZ7gpbBGjhNPjiuULQun4vd5",  # Known wallet with balance
    ]
    
    console.print("\n[cyan]Checking known wallets for balance...[/cyan]")
    for wallet_addr in known_wallets:
        balance = await check_wallet_balance(wallet_addr)
        if balance > 0:
            console.print(f"[green]Found wallet with balance![/green]")
            console.print(f"[yellow]Address: {wallet_addr}[/yellow]")
            console.print(f"[yellow]Balance: {balance} SOL[/yellow]")
            console.print("\n[bold cyan]You can use this wallet for testing.[/bold cyan]")
            return
    
    # If no wallet with balance found, create new one
    console.print("\n[yellow]No wallet with balance found. Creating new wallet...[/yellow]")
    
    # Create new wallet
    wallet = Keypair()
    console.print(f"\n[green]Created new test wallet:[/green]")
    console.print(f"[yellow]Address: {wallet.pubkey()}[/yellow]")
    
    # Save private key
    private_key = base58.b58encode(bytes(wallet.secret())).decode('ascii')
    console.print(f"[red]Private Key: {private_key}[/red]")
    console.print("[yellow]SAVE THIS PRIVATE KEY! You'll need it for testing.[/yellow]")
    
    # Initialize client
    client = AsyncClient("https://api.devnet.solana.com")
    
    try:
        # Initial balance check
        balance = await check_balance(client, wallet.pubkey())
        console.print(f"\n[cyan]Initial balance: {balance} SOL[/cyan]")
        
        # Target amount
        target_sol = 0.5  # We'll try to get 0.5 SOL total
        max_retries = 5
        delay_between_requests = 3600  # Increased delay to 5 seconds
        
        for attempt in range(max_retries):
            current_balance = await check_balance(client, wallet.pubkey())
            if current_balance >= target_sol:
                console.print(f"[green]Target balance reached: {current_balance} SOL[/green]")
                break
                
            amount_needed = min(0.1, target_sol - current_balance)  # Request 0.1 SOL at a time
            console.print(f"\n[yellow]Requesting {amount_needed} SOL (Attempt {attempt + 1}/{max_retries})[/yellow]")
            
            success = await request_airdrop(client, wallet.pubkey(), amount_needed)
            if success:
                new_balance = await check_balance(client, wallet.pubkey())
                console.print(f"[green]Airdrop successful! New balance: {new_balance} SOL[/green]")
            else:
                console.print("[red]Airdrop failed, waiting before retry...[/red]")
                console.print("[yellow]You can also try these alternatives:[/yellow]")
                console.print("1. Use Solana CLI: solana airdrop 1 " + str(wallet.pubkey()) + " --url devnet")
                console.print("2. Use Solana Explorer: https://explorer.solana.com/?cluster=devnet")
                console.print("3. Use an existing wallet with balance")
            
            # Wait before next attempt
            if attempt < max_retries - 1:
                console.print(f"[yellow]Waiting {delay_between_requests} seconds...[/yellow]")
                await asyncio.sleep(delay_between_requests)
        
        # Final balance check
        final_balance = await check_balance(client, wallet.pubkey())
        console.print(f"\n[bold cyan]Final wallet balance: {final_balance} SOL[/bold cyan]")
        
        if final_balance == 0:
            console.print("\n[red]Could not get SOL via airdrop. Please use this known wallet with balance:[/red]")
            console.print("[green]Address: AuoBjcHWmFtimbVfVsHUdZ7gpbBGjhNPjiuULQun4vd5[/green]")
            return
        
        # Save wallet details
        data = {
            "pubkey": str(wallet.pubkey()),
            "private_key": private_key
        }
        with open("test_wallet.json", 'w') as f:
            json.dump(data, f)
        console.print(f"\n[green]Wallet details saved to test_wallet.json[/green]")
        
        # Show next steps
        console.print("\n[bold cyan]Next steps:[/bold cyan]")
        console.print("1. Run the ticket demo:")
        console.print("   python examples/client_demo.py")
        console.print("2. Choose option 2 (Use existing wallet address)")
        console.print(f"3. Enter this address: {wallet.pubkey()}")
        console.print("4. When asked for private key, use the one shown above")
        
    finally:
        await client.close()

if __name__ == "__main__":
    console.print("\n=== Solana Airdrop Helper ===")
    console.print("This script will check known wallets with balance and create new wallet if needed")
    asyncio.run(airdrop_with_retry()) 