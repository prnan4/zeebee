import streamlit as st
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
import toml

import requests
import configparser
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
             
# Read values from secrets.toml
secrets = toml.load("secrets.toml")
openai_api_key = secrets['secrets']['openai_api_key']

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

def scrape_text_from_url(url):
    # Send a GET request to the URL
    response = requests.get(url)

    # Parse the HTML content
    soup = BeautifulSoup(response.content, "html.parser")
    def tag_visible(element):
        if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]']:
            return False
        if isinstance(element, Comment):
            return False
        return True

    # Extract visible text from the HTML
    visible_texts = soup.findAll(text=True)
    visible_texts = filter(tag_visible, visible_texts)
    content_text = u" ".join(t.strip() for t in visible_texts)

    # Remove special characters
    content_text = re.sub(r"[^\w\s]", "", content_text)

    # Remove additional spaces
    content_text = re.sub(r"\s+", " ", content_text)
    return content_text

# Generate a response with context from URL using the language model
def generate_response_with_context_from_URL(question, url):

    url_text = scrape_text_from_url(url)

    prompt = PromptTemplate(
    input_variables=["context", "question"],
    template="{context}\n\n{question}"
    )

    # Format the prompt with the context and question
    formatted_prompt = prompt.format(context=url_text, question=question)
    st.info(llm(formatted_prompt))

# Render the input form
with st.form('my_form'):
    text = st.text_area('Enter question:', 'What are the key features and capabilities of the Zuora subscription management platform?')
    context_type = st.selectbox('Options', ['Standard', 'Zuora Context added', 'Provide URL for context'])
    url = st.text_input('Enter URL:', '(Not required for Standard/ Zuora Context added options)')
    submitted = st.form_submit_button('Submit')

    if submitted and openai_api_key.startswith('sk-'):
        if context_type == 'Standard':
            generate_response(text)
        elif context_type == 'Zuora Context added':
            generate_response_with_context(text)
        elif context_type == 'Provide URL for context':
            generate_response_with_context_from_URL(text, url)

    context_type = st.selectbox('Rate the response', ['Excellent', 'Good', 'Poor'])
    feedback = st.text_input('More Comments', '')
    
    # Feedback is displayed in app
    feedback_submitted = st.form_submit_button('Submit Feedback')

    if feedback_submitted:
      st.subheader('Feedback:')
      st.write(feedback)