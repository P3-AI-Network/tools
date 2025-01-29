import os
import json
import base58
import struct 
import hashlib

from langchain.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Optional, Type, Union

from solana.rpc.api import Client
from solana.rpc.commitment import Commitment

from solders.instruction import Instruction, AccountMeta
from solders.pubkey import Pubkey
from solders.transaction import Transaction
from solders.message import Message
from solders.keypair import Keypair


GLOBAL = Pubkey.from_string("4wTV1YmiEkRvAtNtsSGPtUrqRYQMe5SKy2uB4Jjaxnjf")
SYSTEM_PROGRAM = Pubkey.from_string("11111111111111111111111111111111")
RENT = Pubkey.from_string("SysvarRent111111111111111111111111111111111")
PUMP_FUN_PROGRAM = Pubkey.from_string("6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P")
PUMP_FUN_ACCOUNT = Pubkey.from_string("Ce6TQqeHC9p8KetsN6JsjHK7UTZk7nasjjnr7XxXp9F1")
MPL_TOKEN_METADATA = Pubkey.from_string("metaqbxxUerdq28cj1RbAWkYQm3ybzjb6a8bt518x1s")
MINT_AUTHORITY = Pubkey.from_string("TSLvdd1pWpHVjahSpsvCXUbgwsL3JAcvokwaKt1eokM")
COMPUTE_BUDGET_PROGRAM_ID = Pubkey.from_string("ComputeBudget111111111111111111111111111111")
TOKEN_PROGRAM_ID = Pubkey.from_string("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA")
ASSOCIATED_TOKEN_PROGRAM_ID = Pubkey.from_string("ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL")


def buffer_from_string(value: str) -> bytes:
    return len(value).to_bytes(4, 'little') + value.encode()



class PumpFunToolInput(BaseModel):
    name: str = Field(description="Token name eg: TONfortcoin")
    symbol: str = Field(description="Token Symbol in letters eg: TN, BTX, PJT, WIFFTX")
    uri: str = Field(description="Token website url or uri eg: https://tonfortcoin.com")


class PumpFunTool(BaseTool):
    
    name: str = "pump_fun_create_token"
    description: str = """Create Token on Pump fun platform on solana"""
    args_schema: Type[BaseModel] = PumpFunToolInput
    return_direct: bool = False

    def load_secret_key(self) -> Keypair:

        with open("secret_key.json", "r") as f:
            secret_key = json.load(f)
        
        secret_key_bytes = bytes(secret_key)
        keypair = Keypair.from_bytes(secret_key_bytes)

        return keypair


    def _run(self, **kwargs) -> str:

        try:

            token_name = kwargs.get("name")
            token_symbol = kwargs.get("symbol")
            token_uri = kwargs.get("uri")

            mint_keypair = Keypair()
            print(f"Mint Address: {mint_keypair.pubkey().__str__()}")

            client = Client("https://api.mainnet-beta.solana.com")
            user_account_keypair = self.load_secret_key()

            bonding_curve, _ = Pubkey.find_program_address(
                [b"bonding-curve", bytes(mint_keypair.pubkey())],
                PUMP_FUN_PROGRAM
            )


            associated_bonding_curve, _ = Pubkey.find_program_address(
                [
                    bytes(bonding_curve),
                    bytes(TOKEN_PROGRAM_ID),
                    bytes(mint_keypair.pubkey())
                ],
                ASSOCIATED_TOKEN_PROGRAM_ID
            )

            metadata, _ = Pubkey.find_program_address(
                [
                    b"metadata",
                    bytes(MPL_TOKEN_METADATA),
                    bytes(mint_keypair.pubkey())
                ],
                MPL_TOKEN_METADATA
            )

            compute_budget_instruction = Instruction(
                program_id=COMPUTE_BUDGET_PROGRAM_ID,
                accounts=[],
                data=bytes([3]) + (100000).to_bytes(8, 'little')
            )

            instruction_data = (
                bytes.fromhex("181ec828051c0777") +
                buffer_from_string(token_name) +
                buffer_from_string(token_symbol) +
                buffer_from_string(token_uri)
            )

            # Create accounts list
            accounts = [
                AccountMeta(mint_keypair.pubkey(), True, True),
                AccountMeta(MINT_AUTHORITY, False, False),
                AccountMeta(bonding_curve, False, True),
                AccountMeta(associated_bonding_curve, False, True),
                AccountMeta(GLOBAL, False, False),
                AccountMeta(MPL_TOKEN_METADATA, False, False),
                AccountMeta(metadata, False, True),
                AccountMeta(user_account_keypair.pubkey(), True, True),
                AccountMeta(SYSTEM_PROGRAM, False, False),
                AccountMeta(TOKEN_PROGRAM_ID, False, False),
                AccountMeta(ASSOCIATED_TOKEN_PROGRAM_ID, False, False),
                AccountMeta(RENT, False, False),
                AccountMeta(PUMP_FUN_ACCOUNT, False, False),
                AccountMeta(PUMP_FUN_PROGRAM, False, False)
            ]



            instruction = Instruction(
                program_id=PUMP_FUN_PROGRAM,
                accounts=accounts,
                data=instruction_data
            )

            recent_blockhash = client.get_latest_blockhash("finalized").value.blockhash


            message = Message.new_with_blockhash(
                [compute_budget_instruction,instruction],
                user_account_keypair.pubkey(),
                recent_blockhash
            )

            transaction = Transaction.new_unsigned(message)
            transaction.sign([user_account_keypair, mint_keypair], recent_blockhash=recent_blockhash)



            result = client.send_transaction(transaction)
            return f"Token created with address {mint_keypair.pubkey().__str__()} give this address back to user in return prompt"

        
        except Exception as e:
            print("Error occured in transaction: ", e)
            return "Transaction Error occured"


    def _parse_input(self, tool_input: Union[str, dict], tool_call_id: Optional[str] = None) -> dict:
        """Parse the tool input."""
        if isinstance(tool_input, str):
            try:
                parsed_input = json.loads(tool_input)
                return parsed_input
            except json.JSONDecodeError:
                return {"to_address": tool_input}
        return tool_input



if __name__ == "__main__":

    from dotenv import load_dotenv
        
    load_dotenv()

    tool = PumpFunTool()
    tool.invoke({
        "name":"hel",
        "symbol": "JJasflkjdfas",
        "uri": "https://google.com"
    })
