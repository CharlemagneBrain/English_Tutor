# English Tutor Chatbot with RAG

This project implements an English Tutor Chatbot powered by GPT-4 and a Retrieval-Augmented Generation (RAG) system. The chatbot helps French-speaking students improve their English skills by providing personalized feedback and exercises based on user-uploaded PDF documents. 

## Technical Overview

The system works in the following steps:

1. **Document Processing:** 
    - The user uploads a PDF document. 
    - The document is converted into text using `PyPDF2`.
    - The text is split into chunks of a defined size using `tiktoken`.

2. **Embedding and Indexing:**
    - Each text chunk is vectorized using a pre-trained SentenceTransformer model (`all-MiniLM-L6-v2`). 
    - The embeddings are stored in memory, forming a knowledge base for the specific document.

3. **Question Answering:**
    - The user asks a question in English or French.
    - The question is embedded using the same SentenceTransformer model.
    - The most similar chunks from the knowledge base are retrieved based on cosine similarity.
    - The retrieved chunks are added to the context along with the conversation history. 
    - This context and the user's question are sent to GPT-4 to generate a comprehensive response.

4. **Exercise Generation:**
    - The user can also request personalized exercises. 
    - GPT-4 generates exercises based on the retrieved chunks and its understanding of English language learning.

5. **Chat Interface:**
    - The Streamlit framework provides a user-friendly interface for interacting with the chatbot.
    - The conversation history is displayed above the input field, similar to ChatGPT. 

## Project Structure

The project consists of the following files:

- **`main.py`:** The main application file, responsible for handling user interactions, document processing, and communication with GPT-4 via the OpenAI API. 
- **`utils.py`:** Contains utility functions for document conversion, chunk splitting, embedding, candidate retrieval, and interacting with GPT-4.
- **`model_schema.py`:** Defines the structure of messages exchanged between the user, the system, and GPT-4.

## Installation and Setup

1. **Clone the repository:** 
   ```bash
   git clone https://github.com/CharlemagneBrain/English_Tutor.git
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
   Make sure you have the required libraries, including `streamlit`, `openai`, `sentence_transformers`, `PyPDF2`, and `tiktoken`.

3. **Set up OpenAI API Key:**
   - Obtain an API key from [https://beta.openai.com/account/api-keys](https://beta.openai.com/account/api-keys).
   - Set the environment variable `OPENAI_API_KEY` to your key. 

4. **Run the application:**
   ```bash
   streamlit run main.py
   ```

## Usage

1. Upload a PDF document in English using the file uploader. 
2. Click the "Load Document" button to process and index the document.
3. Ask your questions or request personalized exercises in the text input field. 
4. The chatbot will respond based on the information extracted from the uploaded document and its understanding of English language learning.

## Future Improvements

- **Multilingual support:** Allow users to upload documents in other languages. 
- **More exercise types:** Implement a wider variety of English exercises (e.g., grammar, vocabulary, pronunciation). 
- **User profiles:** Store user data and learning progress to provide personalized recommendations.
- **Interactive exercises:** Make exercises more engaging and interactive. 

## Contributing

Contributions are welcome! Feel free to open issues or submit pull requests.


