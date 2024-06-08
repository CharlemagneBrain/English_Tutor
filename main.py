import streamlit as st
import numpy as np
import asyncio
from utils.model_schema import Role, Message
from utils.func_tools import chatgpt_completion, find_embedding_candidates, load_transformers
from streamlit_chat import message

st.set_page_config(page_title="NexAI English Tutor", page_icon=":books:", layout="wide")

st.title("NexAI English Tutor Chat")
st.markdown("### Welcome to your English Tutor! 👋📚")

openai_api_key = st.sidebar.text_input("OpenAI API Key", type="password")

if 'transformer' not in st.session_state:
    st.session_state.transformer = None
if 'history' not in st.session_state: 
    st.session_state.history = []

async def initialize_transformer():
    st.session_state.transformer = load_transformers(model_name="all-MiniLM-L6-v2", cache_folder="models_cache")

def get_response(query):
    query_embedding = st.session_state.transformer.encode(query)
    paragraphes = find_embedding_candidates(query_embedding=query_embedding, top_k=7)
    context = "\n\n".join(paragraphes)
    completion_response = chatgpt_completion(context, query, st.session_state.history, api_key=openai_api_key)
    
    response = ""
    for chunk in completion_response:
        content = chunk.choices[0].delta.content
        if content is not None:
            response += content
    
    st.session_state.history.append({"role": "assistant", "content": response})
        
    return response

if st.session_state.transformer is None:
    asyncio.run(initialize_transformer())

for message in st.session_state.history:
    if message["role"] == "user":
        st.write(f"**Vous:** {message['content']}")
    else:
        st.write(f"**NexAI Tutor:** {message['content']}")
        
user_query = st.chat_input("Discutez !")

if user_query:
    st.session_state.history.append({"role": "user", "content": user_query})
    st.write(f"**Vous:** {user_query}")
    with st.spinner(text="Patientez un instant"):
        response = get_response(user_query)
        st.write(f"**NexAI Tutor:** {response}")
else:
    st.write("Hello !")