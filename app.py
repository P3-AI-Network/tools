import streamlit as st
import os 
from dotenv import load_dotenv


from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain.prompts import PromptTemplate
from langchain.chains.llm import LLMChain
from langchain.chains.sequential import SequentialChain
from langchain.memory import ConversationBufferMemory

load_dotenv()


os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGCHAIN_API_KEY")
os.environ["LANGCHAIN_PROJECT"] = os.getenv("LANGCHAIN_PROJECT")


st.title("Celebrity Search Results")
input_text = st.text_input("Enter the name of Celebrity")


# memory
person_memory = ConversationBufferMemory(input_key='name', memory_key='person_history') 
dob_memory = ConversationBufferMemory(input_key='person', memory_key='dob_history') 
events_memory = ConversationBufferMemory(input_key='dob', memory_key='events_history') 


first_prompt_template = PromptTemplate(
    input_variables=['name'],
    template="Tell me about Celebrity {name} in 1 paragraoh or 100 words max."
)


# Init Openai LLm 
llm = ChatOpenAI(model="gpt-3.5-turbo")


chain = LLMChain(llm=llm, prompt=first_prompt_template, verbose=True, output_key='person', memory=person_memory)


second_prompt_template = PromptTemplate(
    input_variables=['person'],
    template="When was {person} born ? give me only the dd/mm/yyyy format and nothing more than that"
)

chain2 = LLMChain(llm=llm, prompt=second_prompt_template, verbose=True, output_key='dob', memory=dob_memory)


third_prompt_template = PromptTemplate(
    input_variables=['dob'],
    template="Mention 5 major events happend around {dob} in the world"
)

chain3 = LLMChain(llm=llm, prompt=third_prompt_template, verbose=True, output_key='events', memory=events_memory)

parent_chain = SequentialChain(chains=[chain, chain2, chain3], verbose=True, input_variables=['name'], output_variables=['person','dob', 'events'])


if input_text:
    st.write(parent_chain({'name': input_text}))


    with st.expander("Person Memory"):
        st.info(person_memory.buffer)


    with st.expander("DOB Memory"):
        st.info(dob_memory.buffer)  

    with st.expander("Events Memory"):
        st.info(events_memory.buffer)

