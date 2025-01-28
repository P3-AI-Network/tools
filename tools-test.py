import os

from langchain_openai import ChatOpenAI
from langchain.agents import create_react_agent, AgentExecutor
from langchain.prompts import PromptTemplate
from tools import ArbitrumTransactionTool
from dotenv import load_dotenv

load_dotenv()


os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGCHAIN_API_KEY")
os.environ["LANGCHAIN_PROJECT"] = os.getenv("LANGCHAIN_PROJECT")
os.environ["COIN_MARKET_CAP_API"] = os.getenv("COIN_MARKET_CAP_API")
os.environ["WEB3_PRIVATE_KEY"] = os.getenv("WEB3_PRIVATE_KEY")
os.environ["WEB3_WALLET_ADDRESS"] = os.getenv("WEB3_WALLET_ADDRESS")
os.environ["INFURA_PROJECT_ID"] = os.getenv("INFURA_PROJECT_ID")


llm = ChatOpenAI(model="gpt-3.5-turbo")
tools = [ArbitrumTransactionTool()]

prompt = PromptTemplate.from_template("""
    Answer the following questions as best you can. You have access to the following tools:

{tools}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}] / if the question is not related to any of the tools then just answer the question without using the tools
Action Input: the input to the action should be a json string with only the required parameters
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Begin!

Question: {input}
{agent_scratchpad}
""")

agent = create_react_agent(tools=tools, llm=llm, prompt=prompt)
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,
    max_iterations=3,
    handle_parsing_errors=True,  # Add this line
)

query = "Can you send 0.001 ETH to 0xDF2b85e90F4Aa7bDC724dE4aF08B45cDc7458593"
# query = "Hey how are you, write a short story"
response = agent_executor.invoke({"input": query})

print(response)