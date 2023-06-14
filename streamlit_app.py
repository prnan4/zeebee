import streamlit as st
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
import toml

import requests
from bs4 import BeautifulSoup
from bs4.element import Comment
import re

st.title('🐝 Zeebee')

st.subheader('''
🤖 Welcome to Zuora's Product Catalogue Chatbot! 🚀

I'm here to assist you in exploring our wide range of subscription management products. Whether you're looking for billing solutions or subscription analytics, I've got you covered.

Simply type your questions or preferences, and I'll provide you with information on how our products can help streamline your subscription-based business.

Let's get started! How can I assist you today? 😊
''')
             
#openai_api_key = st.sidebar.text_input('OpenAI API Key')

secrets = st.secrets["secrets"]
openai_api_key = secrets["openai_api_key"]

def generate_response(question):
    llm = OpenAI(temperature=0.5, openai_api_key=openai_api_key)
    st.info(llm(question))

def generate_response_with_context(question):
    llm = OpenAI(temperature=0.5, openai_api_key=openai_api_key)
    prompt = PromptTemplate(
        input_variables=["context", "question"],
        template="{context}\n\n{question}"
    )

    context = '''Create a custom object as the lookup table
    To create a custom object through the Zuora UI, complete the following steps:

    In the left-hand navigation section, navigate to Platform > Custom Objects.
    Click + CREATE CUSTOM OBJECT.
    On the Custom Objects page that is displayed, configure the lookup table definition: 
    In the NAME field, enter the UI element name for the new custom object. In this scenario, enter CarRental.
    In the API NAME field, enter an API label name for the custom object. In this scenario, enter CarRental.
    The API label name will be used later, so note it for reference.
    In the Custom Fields area, click + NEW CUSTOM FIELD.
    In the Custom Field dialog that is displayed, complete the following configurations:
    In the custom fields overview area, enter the UI element name for the new custom field in the NAME field. In this scenario, enter type.
    The value in the API NAME field is automatically populated based on the specified field name. In this scenario, type__c is automatically displayed. The API Name of the field will also be used later.
    In the Details area, select Text from the FIELD TYPE list.
    Switch the Filterable toggle on to ensure that the custom field is filterable.
    It is best practice to also switch the Required on if you need to use the custom field in the price formula later. 
    Click SAVE to save the custom field configurations.
    Repeat steps 4 and 5 to create the state and multiplier custom fields.
    When creating the multiplier custom field, you have to select Number from the FIELD TYPE list.
    Click SAVE to save the custom object configurations.
    The definition of the lookup table called CarRental is now created, with the type, state, and multiplier fields.'''

    # Format the prompt with the context and question
    formatted_prompt = prompt.format(context=context, question=question)
    st.info(llm(formatted_prompt))

with st.form('my_form'):
    text = st.text_area('Enter question:', 'What are the key features and capabilities of the Zuora subscription management platform?')
    context_type = st.selectbox('Options', ['Standard', 'Zuora Context added'])
    submitted = st.form_submit_button('Submit')

    #   if not openai_api_key.startswith('sk-'):
    #     st.warning('Please enter your OpenAI API key!', icon='⚠')

    if submitted and openai_api_key.startswith('sk-'):
        if context_type == 'Standard':
            generate_response(text)
        elif context_type == 'Zuora Context added':
            generate_response_with_context(text)

    context_type = st.selectbox('Rate the response', ['Excellent', 'Good', 'Poor'])
    feedback = st.text_input('More Comments', '')
    
    # Feedback is displayed in app. Need to modify logic to store feedback to databaset
    feedback_submitted = st.form_submit_button('Submit Feedback')

    if feedback_submitted:
      st.subheader('Feedback:')
      st.write(feedback)