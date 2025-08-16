from app.core.config import OPENAI_API_KEY
from app.core.database import SessionLocal
from app.models.regulation import Regulation
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from sqlalchemy.orm import Session
import os
import requests

PDFS_DIR = "data/pdfs"
FAISS_INDEX_PATH = "data/faiss_index"
NUM_PDFS_TO_PROCESS = 15


def process_all_pdfs():
    os.makedirs(PDFS_DIR, exist_ok=True)
    db: Session = SessionLocal()

    regulations = (
        db.query(Regulation)
        .filter(Regulation.file_pdf.isnot(None))
        .limit(NUM_PDFS_TO_PROCESS)
        .all()
    )
    db.close()

    # Define a User-Agent header to mimic a browser
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    documents = []
    for reg in regulations:
        pdf_path = os.path.join(PDFS_DIR, f"{reg.regulation_id}.pdf")
        if not os.path.exists(pdf_path):
            print(f"Downloading {reg.file_pdf}...")
            try:
                # Use the headers in the request
                response = requests.get(reg.file_pdf, headers=headers)
                response.raise_for_status()
                with open(pdf_path, "wb") as f:
                    f.write(response.content)
            except requests.RequestException as e:
                print(f"Failed to download {reg.file_pdf}: {e}")
                continue

        # This part only runs if the PDF exists or was downloaded successfully
        print(f"Loading document {pdf_path}...")
        try:
            loader = PyPDFLoader(pdf_path)
            documents.extend(loader.load())
        except Exception as e:
            print(f"Failed to load or parse PDF {pdf_path}: {e}")

    # Add a check to ensure documents were actually loaded before proceeding
    if not documents:
        print("No documents were loaded. Aborting FAISS index creation.")
        return

    # Split documents into chunks
    print("Splitting documents into chunks...")
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    splits = text_splitter.split_documents(documents)

    # Create embeddings and store in FAISS
    print("Creating embeddings and building FAISS index...")
    embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)
    vector_store = FAISS.from_documents(splits, embeddings)

    # Save the FAISS index locally
    vector_store.save_local(FAISS_INDEX_PATH)
    print(f"FAISS index created and saved to {FAISS_INDEX_PATH}")


if __name__ == "__main__":
    process_all_pdfs()
