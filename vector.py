from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document
import os
import pandas as pd
from pathlib import Path
from commercetxt import parse_file


#embedding model
embeddings = OllamaEmbeddings(model="mxbai-embed-large")

db_location = "./chroma_db_ikea"

#boolean to check if the database already exists, if not we will add documents to it
add_documents = not os.path.exists(db_location)

products_dir = Path("hf_data/products")

#prepare documents and ids
if add_documents:
    documents = []
    ids = []

    for i, file_path in enumerate(products_dir.rglob('*')):
        if file_path.is_file():
            result = parse_file(str(file_path))
            product = result.directives.get('PRODUCT', {})
            offer = result.directives.get('OFFER', {})
            specs = result.directives.get('SPECS', {})

            document = Document(
                        page_content=str(product) + "\n" + str(offer) + "\n" + str(specs),
                        metadata={},
                        id=str(i)
            )

            documents.append(document)
            ids.append(str(i))
        

#create vector store
vector_store = Chroma(
    collection_name="ikea_products",
    persist_directory=db_location,
    embedding_function=embeddings    
)

if add_documents:
    #vector_store.add_documents(documents=documents, ids=ids)

    BATCH_SIZE = 8

    for start in range(0, len(documents), BATCH_SIZE):
        end = start + BATCH_SIZE

        '''print(
            f"Embedding {start + 1}-"
            f"{min(end, len(documents))} of {len(documents)}"
        )'''

        vector_store.add_documents(
            documents=documents[start:end],
            ids=ids[start:end],
        )

#retriever to get the top 5 most relevant documents for a given query
retriever = vector_store.as_retriever(search_kwargs={"k": 5})