import streamlit as st
from utils.model_schema import Role, Message
from utils.prompt_manager import build_system_settings
import asyncio
import os

st.set_page_config(
    page_title="NexAI English Tutor - TOEFL Reading", page_icon=":books:", layout="wide"
)

st.title("NexAI English Tutor - TOEFL Reading")
st.markdown("### Ask your questions about TOEFL Reading exercises!")

# --- Load Transformer Model ---

if "transformer" not in st.session_state:
    st.session_state.transformer = None

if "history" not in st.session_state:
    st.session_state.history = []

if "exercise_context" not in st.session_state:
    st.session_state.exercise_context = ""

st.session_state.exercise_context = "TOEFL Reading"

from utils.func_tools import load_transformers, chatgpt_completion, find_embedding_candidates

async def initialize_transformer():
    st.session_state.transformer = load_transformers(
        model_name="all-MiniLM-L6-v2", cache_folder="models_cache"
    )

def get_response(query):
    completion_response = chatgpt_completion(
        st.session_state.exercise_context, query, st.session_state.history
    )
    response = ""
    for chunk in completion_response:
        content = chunk.choices[0].delta.content
        if content is not None:
            response += content
    st.session_state.history.append({"role": "assistant", "content": response})
    return response

if st.session_state.transformer is None:
    asyncio.run(initialize_transformer())

# --- Display Chat History and Response ---

if st.session_state.exercise_context:
    # Display previous interactions
    for message in st.session_state.history:
        if message["role"] == "user":
            st.write(f"**Vous:** {message['content']}")
        else:
            st.write(f"**NexAI Tutor:** {message['content']}")

    # User Input
    user_query = st.chat_input(
        f"Ask your question about {st.session_state.exercise_context} exercises:"
    )
    if user_query:
        st.session_state.history.append({"role": "user", "content": user_query})
        st.write(f"**Vous:** {user_query}")
        with st.spinner(text="..."):
            response = get_response(user_query)
            st.write(f"**NexAI Tutor:** {response}")

# --- Navigate to Other Pages ---

st.button("Go back to Main Page", on_click=lambda: st.session_state.exercise_context, args=(""))