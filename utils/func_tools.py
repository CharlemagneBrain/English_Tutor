from openai import OpenAI
import PyPDF2
import tiktoken
from docx import Document
from sentence_transformers import SentenceTransformer
import numpy as np
import operator as op 
import itertools as it
from typing import List, Tuple, Dict, Any
from utils.model_schema import Message, Role
from utils.prompt_manager import build_system_settings
import asyncio
from qdrant_client import QdrantClient

def load_tokenizer(encoder_name: str = 'gpt-4o') -> tiktoken.Encoding:
    """
    Load a tokenizer based on the specified encoder model.
    For dividing text into chunks.

    Args:
        encoder_name (str): The name of the encoder model to be used for tokenization. Default is 'gpt-4o'.

    Returns:
        tiktoken.Encoding: An instance of the Encoding class from the tiktoken library, initialized with the specified encoder.
    """
    return tiktoken.encoding_for_model(encoder_name)

def load_transformers(model_name: str, cache_folder: str, device: str = 'cpu') -> SentenceTransformer:
    """
    Load a transformer model for sentence embeddings.

    Args:
        model_name (str): The name or path of the model to be loaded.
        cache_folder (str): The folder path where the model cache should be stored.
        device (str): The device type on which the model should be run ('cpu' or 'gpu'). Default is 'cpu'.

    Returns:
        SentenceTransformer: An instance of the SentenceTransformer class, initialized with the specified model and configuration.
    """
    return SentenceTransformer(
        model_name_or_path=model_name,
        cache_folder=cache_folder,
        device=device
    )


async def async_convert_pdf_to_text(pdf_file: str) -> List[str]:
    reader = PyPDF2.PdfReader(pdf_file)
    return [page.extract_text() for page in reader.pages]

async def async_convert_docx_to_text(docx_file: str) -> List[str]:
    doc = Document(docx_file)
    return [paragraph.text for paragraph in doc.paragraphs]

async def async_convert_to_text(file_paths: List[str]) -> List[str]:
    """
        Asynchronously converts multiple files (PDF or DOCX) to text. This function determines the type of each file
        and calls the appropriate conversion function.

        Args:
        file_paths (List[str]): A list of file paths, where each path points to a PDF or DOCX file.

        Returns:
        List[str]: A combined list of strings containing the text extracted from all the files.
    """
    results: List[str] = []
    tasks = []
    
    for file_path in file_paths:
        if file_path.endswith('.pdf'):
            tasks.append(async_convert_pdf_to_text(file_path))
        elif file_path.endswith('.docx'):
            tasks.append(async_convert_docx_to_text(file_path))

    texts = await asyncio.gather(*tasks)
    for text in texts:
        results.extend(text)
    return results

def split_pages_into_chunks(pages: List[str], chunk_size: int, tokenizer: tiktoken.Encoding) -> List[str]:
    """
    Split pages into chunks of specified size using the given tokenizer.

    Args:
        pages (List[str]): List of text pages to be split.
        chunk_size (int): The size of each chunk in terms of number of tokens.
        tokenizer (tiktoken.Encoding): The tokenizer to be used for encoding and decoding text.

    Returns:
        List[str]: A list of text chunks.
    """
    pages_tokens = [tokenizer.encode(page) for page in pages]
    total_tokens = list(it.chain(*pages_tokens))

    nb_chunks = max(1, round(len(total_tokens) / chunk_size))

    return [tokenizer.decode(chunk_tokens) for chunk_tokens in np.array_split(total_tokens, nb_chunks)]

def vectorize(chunks: List[str], transformer: SentenceTransformer, device: str = "cpu") -> List[Tuple[str, np.ndarray]]:
    """
    Vectorize the given text chunks using the specified transformer model.

    Args:
        chunks (List[str]): The text chunks to be vectorized.
        transformer (SentenceTransformer): The transformer model to be used for vectorization.
        device (str): The device type on which the model should be run ('cpu' or 'gpu').

    Returns:
        List[Tuple[str, np.ndarray]]: A list of tuples containing the original text chunk and its corresponding vector.
    """
    embeddings = transformer.encode(
        sentences=chunks,
        batch_size=64,
        device=device
    )
    return list(zip(chunks, embeddings))

# def find_embedding_candidates(query_embedding: np.ndarray, chunks: List[str], corpus_embeddings: np.ndarray, top_k: int = 7) -> List[str]:
#     """
#     Find the top-k embedding candidates for a given query embedding.

#     Args:
#         query_embedding (np.ndarray): The embedding of the query.
#         chunks (List[str]): The text chunks available for comparison.
#         corpus_embeddings (np.ndarray): The embeddings of the text chunks.
#         top_k (int): The number of top candidates to return. Default is 7.

#     Returns:
#         List[str]: A list of the top-k text chunks that are most similar to the query.
#     """
#     dot_product = np.dot(query_embedding, corpus_embeddings.T)
#     norms = np.linalg.norm(query_embedding) * np.linalg.norm(corpus_embeddings, axis=1)
#     scores = dot_product / norms

#     sorted_chunks = sorted(zip(chunks, scores), key=op.itemgetter(1), reverse=True)
    
#     return [chunk for chunk, _ in sorted_chunks[:top_k]]

def find_embedding_candidates(query_embedding: np.ndarray, top_k: int = 7) -> List[str]:
    client = QdrantClient(
        url="https://c80cf935-0f6b-4fe6-af49-9da5c9752f82.us-east4-0.gcp.cloud.qdrant.io:6333", 
        api_key="Dc_jwEpz1fHy5oqx6OX1gUuDmCTkm-ghCo0dwyliQv7XYLN9KLFdVw",
    )
    response = client.search(
        collection_name="toefl_tutor",
        query_vector=query_embedding.tolist(),
        limit=top_k
    )
    return [hit.payload['text'] for hit in response]

def chatgpt_completion(context: str, query: str, history: List[Dict[str, str]], api_key: str):
    """
    Generate a completion using the ChatGPT model based on the provided context and query.

    Args:
        context (str): The context or background information for the query.
        query (str): The specific query or question.
        history (List[Dict[str, str]]): A list of previous interactions in the form of dictionaries with roles and content.
        api_key (str): The API key used to authenticate with the OpenAI service.

    Returns:
        Any: The response from the ChatGPT model as generated by the OpenAI API.
    """
    client = OpenAI(api_key=api_key) #os.environ["OPENAI_API_KEY"]
    
    messages = [build_system_settings(context).dict()] + history + \
              [Message(role=Role.USER, content=f"Voici ma question : {query}").dict()]
    
    completion_rsp = client.chat.completions.create(
        model='gpt-4o',
        messages=messages,
        stream=True 
    )
    
    return completion_rsp

