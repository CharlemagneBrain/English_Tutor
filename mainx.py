import streamlit as st
from utils.func_tools import load_transformers
from utils.model_schema import Role, Message
from utils.prompt_manager import build_system_settings
import asyncio
import os


st.set_page_config(
    page_title="NexAI English Tutor", page_icon=":books:", layout="wide"
)

st.title("NexAI English Tutor Chat")
st.markdown("### Welcome to your English Tutor! 👋📚")

# --- Sidebar ---
with st.sidebar:
    st.header("Choose your exercise:")
    exercise_type = st.radio(
        "Select an exercise type:",
        ("TOEFL Reading", "Cambridge English Reading", "TOEFL Writing", "Cambridge English Writing"),
    )

    if exercise_type == "TOEFL Reading":
        st.write("TOEFL Reading exercises focus on academic passages.")
    elif exercise_type == "Cambridge English Reading":
        st.write(
            "Cambridge English Reading exercises cover various reading styles and skills."
        )
    elif exercise_type == "TOEFL Writing":
        st.write("TOEFL Writing exercises test your academic writing skills.")
    elif exercise_type == "Cambridge English Writing":
        st.write("Cambridge English Writing exercises assess your formal and creative writing.")

# --- Main Content ---

if "transformer" not in st.session_state:
    st.session_state.transformer = None

if "history" not in st.session_state:
    st.session_state.history = []

if "exercise_context" not in st.session_state:
    st.session_state.exercise_context = ""

if "exercise_type" not in st.session_state:
    st.session_state.exercise_type = ""

st.session_state.exercise_type = exercise_type


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

if st.session_state.exercise_context:
    # Display previous interactions
    for message in st.session_state.history:
        if message["role"] == "user":
            st.write(f"**Vous:** {message['content']}")
        else:
            st.write(f"**NexAI Tutor:** {message['content']}")

    # User Input
    user_query = st.chat_input(
        f"Ask your question about {st.session_state.exercise_type} exercises:"
    )
    if user_query:
        st.session_state.history.append({"role": "user", "content": user_query})
        st.write(f"**Vous:** {user_query}")
        with st.spinner(text="..."):
            response = get_response(user_query)
            st.write(f"**NexAI Tutor:** {response}")

# --- Navigation to Specific Pages ---

st.button("Go to TOEFL Reading", on_click=lambda: st.session_state.exercise_context, args=("TOEFL Reading"))
st.button("Go to Cambridge English Reading", on_click=lambda: st.session_state.exercise_context, args=("Cambridge English Reading"))
st.button("Go to TOEFL Writing", on_click=lambda: st.session_state.exercise_context, args=("TOEFL Writing"))
st.button("Go to Cambridge English Writing", on_click=lambda: st.session_state.exercise_context, args=("Cambridge English Writing"))