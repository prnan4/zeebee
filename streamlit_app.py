import streamlit as st
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
import toml

import requests
from bs4 import BeautifulSoup
from bs4.element import Comment
import re

# Set up the Streamlit app title and introductory message
st.title('🐝 Zeebee')

st.subheader('''
🤖 Welcome to Zuora's Product Catalogue Chatbot! 🚀

I'm here to assist you in exploring our wide range of subscription management products. Whether you're looking for billing solutions or subscription analytics, I've got you covered.

Simply type your questions or preferences, and I'll provide you with information on how our products can help streamline your subscription-based business.

Let's get started! How can I assist you today? 😊
''')
             
secrets = st.secrets["secrets"]
openai_api_key = secrets["openai_api_key"]

# Initialize the OpenAI language model
llm = OpenAI(temperature=0.5, openai_api_key=openai_api_key)

# Generate a response using the language model
def generate_response(question):
    st.info(llm(question))

# Generate a response with context using the language model
def generate_response_with_context(question):
    prompt = PromptTemplate(
        input_variables=["context", "question"],
        template="{context}\n\n{question}"
    )
    # Read the context from a file
    with open('zuora_context.txt', 'r') as file:
        context = file.read()

    # Format the prompt with the context and question
    formatted_prompt = prompt.format(context=context, question=question)
    st.info(llm(formatted_prompt))

# Render the input form
with st.form('my_form'):
    text = st.text_area('Enter question:', 'What are the key features and capabilities of the Zuora subscription management platform?')
    context_type = st.selectbox('Options', ['Standard', 'Zuora Context added'])
    submitted = st.form_submit_button('Submit')

    if submitted and openai_api_key.startswith('sk-'):
        if context_type == 'Standard':
            generate_response(text)
        elif context_type == 'Zuora Context added':
            generate_response_with_context(text)

    context_type = st.selectbox('Rate the response', ['Excellent', 'Good', 'Poor'])
    feedback = st.text_input('More Comments', '')
    
    # Feedback is displayed in app
    feedback_submitted = st.form_submit_button('Submit Feedback')

    if feedback_submitted:
      st.subheader('Feedback:')
      st.write(feedback)