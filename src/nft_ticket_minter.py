from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solana.rpc.async_api import AsyncClient
from solana.transaction import Transaction
from solders.system_program import create_account, CreateAccountParams
from solana.rpc.commitment import Commitment
from spl.token.instructions import (
    initialize_mint, 
    mint_to,
    create_associated_token_account,
    get_associated_token_address,
    burn
)
import json
from datetime import datetime
import os

class NFTTicketMinter:
    def __init__(self, rpc_url="https://api.devnet.solana.com"):
        self.client = AsyncClient(rpc_url, commitment="confirmed")
        
    async def create_nft_ticket(self, owner: Keypair, event_name: str, event_date: str, seat_info: dict, price: float):
        """Create a new NFT ticket"""
        try:
            # Create mint account
            mint_account = Keypair()
            
            # Get token program ID
            token_program_id = Pubkey.from_string("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA")
            
            # Calculate rent-exempt minimum
            space = 82  # Standard token account size
            rent = await self.client.get_minimum_balance_for_rent_exemption(space)
            
            # Create mint account transaction
            transaction = Transaction()
            
            # Create account instruction
            create_account_ix = create_account(
                CreateAccountParams(
                    from_pubkey=owner.pubkey(),
                    to_pubkey=mint_account.pubkey(),
                    lamports=rent,
                    space=space,
                    owner=token_program_id
                )
            )
            transaction.add(create_account_ix)
            
            # Initialize mint instruction
            init_mint_ix = initialize_mint(
                program_id=token_program_id,
                mint=mint_account.pubkey(),
                mint_authority=owner.pubkey(),
                freeze_authority=None,
                decimals=0
            )
            transaction.add(init_mint_ix)
            
            # Get associated token account
            token_account = get_associated_token_address(owner.pubkey(), mint_account.pubkey())
            
            # Create associated token account instruction
            create_ata_ix = create_associated_token_account(
                payer=owner.pubkey(),
                owner=owner.pubkey(),
                mint=mint_account.pubkey()
            )
            transaction.add(create_ata_ix)
            
            # Mint one token instruction
            mint_to_ix = mint_to(
                program_id=token_program_id,
                mint=mint_account.pubkey(),
                dest=token_account,
                mint_authority=owner.pubkey(),
                amount=1
            )
            transaction.add(mint_to_ix)
            
            # Get recent blockhash
            recent_blockhash = await self.client.get_latest_blockhash()
            transaction.recent_blockhash = recent_blockhash.value.blockhash
            
            # Send transaction with proper options
            opts = {
                "skip_preflight": True,
                "preflight_commitment": "confirmed",
                "encoding": "base64"
            }
            
            # Send transaction with both signers
            signers = [owner, mint_account]
            
            # Send transaction
            result = await self.client.send_transaction(
                transaction,
                *signers,
                opts=opts
            )
            
            # Wait for confirmation with increased timeout
            await self.client.confirm_transaction(result.value, commitment="confirmed")
            
            # Return success response
            return {
                "success": True,
                "nft_address": str(mint_account.pubkey()),
                "token_account": str(token_account),
                "metadata": {
                    "name": f"{event_name} Ticket",
                    "event_date": event_date,
                    "seat_info": seat_info,
                    "price": price
                },
                "owner": str(owner.pubkey()),
                "transaction_id": str(result.value)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def verify_nft_ticket(self, nft_address: Pubkey) -> dict:
        """Verify if an NFT ticket is valid"""
        try:
            # Get token account info
            account_info = await self.client.get_account_info(nft_address)
            
            if not account_info.value:
                return {
                    "valid": False,
                    "error": "Token account not found"
                }
            
            return {
                "valid": True,
                "token_data": account_info.value
            }
            
        except Exception as e:
            return {
                "valid": False,
                "error": f"Failed to verify ticket: {str(e)}"
            }
    
    async def use_nft_ticket(self, owner: Keypair, nft_address: Pubkey) -> dict:
        """Mark an NFT ticket as used by burning the token"""
        try:
            verify_result = await self.verify_nft_ticket(nft_address)
            if not verify_result["valid"]:
                return {
                    "success": False,
                    "error": "Invalid ticket"
                }
            
            # Get token account
            token_account = get_associated_token_address(owner.pubkey(), nft_address)
            
            # Create burn instruction
            burn_ix = burn(
                program_id=Pubkey.from_string("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"),
                mint=nft_address,
                account=token_account,
                owner=owner.pubkey(),
                amount=1
            )
            
            # Build transaction
            transaction = Transaction().add(burn_ix)
            
            # Get recent blockhash
            recent_blockhash = await self.client.get_latest_blockhash()
            transaction.recent_blockhash = recent_blockhash.value.blockhash
            
            # Send transaction with proper options
            opts = {
                "skip_preflight": True,
                "preflight_commitment": "confirmed",
                "encoding": "base64"
            }
            
            result = await self.client.send_transaction(
                transaction,
                owner,
                opts=opts
            )
            
            # Wait for confirmation
            await self.client.confirm_transaction(result.value)
            
            return {
                "success": True,
                "transaction_id": str(result.value)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to use ticket: {str(e)}"
            }
    
    async def get_ticket_history(self, nft_address: Pubkey) -> dict:
        """Get the transaction history for an NFT ticket"""
        try:
            signatures = await self.client.get_signatures_for_address(nft_address)
            
            history = []
            for sig in signatures:
                tx = await self.client.get_transaction(sig.signature)
                history.append({
                    "signature": str(sig.signature),
                    "timestamp": tx.block_time,
                    "slot": tx.slot,
                    "type": self._determine_transaction_type(tx)
                })
            
            return {
                "success": True,
                "history": history
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to get ticket history: {str(e)}"
            }
    
    def _determine_transaction_type(self, transaction) -> str:
        """Helper method to determine transaction type"""
        if "Initialize Mint" in str(transaction.transaction.message):
            return "Mint"
        elif "Transfer" in str(transaction.transaction.message):
            return "Transfer"
        elif "Burn" in str(transaction.transaction.message):
            return "Usage"
        return "Unknown"
    
    async def close(self):
        """Close the client connection"""
        await self.client.close() 