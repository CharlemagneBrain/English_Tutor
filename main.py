import streamlit as st
from docx import Document
import os
import numpy as np
import asyncio

from utils.model_schema import Role, Message
from utils.func_tools import (chatgpt_completion, async_convert_to_text,
    find_embedding_candidates, load_tokenizer, load_transformers, split_pages_into_chunks,
    vectorize)

st.set_page_config(page_title="NexAI English Tutor", page_icon=":books:", layout="wide")

st.title("NexAI English Tutor Chat")
st.markdown("### Welcome to your English Tutor! 👋📚")

openai_api_key = st.sidebar.text_input("OpenAI API Key", type="password")
transformers_cache = ""
uploaded_files = st.sidebar.file_uploader("Upload PDF or DOCX files", type=["pdf", "docx"], accept_multiple_files=True)

if 'knowledge_base' not in st.session_state:
    st.session_state.knowledge_base = None
if 'transformer' not in st.session_state:
    st.session_state.transformer = None
if 'history' not in st.session_state: 
    st.session_state.history = []
    
async def build_index_async(uploaded_files):
    """
        Asynchronously builds an index from uploaded files.

        This function handles the uploading of files, converts them to text,
        splits the text into manageable chunks, vectorizes these chunks, and
        stores the resulting knowledge base in the session state.

        Args:
        - uploaded_files (list of UploadedFile): A list of files uploaded by the user.
       
    """
    tokenizer = load_tokenizer()
    transformer = load_transformers(model_name="all-MiniLM-L6-v2", cache_folder=transformers_cache)

    file_paths = [file.name for file in uploaded_files]
    for file in uploaded_files:
        with open(file.name, 'wb') as f:
            f.write(file.getbuffer())

    texts = await async_convert_to_text(file_paths)
    st.write(f'Nombre de documents fournis: {len(file_paths)}')
    chunks = split_pages_into_chunks(texts, 512, tokenizer)
    knowledge_base = vectorize(chunks, transformer)

    for file_path in file_paths:
        os.remove(file_path)

    st.session_state.knowledge_base = knowledge_base
    st.session_state.transformer = transformer

def get_response(query):
    chunks, embeddings = list(zip(*st.session_state.knowledge_base))
    corpus_embeddings = np.vstack(embeddings)

    query_embedding = st.session_state.transformer.encode(query)
    paragraphes = find_embedding_candidates(
        query_embedding=query_embedding,
        chunks=chunks,
        corpus_embeddings=corpus_embeddings,
        top_k=7
    )

    context = "\n\n".join(paragraphes)
    completion_response = chatgpt_completion(context, query, st.session_state.history, api_key=openai_api_key)
    
    response = ""
    for chunk in completion_response:
        content = chunk.choices[0].delta.content
        if content is not None:
            response += content
    
    st.session_state.history.append({"role": "user", "content": query})
    st.session_state.history.append({"role": "assistant", "content": response})
        
    return response


if uploaded_files and st.sidebar.button("Chargez le document"):
    asyncio.run(build_index_async(uploaded_files))

if st.session_state.knowledge_base:
    for message in st.session_state.history:
        if message["role"] == "user":
            st.write(f"**Vous:** {message['content']}")
        else:
            st.write(f"**NexAI Tutor:** {message['content']}")
            
    user_query = st.text_input("Discutez:")
    if user_query:
        response = get_response(user_query)
        st.write(response)
else:
    st.write("Veuillez chargez le fichier PDF ")
