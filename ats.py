import streamlit as st 
from pypdf import PdfReader
import io

from langchain_openai.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains.llm import LLMChain

st.title("Welcome to the ATS")


# Create a Input text field to upload job description
job_description = st.text_area("Enter the Job description")


# Create a PDF upload Button for resume upload 
pdf = st.file_uploader("Upload Resunme", type="pdf")


# Create a Button to Give feedback on the resume 
feedback_button = st.button("Give Feedback")

# Create a Button to get percentage match of resume to job description 
percentage_button = st.button("Get Match Percentage")

feedback_prompt = PromptTemplate(
    input_variables=['job_description','resume'],
    template="""
        You are a HR manager and you have knoweledge about all the technical domains, you have given a 
        Job description give a feedback to the user on how he can align their resume to the job description 
        any mistake they did or anything they missed out in the resume.

        Job Description: {job_description}

        Resume: {resume}
    """
)

percentage_prompt = PromptTemplate(
    input_variables=['job_description','resume'],
    template="""
        You are a HR manager and you have knoweledge about all the technical domains, you have given a 
        Job description give a percentage to the users resume and i want the response to be in % and nothing more.
        Just giive only percentage eg: 100% or 50% or 26%

        Job Description: {job_description}

        Resume: {resume}
    """
)

llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.2)
chain = LLMChain(llm=llm,prompt=feedback_prompt)
chain2 = LLMChain(llm=llm,prompt=percentage_prompt)


pdf_bytes = io.BytesIO(pdf.read())
pdf_reader = PdfReader(pdf_bytes)

pdf_text = ""

for page in pdf_reader.pages:
    pdf_text += page.extract_text()

if feedback_button:
    result = chain.run(job_description=job_description,resume=pdf_text)
    st.write(result)



if percentage_button:
    result = chain2.run(job_description=job_description,resume=pdf_text)
    st.write(result)


