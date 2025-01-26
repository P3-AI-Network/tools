import streamlit as st

from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_openai.chat_models import ChatOpenAI
from dotenv import load_dotenv

import os


st.set_page_config(page_title="Conversational Q&A Bot")
st.header("Hey, Let's chat")


load_dotenv()


os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGCHAIN_API_KEY")
os.environ["LANGCHAIN_PROJECT"] = os.getenv("LANGCHAIN_PROJECT")



llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.5)

if "flowmessages" not in st.session_state:
    st.session_state["flowmessages"] = [
        SystemMessage(content="You are a Story writer AI Assistant. create a story on the given prompt")
    ]



def get_openai_response(question):
    st.session_state["flowmessages"].append(HumanMessage(content=question))
    answer = llm(st.session_state['flowmessages'])
    st.session_state["flowmessages"].append(AIMessage(content=answer.content))
    return answer.content



input = st.text_input("Ask me anything")
response = get_openai_response(input)

submit = st.button("Ask the question")

if submit:
    st.subheader("The Response is")
    st.write(response)
