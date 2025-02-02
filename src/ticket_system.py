import asyncio
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solana.rpc.async_api import AsyncClient
from solana.rpc.commitment import Commitment
from solana.transaction import Transaction
from solders.system_program import TransferParams, transfer
import struct
from datetime import datetime

class TicketSystem:
    def __init__(self, rpc_url="https://api.devnet.solana.com"):
        self.client = AsyncClient(rpc_url)
        
    async def create_ticket(self, owner: Keypair, price: int):
        """Create a new ticket"""
        try:
            # Create ticket account
            ticket_account = Keypair()
            
            # Calculate space needed for ticket data
            TICKET_SPACE = 8 + 32 + 8 + 1  # ticket_id + owner + price + is_used
            
            # Get minimum balance for rent exemption
            min_balance_resp = await self.client.get_minimum_balance_for_rent_exemption(TICKET_SPACE)
            min_balance = min_balance_resp.value  # Access the value property
            
            # Create transfer instruction for rent
            transfer_ix = transfer(
                TransferParams(
                    from_pubkey=owner.pubkey(),
                    to_pubkey=ticket_account.pubkey(),
                    lamports=min_balance + price
                )
            )
            
            # Pack ticket data
            ticket_data = struct.pack(
                "<Q32sQB",
                int(datetime.now().timestamp()),  # ticket_id
                bytes(owner.pubkey()),           # owner
                price,                          # price
                0                               # is_used (False)
            )
            
            # Create transaction
            transaction = Transaction()
            transaction.add(transfer_ix)
            
            # Send and confirm transaction
            recent_blockhash = await self.client.get_latest_blockhash()
            transaction.recent_blockhash = recent_blockhash.value.blockhash
            
            result = await self.client.send_transaction(
                transaction,
                owner,
            )
            
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
            return {"success": False, "error": str(e)}
    
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
            
            # Create transfer instruction to mark as used
            transfer_ix = transfer(
                TransferParams(
                    from_pubkey=ticket_pubkey,
                    to_pubkey=user.pubkey(),
                    lamports=verify_result["balance"]
                )
            )
            
            # Create and send transaction
            transaction = Transaction()
            transaction.add(transfer_ix)
            
            recent_blockhash = await self.client.get_latest_blockhash()
            transaction.recent_blockhash = recent_blockhash.value.blockhash
            
            result = await self.client.send_transaction(
                transaction,
                user
            )
            
            return {"success": True, "transaction_id": result.value}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def close(self):
        """Close the client connection"""
        await self.client.close() 