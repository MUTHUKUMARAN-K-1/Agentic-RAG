import os
import json
import random
from langchain_community.document_loaders import WebBaseLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import chromadb
from chromadb.utils import embedding_functions
from duckduckgo_search import DDGS
import dotenv
import ollama
dotenv.load_dotenv()

# Use Ollama for embeddings
# Default to nomic-embed-text model for embeddings (lightweight and good quality)
ollama_embedding_model = os.environ.get("OLLAMA_EMBEDDING_MODEL", "nomic-embed-text")

def get_ollama_embedding(text):
    """Get embedding from Ollama"""
    try:
        response = ollama.embeddings(model=ollama_embedding_model, prompt=text)
        return response['embedding']
    except Exception as e:
        print(f"Error getting embedding from Ollama: {e}")
        # Fallback to ChromaDB's default embedding function
        default_ef = embedding_functions.DefaultEmbeddingFunction()
        return default_ef([text])[0]

# Custom embedding function for ChromaDB using Ollama
class OllamaEmbeddingFunction(embedding_functions.EmbeddingFunction):
    def __init__(self):
        super().__init__()
    
    def __call__(self, input):
        if isinstance(input, str):
            return get_ollama_embedding(input)
        elif isinstance(input, list):
            return [get_ollama_embedding(text) for text in input]
        else:
            raise ValueError(f"Unsupported input type: {type(input)}")

# Initialize embedding function
ollama_ef = OllamaEmbeddingFunction()

url_to_name_map = {
    "https://lilianweng.github.io/posts/2023-06-23-agent/": "Agent_Post",
    "https://lilianweng.github.io/posts/2023-03-15-prompt-engineering/": "Prompt_Engineering_Post",
    "https://lilianweng.github.io/posts/2023-10-25-adv-attack-llm/": "Adv_Attack_LLM_Post",
}


docs = {}
for url in url_to_name_map:
    try:
        loader = WebBaseLoader(url)
        docs[url] = loader.load()
    except Exception as e:
        print(f"Error loading {url}: {e}")


text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
    chunk_size=100, chunk_overlap=50
)

doc_splits = {}
for url, doc in docs.items():
    doc_splits[url] = text_splitter.split_documents(doc)


client = chromadb.PersistentClient(path="db")


def create_collection(collection_name):
    return client.get_or_create_collection(name=collection_name, embedding_function=ollama_ef)


def upload_data_to_collection(collection_name, data):
    try:
        collection = create_collection(collection_name)
        id = random.randint(10000, 99999)
        # ChromaDB will automatically use the embedding function
        collection.add(
            documents=[data],
            ids=[str(id)]
        )
        print(f"Data uploaded to collection {collection_name} with ID: {id}")
        return json.dumps({"Message": "Data uploaded successfully"})
    except Exception as e:
        print(f"Error uploading data to {collection_name}: {e}")
        return json.dumps({"Error": str(e)})



# Populate database with documents (only runs when explicitly executed, not on import)
# To populate the database, run: python3 upload.py
if __name__ == "__main__":
    print("Starting database population...")
    for url, splits in doc_splits.items():
        collection_name = url_to_name_map[url]
        print(f"Uploading to collection: {collection_name}")
        for chunk in splits:
            upload_data_to_collection(collection_name, chunk.page_content)
    print("Database population completed!")



def search_db(collection_name: str, input_query: str, n=5):
    try:
        if not isinstance(n, int) or n <= 0:
            n = 5

        collection = create_collection(collection_name)
        print("\n\nSearching {}\n\n".format(collection))
        
        # ChromaDB will automatically use the embedding function
        res = collection.query(
            query_texts=[input_query],
            n_results=n
        )
        
        
        result = [doc for doc in res['documents'][0]]
        
        return json.dumps({"Data": result})
    
    except Exception as e:
        print(f"Error searching in collection {collection_name}: {e}")
        return json.dumps({"Error": str(e)})

def Internet_search(input:str):
    print("\n\nSearching Internet \n\n")
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(input, max_results=5))
            if results:
                # Format results as a readable string without result numbers
                formatted_results = []
                for result in results:
                    title = result.get('title', 'N/A')
                    body = result.get('body', 'N/A')
                    # Only include title and content, no URLs or result numbers
                    formatted_results.append(f"{title}\n{body}")
                return "\n\n".join(formatted_results)
            else:
                return "No search results found for this query."
    except Exception as e:
        print(f"Error performing internet search: {e}")
        return f"Error performing search: {str(e)}"


# search_results = search_db("Agent_Post", "what are ai agents?")
# print(search_results)
