from langchain_community.document_loaders import PDFPlumberLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
from langchain_community.vectorstores import FAISS

pdfs_directory = 'pdfs/'
def upload_pdf():
  with open(pdfs_directory+file.name,"wb")as f:
    f.write(file.getbuffer())


def load_pdf(file_path):
  loader = PDFPlumberLoader(file_path)
  documents = loader.load()
  return documents
file_path = 'adityaresume_1740157326.pdf'
documents =load_pdf(file_path)
def create_chunks(documents):
  text_splitter = RecursiveCharacterTextSplitter(
    chunk_size= 1000,
    chunk_overlap = 200,
    add_start_index=True
  )
  text_chunks =text_splitter.split_documents(documents)

  return text_chunks

text_chunks = create_chunks(documents)
ollama_model_name ="deepseek-r1:7b"

def get_embedding_model(ollama_model_name):
  embeddings = OllamaEmbeddings(model=ollama_model_name)
  return embeddings

FAISS_DB_PATH = "vectorstore/db_faiss"
try:
    faiss_db = FAISS.from_documents(text_chunks, get_embedding_model(ollama_model_name))
except Exception as e:
    print(f"An error occurred: {e}")
    
faiss_db.save_local(FAISS_DB_PATH)