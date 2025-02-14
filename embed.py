# This module handles the embedding process, including saving uploaded files, loading and splitting data, and adding documents to the vector database.


import os
from datetime import datetime
from werkzeug.utils import secure_filename
from langchain_community.document_loaders import PyPDFLoader, UnstructuredHTMLLoader, PythonLoader, UnstructuredRSTLoader, JSONLoader, TomlLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from get_vector_db import get_vector_db

TEMP_FOLDER = os.getenv("TEMP_FOLDER", "./_temp")


# Function to check if the uploaded file is allowed (only PDF files)
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ["html", "pdf", "py", "rst", "json", "toml"]


# Function to save the uploaded file to the temporary folder
def save_file_orig(file):
    # Save the uploaded file with a secure filename and return the file path
    ct = datetime.now()
    ts = ct.timestamp()
    filename = str(ts) + "_" + secure_filename(file.filename)
    file_path = os.path.join(TEMP_FOLDER, filename)
    file.save(file_path)

    return file_path

def save_file(file_or_path):
    ct = datetime.now()
    ts = ct.timestamp()

    # Determine if the input is a file or file path
    if hasattr(file_or_path, 'filename'):  # This checks if it's a file object
        filename = secure_filename(file_or_path.filename)
        file_path = os.path.join(TEMP_FOLDER, f"{ts}_{filename}")
        file_or_path.save(file_path)  # Save the uploaded file
    else:  # If it's a file path
        filename = os.path.basename(file_or_path)
        file_path = os.path.join(TEMP_FOLDER, f"{ts}_{filename}")
        os.rename(file_or_path, file_path)  # Move the file to the temporary folder

    return file_path


# Function to load and split the data from the PDF file
def load_and_split_data(file_path):
    file_extension = os.path.splitext(file_path)[1].lower()
    
    try:
        # Load the data based on the file extension
        if file_extension == '.pdf':
            loader = PyPDFLoader(file_path=file_path)
        if file_extension == '.html':
            loader = UnstructuredHTMLLoader(file_path=file_path)
        elif file_extension == '.py':
            loader = PythonLoader(file_path=file_path)
        elif file_extension == '.rst':
            loader = UnstructuredRSTLoader(file_path=file_path)
        elif file_extension == '.json':
            loader = JSONLoader(file_path=file_path, jq_schema='.', text_content=False)
        elif file_extension == '.toml':
            loader = TomlLoader(file_path)
        else:
            raise ValueError(f"Unsupported file extension: {file_extension}")
    except Exception as e:
        raise ValueError(f"Error loading file: {e}")
    # split the data into chunks
    data = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=7500, chunk_overlap=100)
    chunks = text_splitter.split_documents(data)

    return chunks


# Main function to handle the embedding process
def embed_orig_flask(file, collection_name):
    # Check if the file is valid, save it, load and split the data, add to the database, and remove the temporary file
    if file.filename != "" and file and allowed_file(file.filename):
        file_path = save_file(file)
        chunks = load_and_split_data(file_path)
        db = get_vector_db(COLLECTION_NAME=collection_name)
        db.add_documents(chunks)
        # db.persist() #not needed with  langchain_chroma
        os.remove(file_path)

        return True

    return False


def embed(file_path, collection_name):
    # Ensure the file exists
    if not os.path.isfile(file_path):
        return False

    if not allowed_file(file_path):
        return False

    # Check if the file is valid, save it, load and split the data, add to the database, and remove the temporary file
    file_path_new = save_file(file_path)
    chunks = load_and_split_data(file_path_new)
    db = get_vector_db(COLLECTION_NAME=collection_name)
    db.add_documents(chunks)
    # db.persist() #not needed with  langchain_chroma
    os.remove(file_path_new)

    return True
