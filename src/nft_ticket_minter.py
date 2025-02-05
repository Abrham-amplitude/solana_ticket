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
    burn,
    InitializeMintParams,
    MintToParams
)
import json
from datetime import datetime
import os

class NFTTicketMinter:
    def __init__(self, rpc_url="https://api.devnet.solana.com"):
        """Initialize NFT ticket minter with Solana client"""
        self.client = AsyncClient(rpc_url)  # Remove commitment parameter
        
    async def create_nft_ticket(self, owner: Keypair, event_name: str, event_date: str, seat_info: dict, price: float):
        """Create a new NFT ticket"""
        try:
            # Create mint account
            mint_account = Keypair()
            
            # Get token program ID
            token_program_id = Pubkey.from_string("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA")
            
            # Calculate rent-exempt minimum for mint account
            mint_space = 82  # Standard token account size
            mint_rent_response = await self.client.get_minimum_balance_for_rent_exemption(mint_space)
            mint_rent = mint_rent_response.value  # Extract the actual value from the response
            
            # Check owner's balance
            owner_balance = await self.client.get_balance(owner.pubkey())
            print(f"Owner balance: {owner_balance.value}")
            if owner_balance.value < mint_rent + 5_000_000:  # mint_rent + extra for fees
                return {
                    "success": False,
                    "error": f"Insufficient balance. Need at least {(mint_rent + 5_000_000) / 1_000_000_000} SOL"
                }
            
            # Create transaction
            transaction = Transaction()
            
            # Create mint account with proper rent
            create_mint_account_ix = create_account(
                CreateAccountParams(
                    from_pubkey=owner.pubkey(),
                    to_pubkey=mint_account.pubkey(),
                    lamports=mint_rent,
                    space=mint_space,
                    owner=token_program_id
                )
            )
            transaction.add(create_mint_account_ix)
            
            # Initialize mint
            init_mint_ix = initialize_mint(
                InitializeMintParams(
                    program_id=token_program_id,
                    mint=mint_account.pubkey(),
                    decimals=0,
                    mint_authority=owner.pubkey(),
                    freeze_authority=None
                )
            )
            transaction.add(init_mint_ix)
            
            # Get associated token account
            token_account = get_associated_token_address(
                owner.pubkey(),
                mint_account.pubkey()
            )
            
            # Create associated token account
            create_ata_ix = create_associated_token_account(
                owner.pubkey(),  # payer
                owner.pubkey(),  # wallet_address
                mint_account.pubkey()  # token_mint
            )
            transaction.add(create_ata_ix)
            
            # Mint one token
            mint_to_ix = mint_to(
                MintToParams(
                    program_id=token_program_id,
                    mint=mint_account.pubkey(),
                    dest=token_account,
                    mint_authority=owner.pubkey(),
                    amount=1,
                    signers=[]  # Empty list since we're signing with the transaction
                )
            )
            transaction.add(mint_to_ix)
            
            # Get recent blockhash
            recent_blockhash = await self.client.get_latest_blockhash()
            transaction.recent_blockhash = recent_blockhash.value.blockhash
            
            try:
                # Send and confirm transaction with both signers
                signers = [owner, mint_account]
                result = await self.client.send_transaction(
                    transaction,
                    *signers
                )
                
                # Wait for confirmation
                await self.client.confirm_transaction(result.value)
                
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
            
            # Send transaction
            result = await self.client.send_transaction(
                transaction,
                owner
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
        await self.client.close() 