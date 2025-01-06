from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone, ServerlessSpec
from langchain.chains import create_history_aware_retriever
from langchain_core.prompts import MessagesPlaceholder
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv
import os
import time

load_dotenv()

# Singleton cache
singleton_cache = {}

def get_pinecone_index():
    if "pinecone_index" in singleton_cache:
        return singleton_cache["pinecone_index"]

    index_name = "crustdata-index"
    pinecone_api_key = os.environ.get("PINECONE_API_KEY")

    pc = Pinecone(api_key=pinecone_api_key)
    existing_indexes = [index_info["name"] for index_info in pc.list_indexes()]

    if index_name not in existing_indexes:
        pc.create_index(
            name=index_name,
            dimension=3072,
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region="us-east-1"),
        )
        while not pc.describe_index(index_name).status["ready"]:
            time.sleep(1)

    singleton_cache["pinecone_index"] = pc.Index(index_name)
    return singleton_cache["pinecone_index"]

def get_embedding_model():
    os.environ['GOOGLE_API_KEY'] = os.getenv('GEMINI_API_KEY')
    if "embedding_model" in singleton_cache:
        return singleton_cache["embedding_model"]

    embeddings = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")
    singleton_cache["embedding_model"] = embeddings
    return embeddings

def get_llm_model():
    if "llm_model" in singleton_cache:
        return singleton_cache["llm_model"]

    llm = ChatGroq(
        api_key=os.environ.get('GROQ_API_KEY'),
        model_name="mixtral-8x7b-32768",
        temperature=0.7
    )
    singleton_cache["llm_model"] = llm
    return llm

def get_history_aware():
    if "history_aware_retriever" in singleton_cache:
        return singleton_cache["history_aware_retriever"]

    contextualize_q_system_prompt = (
        "Given a chat history and the latest user question "
        "which might reference context in the chat history, "
        "formulate a standalone question which can be understood "
        "without the chat history. Do NOT answer the question, "
        "just reformulate it if needed and otherwise return it as is."
    )

    contextualize_q_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", contextualize_q_system_prompt),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ]
    )
    llm = get_llm_model()
    retriever = calling_vectorstore()
    history_aware_retriever = create_history_aware_retriever(
        llm, retriever, contextualize_q_prompt
    )

    singleton_cache["history_aware_retriever"] = history_aware_retriever
    return history_aware_retriever

def encode_pdf(chunk_size=1000, chunk_overlap=200):
    with open("dataset/data.txt") as f:
        dataset = f.read()
    
    documents = Document(page_content=dataset)
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size, chunk_overlap=chunk_overlap, length_function=len
    )
    texts = text_splitter.split_documents([documents])

    index = get_pinecone_index()
    embeddings = get_embedding_model()
    vectorstore = PineconeVectorStore(index=index, embedding=embeddings)
    vectorstore.upsert_documents(texts)

def calling_vectorstore():
    index = get_pinecone_index()
    embeddings = get_embedding_model()
    vectorstore = PineconeVectorStore(index=index, embedding=embeddings)
    chunks_query_retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
    return chunks_query_retriever
