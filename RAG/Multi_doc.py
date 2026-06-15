import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_spiltters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

## Loading raw knowledge

def load_documents(folder_path:str):
    if not os.path.exists(folder_path):
        ## We are checking to see if the folder path the user provided actually exists on the computer.
        raise FileNotFoundError(f"folder {folder_path} does not exist")
        ## If it does not exist, we immediately stop the program and throw an error message

    documents=[] ##  creating an empty list (a collection)  for reading multiple documents, we need a place to store them as we read them
    for filename in os.listdir(folder_path):
        ## Loop tells the computer: "Look inside folder_path
        ## We want to process every file in the folder one by one automatically, rather than typing out the name of every single file manually.
        if filename.endswith(".pdf"):
            file_path = os.path.join(folder_path, filename)
            ## We are gluing together the folder_path and the filename to create the full "address" of the file.
            ##The os.listdir loop only gives us the name of the file (like "doc.pdf"). 
            ## But to actually open the file, the computer needs the full path so it knows exactly where it lives.
            print(f" Loading: {filename}")
            try:
                loader=PyPDFLoader(file_path)
                documents.extend(loader.load())
                ## extend() takes those pages and dumps them into the empty documents box
                ##  Why not append? If a PDF has 10 pages, append() would put the PDF into our box as one giant, single item.
            except Exception as e:
                print(f" Error loading {filename}:{e}")
    return documents


## Chunking

def split_text(documents):
    splitter= RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )

    chunks=splitter.split_documents(documents)
    print(f"created {len(chunks)} chunks")
    return chunks

embeddings=HuggingFaceEmbeddings(
    model="sentence-transformers/all-MiniLM-L6-v2"
)

def create_vector_store(chunks):
    vector_db=Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory="./chroma_db",
        collection_name="rag_docs"
    )
    return vector_db

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

def query_rag_system(query_text,vector_store):
    llm=ChatGroq(model="llama-3.3-70b-versatile",temprature=0.3)

    retriever=vector_store.as_retriever(search_kwargs={"k":3})

    prompt=ChatPromptTemplate.from_template(
        """
        You are a helpful assistant.
        Answer only using the context below.
        if the answet is not present, say "i dont know."

        <context>
        {context}
        </context>

        Question:
        {question}
        """
    )

    chain=(
        {
            "context": retriever | format_docs,
            "question": RunnablePassthrough(),
        } | prompt| llm | StrOutputParser()

    )

    response=chain.invoke(query_text)
    return response


