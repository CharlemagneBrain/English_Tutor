from openai import OpenAI
import os
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

# from config import OPENAI_API_KEY

def load_tokenizer(encoder_name: str = 'gpt-4-turbo') -> tiktoken.Encoding:
    """
    Load a tokenizer based on the specified encoder model.
    For dividing text into chunks.

    Args:
        encoder_name (str): The name of the encoder model to be used for tokenization. Default is 'gpt-4-turbo'.

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

def convert_pdf_to_text(pdf_file: str) -> List[str]:
    """
    Convert a PDF file to a list of text strings, one per page.

    Args:
        pdf_file (str): The file path of the PDF document to be converted.

    Returns:
        List[str]: A list containing the extracted text from each page of the PDF.
    """
    try:
        reader = PyPDF2.PdfReader(pdf_file)
        return [page.extract_text() for page in reader.pages]
    except Exception as e:
        raise ValueError(f"Error reading PDF file {pdf_file}: {e}")

def convert_docx_to_text(docx_file: str) -> List[str]:
    """
    Convert a DOCX file to a list of text strings, one per paragraph.

    Args:
        docx_file (str): The file path of the DOCX document to be converted.

    Returns:
        List[str]: A list containing the text of each paragraph in the DOCX document.
    """
    try:
        doc = Document(docx_file)
        return [paragraph.text for paragraph in doc.paragraphs]
    except Exception as e:
        raise ValueError(f"Error reading DOCX file {docx_file}: {e}")

def convert_to_text(file_paths: List[str]) -> List[str]:
    """
    Convert multiple files to text, where each file can be either a PDF or a DOCX.

    Args:
        file_paths (List[str]): A list of file paths to be converted.

    Returns:
        List[str]: A list of strings, containing the text extracted from all files.
    """
    results: List[str] = []
    for file_path in file_paths:
        if file_path.endswith('.pdf'):
            results.extend(convert_pdf_to_text(file_path))
        elif file_path.endswith('.docx'):
            results.extend(convert_docx_to_text(file_path))
        else:
            raise ValueError(f"Unsupported file format: {file_path}")
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

def find_embedding_candidates(query_embedding: np.ndarray, chunks: List[str], corpus_embeddings: np.ndarray, top_k: int = 7) -> List[str]:
    """
    Find the top-k embedding candidates that are most similar to the query embedding.

    Args:
        query_embedding (np.ndarray): The query vector.
        chunks (List[str]): The list of text chunks.
        corpus_embeddings (np.ndarray): The array of vectors corresponding to the text chunks.
        top_k (int): The number of top similar chunks to return.

    Returns:
        List[str]: A list of the top 'k' chunks that are most similar to the query embedding.
    """
    dot_product = np.dot(query_embedding, corpus_embeddings.T)
    norms = np.linalg.norm(query_embedding) * np.linalg.norm(corpus_embeddings, axis=1)
    scores = dot_product / norms

    sorted_chunks = sorted(zip(chunks, scores), key=op.itemgetter(1), reverse=True)
    return [chunk for chunk, _ in sorted_chunks[:top_k]]

def chatgpt_completion(context: str, query: str, history: List[Dict[str, str]]):
    """
    Generates a response from the GPT-4 Turbo model based on the user's query within a given context.

    Parameters:
        context (str): A string that sets the context or background information for the conversation.
        query (str): The user's query or question in string format.

    Returns:
        Any: The response from the GPT-4 Turbo model.
    """
    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    
    messages = [build_system_settings(context).dict()] + history + \
              [Message(role=Role.USER, content=f"Voici ma question : {query}").dict()]
    
    completion_rsp = client.chat.completions.create(
        model='gpt-4-turbo',
        messages=messages,
        stream=True 
    )
    
    return completion_rsp

