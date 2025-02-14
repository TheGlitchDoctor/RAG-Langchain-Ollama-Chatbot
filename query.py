# This module processes user queries by generating multiple versions of the query, retrieving relevant documents, and providing answers based on the context.


import os
from langchain_community.chat_models import ChatOllama
from langchain_community.llms import Ollama
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.callbacks.manager import CallbackManager

from langchain.prompts import ChatPromptTemplate, PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain.retrievers.multi_query import MultiQueryRetriever
from get_vector_db import get_vector_db

LLM_MODEL = os.getenv("LLM_MODEL", "qwen2.5-coder:3b")


# Function to get the prompt templates for generating alternative questions and answering based on context
def get_prompt():
    QUERY_PROMPT = PromptTemplate(
        input_variables=["question","chat_history"],
        template="""You are a mechanical scripting expert specializing in generating Python code using provided tools and data. Your demeanor is professional, supportive, and helpful.
        Your response should include:
        A brief explanation of the concept or solution with respect Mechanical Scripts.
        A well-formatted code snippet, if applicable, to address the user’s question.
        Ensure the response is easy to understand and tailored to the user’s needs.
        """,
    )

    template = """Answer the question based ONLY on the following context:
    {context}
    And the context provided in the chat history {chat_history}
    Then craft a clear and concise response to the user’s question:
    {question}
    """

    prompt = ChatPromptTemplate.from_template(template)

    return QUERY_PROMPT, prompt


# Main function to handle the query process
def query(input):
    if input:
        # Initialize the language model with the specified model name
        llm = ChatOllama(model=LLM_MODEL) # Ram. Error - https://github.com/langchain-ai/langchain/issues/15147
        # llm = Ollama(
        #     model=LLM_MODEL,
        #     callback_manager=CallbackManager([StreamingStdOutCallbackHandler()]),
        # )
        print("=============================")
        print(llm)  # RAM
        print("=============================")
        # Get the vector database instance
        db = get_vector_db(COLLECTION_NAME=input["collection_name"]) if "collection_name" in input else get_vector_db()

        # Get the prompt templates
        QUERY_PROMPT, prompt = get_prompt()

        # Set up the retriever to generate multiple queries using the language model and the query prompt
        retriever = MultiQueryRetriever.from_llm(
            db.as_retriever(), llm, prompt=QUERY_PROMPT
        )

        # Define the processing chain to retrieve context, generate the answer, and parse the output
        chain = (
            {"context": retriever, "question": RunnablePassthrough(), "chat_history": RunnablePassthrough()}
            | prompt
            | llm
            | StrOutputParser()
        )

        response = chain.invoke({"question":input["question"], "chat_history":input.get("chat_history", "")})

        return response

    return None
