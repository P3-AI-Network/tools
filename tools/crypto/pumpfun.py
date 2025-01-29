from langchain.tools import BaseTool
import os
from pydantic import BaseModel, Field
from typing import Optional, Type, Union
import json
from solana.rpc.api import Client
from solders.instruction import Instruction, AccountMeta
from solders.pubkey import Pubkey
from solders.transaction import Transaction
from solders.message import Message
from solders.keypair import Keypair


class PumpFunTool(BaseTool):
    
    name: str = "pump_fun_create_token"
    description: str = """Create Token on Pump fun platform on solana"""
    # args_schema: Type[BaseModel] = ArbitrumTransactionToolInput
    # return_direct: bool = True

    def load_secret_key(self) -> Keypair:

        with open("secret_key.json", "r") as f:
            secret_key = json.load(f)
        
        secret_key_bytes = bytes(secret_key)
        keypair = Keypair.from_bytes(secret_key_bytes)

        return keypair


    def _run(self, **kwargs) -> str:


        try:

            private_key: str = os.environ["WEB3_PRIVATE_KEY"]
            address: str = os.environ["WEB3_WALLET_ADDRESS"]
            infura_project_id: str = os.environ["INFURA_PROJECT_ID"]
            infura_url = "https://arbitrum-sepolia.infura.io/v3/" + infura_project_id

            client = Client("https://api.mainnet-beta.solana.com")
            keypair = self.load_secret_key()

            account_metas = [
                AccountMeta(
                    pubkey=keypair.pubkey().__str__(),
                    is_signer=True,
                    is_writable=False
                )
            ]


            recent_blockhash = client.get_latest_blockhash().value.blockhash
            message = Message.new_with_blockhash(
                [],
                keypair.pubkey().__str__(),

            )

        
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
    from bs4 import BeautifulSoup
        
    load_dotenv()

    os.environ["COIN_MARKET_CAP_API"] = os.getenv("COIN_MARKET_CAP_API")
    os.environ["WEB3_PRIVATE_KEY"] = os.getenv("WEB3_PRIVATE_KEY")
    os.environ["WEB3_WALLET_ADDRESS"] = os.getenv("WEB3_WALLET_ADDRESS")
    os.environ["INFURA_PROJECT_ID"] = os.getenv("INFURA_PROJECT_ID")

