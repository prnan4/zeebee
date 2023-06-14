import streamlit as st
from streamlit_chat import message

from langchain.chat_models import ChatOpenAI
from langchain.schema import (
    SystemMessage,
    HumanMessage,
    AIMessage
)

# setup streamlit page
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

secrets = st.secrets["secrets"]
openai_api_key = secrets["openai_api_key"]

chat = ChatOpenAI(temperature=0, openai_api_key=openai_api_key)

# initialize message history
if "messages" not in st.session_state:
    st.session_state.messages = [
        SystemMessage(content="You are a helpful assistant.")
    ]


# sidebar with user input
with st.sidebar:
    user_input = st.text_input("Your question: ", key="user_input")

    # handle user input
    if user_input:
        st.session_state.messages.append(HumanMessage(content=user_input))
        with st.spinner("Thinking..."):
            response = chat(st.session_state.messages)
        st.session_state.messages.append(AIMessage(content=response.content))


# display message history
messages = st.session_state.get('messages', [])
for i, msg in enumerate(messages[1:]):
    if i % 2 == 0:
        message(msg.content, is_user=True, key=str(i) + '_user')
    else:
        message(msg.content, is_user=False, key=str(i) + '_ai')

with st.form('my_form'):
    context_type = st.selectbox('Rate the response', ['Excellent', 'Good', 'Poor'])
    feedback = st.text_input('More Comments', '')
    
    # Feedback is displayed in app. Need to modify logic to store feedback to databaset
    feedback_submitted = st.form_submit_button('Submit Feedback')

    if feedback_submitted:
      st.subheader('Feedback:')
      st.write(feedback)