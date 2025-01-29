from langchain.tools import BaseTool
import os
from pydantic import BaseModel, Field
from typing import Optional, Type, Union
import json
from web3 import Web3


class ArbitrumTransactionToolInput(BaseModel):
    to_address: str = Field(description="To wallet address | to whom you want to send this eth")
    amount: float = Field(description="How much ether you want to send.")


class ArbitrumTransactionTool(BaseTool):
    
    name: str = "send_arbitrum_eth"
    description: str = """Sends Ethereum to a specified address. Use exact format:
    Input should be a JSON string with keys 'to_address' and 'amount'.
    Example: {"to_address": "0x123...", "amount": 0.001}"""
    args_schema: Type[BaseModel] = ArbitrumTransactionToolInput
    return_direct: bool = True

    def _run(self, **kwargs) -> str:

        to_address = kwargs.get('to_address')
        amount = kwargs.get('amount')

        if not to_address or amount is None:
            return "Error: Missing required parameters"


        try:

            private_key: str = os.environ["WEB3_PRIVATE_KEY"]
            address: str = os.environ["WEB3_WALLET_ADDRESS"]
            infura_project_id: str = os.environ["INFURA_PROJECT_ID"]
            infura_url = "https://arbitrum-sepolia.infura.io/v3/" + infura_project_id

            web3 = Web3(Web3.HTTPProvider(infura_url))

            if not web3.is_connected():
                return "Transaction Error occured"

            nonce = web3.eth.get_transaction_count(address)
            value = web3.to_wei(0.001, "ether")
            gas_price = web3.eth.gas_price
            gas_limit = 32000

            transaction = {
                "nonce": nonce,
                "to": to_address,
                "value": web3.to_wei(amount,"ether"),
                "gas": gas_limit,
                "gasPrice": gas_price,
            }

            signed_tx = web3.eth.account.sign_transaction(transaction, private_key)

            tx_hash = web3.eth.send_raw_transaction(signed_tx.raw_transaction)
            print(web3.to_hex(tx_hash))

            return "Done"
        
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

    os.environ["WEB3_PRIVATE_KEY"] = os.getenv("WEB3_PRIVATE_KEY")
    os.environ["WEB3_WALLET_ADDRESS"] = os.getenv("WEB3_WALLET_ADDRESS")
    os.environ["INFURA_PROJECT_ID"] = os.getenv("INFURA_PROJECT_ID")

    tx_tool = ArbitrumTransactionTool()
    data = tx_tool.invoke({"to_address":"0xDF2b85e90F4Aa7bDC724dE4aF08B45cDc7458593", "amount":0.001})
    print(data)
