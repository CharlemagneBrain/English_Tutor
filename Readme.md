# NexAI English Tutor using RAG

Welcome to NexAI English Tutor, an intelligent tutoring system designed to help students prepare for the TOEFL exam. This application provides personalized exercises and responses based on the materials provided by the students.

## Table of Contents

- [Features](#features)
- [Technologies](#technologies)
- [Setup](#setup)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Contributing](#contributing)
- [License](#license)

## Features

- **Ingestion of Documents**: Convert and index course materials and TOEFL example exams in PDF and DOCX formats.
- **Text Extraction and Processing**: Convert documents to text, chunk them, and vectorize the content for efficient retrieval.
- **User Interface**: Streamlit-based interface for interacting with the tutor, asking questions, and receiving personalized exercises.
- **Exercise Generation**: Generate Reading and Writing exercises based on provided documents.
- **OpenAI Integration**: Use OpenAI's API to generate responses and exercises.
- **Vector Search**: Store and retrieve text embeddings using Qdrant for relevant content retrieval.

## Technologies

- **Python** for text processing and application development.
- **Streamlit** for the user interface.
- **Qdrant** for vector database.
- **OpenAI** for generating responses and exercises.
- **PyPDF2** and **python-docx** for document conversion.
- **Sentence Transformers** for text vectorization.
- **tiktoken** for text tokenization.

## Setup

1. **Clone the repository**:
    ```bash
    git clone https://github.com/CharlemagneBrain/English_Tutor
    cd nexai-english-tutor
    ```

2. **Create and activate a virtual environment**:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3. **Install the dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

4. **Set up environment variables**:
    Create a `.env` file in the root directory and add your OpenAI API key:
    ```env
    OPENAI_API_KEY=your_openai_api_key
    ```

5. **Download the required models**:
    The model `all-MiniLM-L6-v2` will be automatically downloaded to the `models_cache` folder when you run the application for the first time.

## Usage

1. **Run the application**:
    ```bash
    streamlit run main.py
    ```

2. **Interact with the tutor**:
    - Enter your OpenAI API key in the sidebar.
    - Ask questions and receive personalized TOEFL exercises.

## Project Structure
```
nexai-english-tutor/
│
├── main.py # Main application file
├── requirements.txt # Project dependencies
├── models_cache/ # Folder for cached models
├── utils/
    │ ├── model_schema.py # Schema for user and assistant messages
    │ ├── func_tools.py # Utility functions for text processing and interaction with OpenAI
    │ ├── ingest.py # Script for creating embeddings and storing them in Qdrant
│
├── data_connections_utils/ # Utilities for database connections
│ ├── databases_conn.py
│ ├── databases_user_info.py
│
└── README.md # Project documentation
```
## Contributing

Contributions are welcome! Please fork the repository and submit a pull request for any features, bug fixes, or enhancements.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
