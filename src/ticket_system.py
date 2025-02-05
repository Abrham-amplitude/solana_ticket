import asyncio
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solana.rpc.async_api import AsyncClient
from solana.transaction import Transaction
from solders.system_program import TransferParams, transfer
from solana.rpc.commitment import Commitment
import struct
from datetime import datetime

class TicketSystem:
    def __init__(self, rpc_url="https://api.devnet.solana.com"):
        """Initialize ticket system with Solana client"""
        self.client = AsyncClient(rpc_url)  # Remove commitment parameter
        
    async def check_wallet_balance(self, pubkey: Pubkey):
        """Check if wallet has enough SOL"""
        try:
            balance_response = await self.client.get_balance(pubkey)
            balance = balance_response.value
            return balance
        except Exception as e:
            print(f"Error checking balance: {e}")
            return 0
            
    async def create_ticket(self, owner: Keypair, price: int):
        """Create a new ticket"""
        try:
            # Check wallet balance first
            balance = await self.check_wallet_balance(owner.pubkey())
            if balance == 0:
                return {
                    "success": False,
                    "error": "Wallet has 0 SOL. Please airdrop some SOL first."
                }
            
            # Make sure wallet has enough SOL
            # Only need price + minimal fee (0.0001 SOL for fees)
            min_required = price + 100_000  # price + 0.0001 SOL for fees
            if balance < min_required:
                return {
                    "success": False,
                    "error": f"Insufficient balance. Wallet has {balance/1_000_000_000} SOL, needs at least {min_required/1_000_000_000} SOL"
                }
            
            # Create ticket account
            ticket_account = Keypair()
            
            # Create transfer instruction for ticket price
            transfer_ix = transfer(
                TransferParams(
                    from_pubkey=owner.pubkey(),
                    to_pubkey=ticket_account.pubkey(),
                    lamports=price
                )
            )
            
            # Create transaction
            transaction = Transaction().add(transfer_ix)
            
            # Get recent blockhash
            recent_blockhash = await self.client.get_latest_blockhash()
            transaction.recent_blockhash = recent_blockhash.value.blockhash
            
            # Send transaction
            result = await self.client.send_transaction(
                transaction,
                owner
            )
            
            # Wait for confirmation
            await self.client.confirm_transaction(result.value)
            
            return {
                "success": True,
                "ticket_pubkey": ticket_account.pubkey(),
                "transaction_id": result.value,
                "ticket_data": {
                    "owner": str(owner.pubkey()),
                    "price": price,
                    "is_used": False
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to create ticket: {str(e)}"
            }
    
    async def verify_ticket(self, ticket_pubkey: Pubkey) -> dict:
        """Verify if a ticket is valid and unused"""
        try:
            # Get account balance as verification
            balance = await self.client.get_balance(ticket_pubkey)
            
            if balance.value == 0:
                return {"valid": False, "error": "Ticket not found or invalid"}
            
            return {
                "valid": True,
                "balance": balance.value
            }
            
        except Exception as e:
            return {"valid": False, "error": str(e)}
    
    async def use_ticket(self, ticket_pubkey: Pubkey, user: Keypair) -> dict:
        """Mark a ticket as used by transferring SOL back"""
        try:
            # Verify ticket first
            verify_result = await self.verify_ticket(ticket_pubkey)
            if not verify_result["valid"]:
                return {"success": False, "error": "Invalid ticket"}
            
            # Create transfer instruction
            transfer_ix = transfer(
                TransferParams(
                    from_pubkey=ticket_pubkey,
                    to_pubkey=user.pubkey(),
                    lamports=verify_result["balance"]
                )
            )
            
            # Create transaction
            transaction = Transaction().add(transfer_ix)
            
            # Get recent blockhash
            recent_blockhash = await self.client.get_latest_blockhash()
            transaction.recent_blockhash = recent_blockhash.value.blockhash
            
            # Send transaction
            result = await self.client.send_transaction(
                transaction,
                user
            )
            
            # Wait for confirmation
            await self.client.confirm_transaction(result.value)
            
            return {"success": True, "transaction_id": result.value}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def close(self):
        """Close the client connection"""
        await self.client.close() 