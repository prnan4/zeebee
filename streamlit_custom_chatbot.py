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

option = st.sidebar.selectbox("Choose Option for context:", ("Upload a PDF/txt file", "Enter URL"))     

uploaded_file = None
url = None

if option == "Enter URL":
    # Get context from URL
    url = st.sidebar.text_input('Enter URL:')
else:
    # Upload Context Txt file in sidebar
    uploaded_file = st.sidebar.file_uploader("Upload your context file", type=["txt", "pdf"])

text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)

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
    visible_texts = soup.findAll(string=True)
    visible_texts = filter(tag_visible, visible_texts)
    content_text = u" ".join(t.strip() for t in visible_texts)

    # Remove special characters
    content_text = re.sub(r"[^\w\s]", "", content_text)

    # Remove additional spaces
    content_text = re.sub(r"\s+", " ", content_text)
    return content_text

if uploaded_file or url:
    if uploaded_file:
        with tempfile.NamedTemporaryFile(mode="wb", delete=False) as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            tmp_file_path = tmp_file.name

        file_extension =  os.path.splitext(uploaded_file.name)[1].lower()  

        if file_extension == ".pdf":
            loader = PyPDFLoader(file_path=tmp_file_path)  
            data = loader.load_and_split(text_splitter)
        
        elif file_extension == ".txt":
            loader = TextLoader(file_path=tmp_file_path, encoding="utf-8")
            data = loader.load_and_split(text_splitter)

    if url: 
        with open(f"temp.txt", "w") as file:
            file.write(scrape_text_from_url(url))
        loader = TextLoader("temp.txt")
        data = loader.load()
        documents = text_splitter.split_documents(data)
        
    # Defining OpenAI embeddings
    embeddings = OpenAIEmbeddings(openai_api_key = openai_api_key)

    # vectorstore = Chroma.from_documents(documents, embeddings)
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
        with st.form(key='my_form', clear_on_submit=True):
            user_input = st.text_input("Query:", placeholder="Enter your question here", key='input')
            submit_button = st.form_submit_button(label='Enter')
            
        if submit_button and user_input:
            output = conversational_chat(user_input)
            
            st.session_state['past'].append(user_input)
            st.session_state['generated'].append(output)

    if st.session_state['generated']:
        with response_container:
            for i in range(len(st.session_state['generated'])):
                message(st.session_state["past"][i], is_user=True, key=str(i) + '_user')
                message(st.session_state["generated"][i], key=str(i))
