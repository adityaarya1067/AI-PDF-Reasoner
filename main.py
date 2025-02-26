import streamlit as st
import os
from dotenv import load_dotenv
from langchain_community.document_loaders import PDFPlumberLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.vectorstores import FAISS
from langchain_groq import ChatGroq


load_dotenv()

api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    raise ValueError("GROQ_API_KEY not found in environment variables")

custom_prompt_template = """
Use the pieces of information provided in the context to answer user's question.
If you dont know the answer, just say that you dont know, dont try to make up an answer. 
Dont provide anything out of the given context
Question: {question} 
Context: {context} 
Answer:
"""

ollama_model_name="deepseek-r1:7b"
embeddings = OllamaEmbeddings(model="deepseek-r1:7b")
FAISS_DB_PATH="vectorstore/db_faiss"
pdfs_directory = 'pdfs/'

# Initialize Groq with API key
llm_model = ChatGroq(
    temperature=0.7,
    groq_api_key=api_key,
    model="deepseek-r1-distill-llama-70b"
)

# Create necessary directories if they don't exist
os.makedirs(pdfs_directory, exist_ok=True)
os.makedirs(os.path.dirname(FAISS_DB_PATH), exist_ok=True)

def upload_pdf(file):
    with open(pdfs_directory + file.name, "wb") as f:
        f.write(file.getbuffer())


def load_pdf(file_path):
    loader = PDFPlumberLoader(file_path)
    documents = loader.load()
    return documents


def create_chunks(documents): 
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size = 1000,
        chunk_overlap = 200,
        add_start_index = True
    )
    text_chunks = text_splitter.split_documents(documents)
    return text_chunks


def get_embedding_model(ollama_model_name):
    embeddings = OllamaEmbeddings(model=ollama_model_name)
    return embeddings


def create_vector_store(db_faiss_path, text_chunks, ollama_model_name):
    faiss_db=FAISS.from_documents(text_chunks, get_embedding_model(ollama_model_name))
    faiss_db.save_local(db_faiss_path)
    return faiss_db


def retrieve_docs(faiss_db, query):
    return faiss_db.similarity_search(query)


def get_context(documents):
    context = "\n\n".join([doc.page_content for doc in documents])
    return context


def answer_query(documents, model, query):
    context = get_context(documents)
    prompt = ChatPromptTemplate.from_template(custom_prompt_template)
    chain = prompt | model
    return chain.invoke({"question": query, "context": context})


uploaded_file = st.file_uploader(
    "Upload PDF",
    type="pdf",
    accept_multiple_files=False
)


user_query = st.text_area("Enter your prompt: ", height=150 , placeholder= "Ask Anything!")

ask_question = st.button("Ask AI PDF Reasoner")

if ask_question:

    if uploaded_file and user_query:
        upload_pdf(uploaded_file)
        documents = load_pdf(pdfs_directory + uploaded_file.name)
        text_chunks = create_chunks(documents)
        faiss_db = create_vector_store(FAISS_DB_PATH, text_chunks, ollama_model_name)

        retrieved_docs=retrieve_docs(faiss_db, user_query)
        response=answer_query(documents=retrieved_docs, model=llm_model, query=user_query)

        st.chat_message("user").write(user_query)
        st.chat_message("AI Lawyer").write(response)

    else:
        st.error("Kindly upload a valid PDF file and/or ask a valid Question!")
