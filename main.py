import streamlit as st
import os
import torch as th
import numpy as np

from utils.model_schema import Role, Message
from utils.func_tools import (chatgpt_completion, convert_pdf_to_text, convert_to_text,
    find_embedding_candidates, load_tokenizer, load_transformers, split_pages_into_chunks,
    vectorize)

st.set_page_config(page_title="English Tutor", page_icon=":books:", layout="wide")

st.title("English Tutor Chat")
st.markdown("### Posez vos questions et recevez des réponses adaptées à vos documents.")


#openai_api_key = st.sidebar.text_input("OpenAI API Key", type="password")
transformers_cache = ""
path2pdf_file = st.sidebar.file_uploader("Upload PDF file", type=["pdf"])

if 'knowledge_base' not in st.session_state:
    st.session_state.knowledge_base = None
if 'transformer' not in st.session_state:
    st.session_state.transformer = None
if 'history' not in st.session_state: 
    st.session_state.history = []
    
def build_index(path2pdf_file):
    tokenizer = load_tokenizer()
    transformer = load_transformers(model_name="all-MiniLM-L6-v2", cache_folder=transformers_cache)

    pages = convert_pdf_to_text(path2pdf_file)
    st.write(f'Nombre de pages : {len(pages)}')
    chunks = split_pages_into_chunks(pages, 256, tokenizer)
    knowledge_base = vectorize(chunks, transformer)

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
    completion_response = chatgpt_completion(context, query, st.session_state.history)
    
    response = ""
    for chunk in completion_response:
        content = chunk.choices[0].delta.content
        if content is not None:
            response += content
    
    st.session_state.history.append({"role": "user", "content": query})
    st.session_state.history.append({"role": "assistant", "content": response})
        
    return response

# Interface principale
if path2pdf_file is not None and st.sidebar.button("Chargez le document"):
    build_index(path2pdf_file)

if st.session_state.knowledge_base:
    for message in st.session_state.history:
        if message["role"] == "user":
            st.write(f"**Vous:** {message['content']}")
        else:
            st.write(f"**NexAI Tutor:** {message['content']}")
            
    user_query = st.text_input("Discutez:")
    if user_query:
        response = get_response(user_query)
        st.markdown("### Réponse")
        st.write(response)
else:
    st.write("Veuillez chargez le fichier PDF ")
