from langchain.tools import BaseTool
import requests
import os
from pydantic import BaseModel, Field
from typing import Optional, Type, Union
from bs4 import BeautifulSoup
import json


class CryptoPriceToolInput(BaseModel):
    symbol: str = Field(description="Symbol of the requred crytocurrency, eg: Bitcoin = BTC, Ethereum= ETH, Binance Coin = BNB, Tether = USDT, Solana = SOL")

class CryptoPriceTool(BaseTool):

    name: str = "get_crypto_price"
    description: str = "Fetches the current USD price of a cryptocurrency by its symbol from Coinmarketcap"   
    args_schema: Type[BaseModel] = CryptoPriceToolInput
    return_direct: bool = False

    def _run(self, *args, **kwargs) -> int:

        symbol: str = kwargs.get('symbol')
        if not symbol:
            return -2

        base_url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest"
        headers = {
            "X-CMC_PRO_API_KEY": os.environ["COIN_MARKET_CAP_API"],
        }
        params = {
            "symbol": symbol,
            "convert": "USD"
        }
        

        try: 
            response = requests.get(url=base_url, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()

            return data


        except Exception as e:
            print(e) 
            return -1


    async def _arun(self, symbol: str) -> str:
        """Async version of the price fetcher (optional)."""
        raise NotImplementedError("Async support is not implemented for this tool.")
    
    def _parse_input(self, tool_input: Union[str, dict], tool_call_id: Optional[str] = None) -> dict:
        """Parse the tool input."""
        if isinstance(tool_input, str):
            try:
                parsed_input = json.loads(tool_input)
                return parsed_input
            except json.JSONDecodeError:
                return {"symbol": tool_input}
        return tool_input
    



class CryptoLatestNewsToolInput(BaseModel):
    pass

class CryptoLatestNewsTool(BaseTool):

    name: str = "get_latest_crypto_news_content"
    description: str = "Fetch Latest articles and news in crypto industry"


    def _run(self, **kwargs) -> str: 

        # Fetch latest artiels from coin market cap 
        base_url = "https://pro-api.coinmarketcap.com/v1/content/latest"
        headers = {
            "X-CMC_PRO_API_KEY": os.environ["COIN_MARKET_CAP_API"],
        }

        try: 
            response = requests.get(url=base_url, headers=headers)
            response.raise_for_status()
            data = response.json()
            print(data)
            cleaned_data = []


            for content in data["data"]:

                content_data = {
                    "title": "", 
                    "subtitle": "",
                    "type": "",
                    "source_name": "",
                    "source_content": ""
                }


                content_data["title"] = content["title"]
                content_data["subtitle"] = content["subtitle"]
                content_data["source_name"] = content["source_name"]
                content_data["title"] = content["title"]

                page_resp = requests.get(content["source_url"])
                
                if page_resp.status_code != 200: 
                    continue


                soup = BeautifulSoup(page_resp.text, "html.parser")
                page_content = soup.get_text(separator="\n").strip()
                content_data["source_content"] = page_content
                print(content_data)
                cleaned_data.append(content_data)

            return str(cleaned_data)

        except Exception as e:
            print(e)
            return "API Error Occured"



if __name__ == "__main__":

    from dotenv import load_dotenv
    from bs4 import BeautifulSoup
        
    load_dotenv()

    os.environ["COIN_MARKET_CAP_API"] = os.getenv("COIN_MARKET_CAP_API")

    crypto_symbol = CryptoPriceTool()
    crypto_symbol.run("BTC")

    crypto_news = CryptoLatestNewsTool()
    data = crypto_news.run("")    
    print(data)