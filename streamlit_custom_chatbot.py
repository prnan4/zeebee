import streamlit as st
from streamlit_chat import message

from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.text_splitter import CharacterTextSplitter
from langchain.llms import OpenAI
from langchain.chains import ConversationalRetrievalChain

from langchain.document_loaders import PyPDFLoader
from langchain.document_loaders import TextLoader

from langchain.document_loaders import TextLoader
from langchain.document_loaders import DirectoryLoader

import tempfile
import os

import requests
from bs4 import BeautifulSoup
from bs4.element import Comment
import re

# Clear the Session State
if 'key_to_remove' in st.session_state:
    del st.session_state['key_to_remove']

#Define openai-api-key
# Read values from secrets.toml
secrets = st.secrets["secrets"]
openai_api_key = secrets["openai_api_key"]

# Set up the Streamlit app title and introductory message
st.set_page_config(
    page_title="Zeebee",
    page_icon="🐝"
)

st.title('🐝 Zeebee')

st.write('''
I'm here to assist you in exploring our wide range of subscription management products. Whether you're looking for billing solutions or subscription analytics, I've got you covered.

Simply type your questions or preferences, and I'll provide you with information on how our products can help streamline your subscription-based business.

Let's get started! How can I assist you today? 😊
''')

loader = TextLoader("zuora_context.txt")
# loader = DirectoryLoader('zuora_context/', loader_cls=TextLoader)
data = loader.load()

text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
data = text_splitter.split_documents(data)
        
# Defining OpenAI embeddings
embeddings = OpenAIEmbeddings(openai_api_key = openai_api_key)
vectorstore = FAISS.from_documents(data, embeddings)

# Creating conversational retrieval chain 
qa = ConversationalRetrievalChain.from_llm(OpenAI(temperature=0, openai_api_key = openai_api_key), vectorstore.as_retriever())

def conversational_chat(query):
    
    result = qa({"question": query, 
    "chat_history": st.session_state['history']})
    st.session_state['history'].append((query, result["answer"]))
    
    return result["answer"]

if 'generated' not in st.session_state:
    st.session_state['generated'] = ["Hello! Ask me anything about product catalogue of Zuora" + " 🤗"]

if 'history' not in st.session_state:
    st.session_state['history'] = []

if 'past' not in st.session_state:
    st.session_state['past'] = ["Hey ! 👋"]
    
#container for the chat history
response_container = st.container()
#container for the user's text input
container = st.container()

with container:
    user_input = st.text_input("Your question: ", key="user_input")
        
    if user_input:
        output = conversational_chat(user_input)
        
        st.session_state['past'].append(user_input)
        st.session_state['generated'].append(output)
        

if st.session_state['generated']:
    with response_container:
        for i in range(len(st.session_state['generated'])):
            message(st.session_state["past"][i], is_user=True, key=str(i) + '_user')
            message(st.session_state["generated"][i], key=str(i))
