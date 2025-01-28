from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_community.tools.tavily_search import TavilySearchResults
import os
load_dotenv()


os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGCHAIN_API_KEY")
os.environ["LANGCHAIN_PROJECT"] = os.getenv("LANGCHAIN_PROJECT")
os.environ["TAVILY_API_KEY"] = os.getenv("TAVILY_API_KEY")
os.environ["GITHUB_APP_PRIVATE_KEY"] = os.getenv("GITHUB_APP_PRIVATE_KEY")
os.environ["GITHUB_REPOSITORY"] = os.getenv("GITHUB_REPOSITORY")
os.environ["GITHUB_APP_ID"] = os.getenv("GITHUB_APP_ID")


search = TavilySearchResults(max_results=2)
search_results = search.invoke("what is the weather in PUNE")
print(search_results)