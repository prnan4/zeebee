import streamlit as st
from streamlit_chat import message

from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.text_splitter import CharacterTextSplitter
from langchain.llms import OpenAI
from langchain.chains import ConversationalRetrievalChain

from langchain.document_loaders import TextLoader

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
         
# Upload Context Txt file in sidebar
uploaded_file = st.sidebar.file_uploader("upload", type="text")

# Vectorising custom knowledge

loader = TextLoader("zuora_context.txt")
documents = loader.load()

text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
documents = text_splitter.split_documents(documents)

embeddings = OpenAIEmbeddings(openai_api_key = openai_api_key)
# vectorstore = Chroma.from_documents(documents, embeddings)
vectorstore = FAISS.from_documents(documents, embeddings)

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


with st.form('response_form'):
    context_type = st.selectbox('Rate the response', ['Excellent', 'Good', 'Poor'])
    feedback = st.text_input('More Comments', '')
    
    # Feedback is displayed in app. Need to modify logic to store feedback to databaset
    feedback_submitted = st.form_submit_button('Submit Feedback')

    if feedback_submitted:
      st.subheader('Feedback:')
      st.write(feedback)