from solana.rpc.async_api import AsyncClient
from solana.rpc.commitment import Commitment
from solana.keypair import Keypair
from solana.transaction import Transaction
from solana.system_program import TransactionInstruction, create_account
from solana.publickey import PublicKey
import struct
from datetime import datetime
from typing import Optional, Dict
import base58

class TicketClient:
    def __init__(self, rpc_url="https://api.devnet.solana.com"):
        self.client = AsyncClient(rpc_url, commitment=Commitment.CONFIRMED)
        self.program_id = PublicKey("YOUR_PROGRAM_ID_HERE")  # You'll get this after deploying
        
    async def create_ticket(self, payer: Keypair, event_id: int, price: int):
        """Create a new ticket"""
        # Generate a new account for the ticket
        ticket_account = Keypair()
        
        # Calculate the space needed for ticket data
        TICKET_SPACE = 8 + 8 + 32 + 1  # event_id + price + owner + is_used
        
        # Create transaction instruction
        create_account_ix = create_account(
            from_pubkey=payer.public_key,
            new_account_pubkey=ticket_account.public_key,
            lamports=await self.client.get_minimum_balance_for_rent_exemption(TICKET_SPACE),
            space=TICKET_SPACE,
            program_id=self.program_id
        )
        
        # Create the ticket data
        data = struct.pack("<QQB", event_id, price, 0)  # 0 for is_used
        
        create_ticket_ix = TransactionInstruction(
            keys=[
                {"pubkey": ticket_account.public_key, "is_signer": True, "is_writable": True},
                {"pubkey": payer.public_key, "is_signer": True, "is_writable": True},
            ],
            program_id=self.program_id,
            data=data
        )
        
        transaction = Transaction()
        transaction.add(create_account_ix)
        transaction.add(create_ticket_ix)
        
        # Send and confirm transaction
        result = await self.client.send_transaction(
            transaction,
            payer,
            ticket_account,
        )
        
        return result
    
    async def validate_ticket(self, ticket_account: PublicKey):
        """Validate if a ticket is valid and unused"""
        account_info = await self.client.get_account_info(ticket_account)
        if account_info.value is None:
            return False
            
        data = account_info.value.data
        event_id, price, is_used = struct.unpack("<QQB", data)
        return not bool(is_used)
    
    async def use_ticket(self, payer: Keypair, ticket_account: PublicKey):
        """Mark a ticket as used"""
        instruction = TransactionInstruction(
            keys=[
                {"pubkey": ticket_account, "is_signer": False, "is_writable": True},
                {"pubkey": payer.public_key, "is_signer": True, "is_writable": False},
            ],
            program_id=self.program_id,
            data=bytes([1])  # Instruction to mark ticket as used
        )
        
        transaction = Transaction()
        transaction.add(instruction)
        
        result = await self.client.send_transaction(
            transaction,
            payer,
        )
        
        return result

    async def create_event(self, payer: Keypair, event_name: str, total_tickets: int, price_per_ticket: int):
        """Create a new event"""
        event_account = Keypair()
        
        # Calculate space for event data
        EVENT_SPACE = 8 + 32 + 64 + 8 + 8  # event_id + organizer + name + total_tickets + price
        
        create_account_ix = create_account(
            from_pubkey=payer.public_key,
            new_account_pubkey=event_account.public_key,
            lamports=await self.client.get_minimum_balance_for_rent_exemption(EVENT_SPACE),
            space=EVENT_SPACE,
            program_id=self.program_id
        )
        
        # Pack event data
        event_data = struct.pack(
            "<Q32s64sQQ",
            int(datetime.now().timestamp()),  # event_id
            bytes(payer.public_key),          # organizer
            event_name.encode().ljust(64),    # name
            total_tickets,
            price_per_ticket
        )
        
        create_event_ix = TransactionInstruction(
            keys=[
                {"pubkey": event_account.public_key, "is_signer": True, "is_writable": True},
                {"pubkey": payer.public_key, "is_signer": True, "is_writable": True},
            ],
            program_id=self.program_id,
            data=event_data
        )
        
        transaction = Transaction()
        transaction.add(create_account_ix)
        transaction.add(create_event_ix)
        
        try:
            result = await self.client.send_transaction(
                transaction,
                payer,
                event_account,
            )
            print(f"Event created successfully: {event_account.public_key}")
            return {"success": True, "event_pubkey": event_account.public_key, "result": result}
        except Exception as e:
            print(f"Error creating event: {e}")
            return {"success": False, "error": str(e)}

    async def get_event_info(self, event_pubkey: PublicKey) -> Optional[Dict]:
        """Get information about an event"""
        try:
            account_info = await self.client.get_account_info(event_pubkey)
            if account_info.value is None:
                return None
                
            data = account_info.value.data
            event_id, organizer, name_bytes, total_tickets, price = struct.unpack("<Q32s64sQQ", data)
            
            return {
                "event_id": event_id,
                "organizer": base58.b58encode(organizer).decode(),
                "name": name_bytes.decode().strip('\x00'),
                "total_tickets": total_tickets,
                "price_per_ticket": price,
            }
        except Exception as e:
            print(f"Error getting event info: {e}")
            return None

    async def buy_ticket(self, payer: Keypair, event_pubkey: PublicKey):
        """Buy a ticket for an event"""
        ticket_account = Keypair()
        
        # Get event info to verify price
        event_info = await self.get_event_info(event_pubkey)
        if not event_info:
            raise ValueError("Event not found")
            
        # Create ticket account and purchase instruction
        result = await self.create_ticket(
            payer,
            event_info["event_id"],
            event_info["price_per_ticket"]
        )
        
        return {
            "success": True,
            "ticket_pubkey": ticket_account.public_key,
            "result": result
        } 