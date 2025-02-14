# This module initializes and returns the vector database instance used for storing and retrieving document embeddings.



import os

# these three lines swap the stdlib sqlite3 lib with the pysqlite3 package
#__import__('pysqlite3')
#import sys
#sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
import chromadb

from langchain_community.embeddings import OllamaEmbeddings
from langchain_chroma import Chroma

def get_vector_db(CHROMA_PATH='chroma', COLLECTION_NAME='local-rag'):
    
    #TEXT_EMBEDDING_MODEL = os.getenv('TEXT_EMBEDDING_MODEL')
    
    #embedding = OllamaEmbeddings(model=TEXT_EMBEDDING_MODEL,show_progress=True)

    chroma_client = chromadb.HttpClient(host='localhost', port=8000)
    
    #db = Chroma(
    #    client=chroma_client,
    #    collection_name=COLLECTION_NAME,
    #    persist_directory=CHROMA_PATH,
    #    embedding_function=embedding
    #)
    # Get all collections
    collections = chroma_client.list_collections()
    print(collections)
    
    # Delete each collection
    
    #chroma_client.delete_collection("PyFluent")

    return "Success"

print(get_vector_db())
