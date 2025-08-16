from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA
from ...core.config import OPENAI_API_KEY

FAISS_INDEX_PATH = "data/faiss_index"

# 1. Initialize LLM and Embeddings
llm = ChatOpenAI(openai_api_key=OPENAI_API_KEY, model_name="gpt-3.5-turbo")
embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)

# 2. Load the local FAISS index
vector_store = FAISS.load_local(FAISS_INDEX_PATH, embeddings, allow_dangerous_deserialization=True)

# 3. Create a retriever
retriever = vector_store.as_retriever()

# 4. Create the RetrievalQA chain
rag_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=retriever,
    return_source_documents=True
)

def query_document_content(user_question: str) -> str:
    """
    Uses the RAG chain to answer questions based on the content of PDF documents.
    """
    result = rag_chain({"query": user_question})
    return result["result"]