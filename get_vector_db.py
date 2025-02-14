# This module initializes and returns the vector database instance used for storing and retrieving document embeddings.



import os

# these three lines swap the stdlib sqlite3 lib with the pysqlite3 package
#__import__('pysqlite3')
#import sys
#sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

#import chromadb
import os
from langchain_community.embeddings import OllamaEmbeddings
from langchain_chroma import Chroma

def get_vector_db(CHROMA_PATH='chroma', COLLECTION_NAME='local-rag'):
    os.environ['OLLAMA_USE_GPU'] = '1'
    os.environ['CUDA_VISIBLE_DEVICES'] = '0'
    TEXT_EMBEDDING_MODEL = 'qwen2.5-coder:3b'
    COLLECTION_NAME = COLLECTION_NAME.lower()
    embedding = OllamaEmbeddings(model=TEXT_EMBEDDING_MODEL,show_progress=True,num_gpu=1, model_kwargs={'device':'cuda', 'OLLAMA_USE_GPU':'1','CUDA_VISIBLE_DEVICES':'0'})

    #chroma_client = chromadb.HttpClient(host='localhost', port=8000)
    
    #db = Chroma(
    #    client=chroma_client,
    #    collection_name=COLLECTION_NAME,
    #    persist_directory=CHROMA_PATH,
    #    embedding_function=embedding
    #)

    db = Chroma(
        collection_name=COLLECTION_NAME,
        persist_directory=CHROMA_PATH,
        embedding_function=embedding
    )

    return db
