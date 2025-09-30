from src.helper import load_pdf_file,text_split,download_huggingface_embeddings
from pinecone.grpc import PineconeGRPC as Pinecone
from pinecone import ServerlessSpec
from langchain_pinecone import PineconeVectorStore
from dotenv import load_dotenv
import os


load_dotenv()
PINECONE_API_KEY = os.getenv('pcsk_7N9fFA_MFo69TpSamPi4AArfvpDRMRx5Wpb8NPsFuMMrSiXpKuBMjyz2xYLV5TmccgSR6h')
os.environ["PINECONE_API_KEY"] = "pcsk_7N9fFA_MFo69TpSamPi4AArfvpDRMRx5Wpb8NPsFuMMrSiXpKuBMjyz2xYLV5TmccgSR6h"

extracted_data = load_pdf_file(data="Data/")
text_chunks = text_split(extracted_data)
embeddings = download_huggingface_embeddings()  

pc = Pinecone(api_key="pcsk_7N9fFA_MFo69TpSamPi4AArfvpDRMRx5Wpb8NPsFuMMrSiXpKuBMjyz2xYLV5TmccgSR6h")
index_name = "medibot"

pc.create_index(
    name=index_name,
    dimension=384,
    metric="cosine",
    spec=ServerlessSpec(
        cloud="aws",
        region="us-east-1"
    )
)   

docsearch = PineconeVectorStore.from_texts([t.page_content for t in text_chunks], embeddings, index_name=index_name)