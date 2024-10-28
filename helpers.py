# import random
# import string
from passlib.context import CryptContext
from sqlalchemy_utils import database_exists, create_database
from sentence_transformers import SentenceTransformer
import math
import os
from dotenv import load_dotenv
from elasticsearch import Elasticsearch, helpers
# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker
# from sqlalchemy.ext.declarative import declarative_base

# # Define the base class for models
# Base = declarative_base()


# SETTING UP ELASTICSEARCH
load_dotenv("config.env")
ELASTICSEARCH_INDEX = "user_uploaded_docs"
ELASTICSEARCH_HOST = os.getenv("ELASTICSEARCH_HOST", "localhost")
ELASTICSEARCH_PORT = os.getenv("ELASTICSEARCH_PORT", "9200")

elastic_client = Elasticsearch("http://localhost:9200")



pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str):
    return pwd_context.hash(password)

async def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)



def file_extension_is_allowed(filename: str) -> bool:
    ALLOWED_EXTENSIONS = ['pdf', 'docx', 'txt']
    return filename.split('.')[-1] in ALLOWED_EXTENSIONS

def get_file_extension(filename: str) -> str:
    return filename.split('.')[-1]

def generate_vectors(text):
    model = SentenceTransformer("all-MiniLM-L6-v2")
    model.max_seq_length = 512
    embeddings = model.encode([text])
    return embeddings

def clean_text(text):
    cleaned_text = ''.join(text.split('\n'))
    cleaned_text = cleaned_text.strip()
    return cleaned_text

def splitting(text, split_strategy='paragraphs'):
    if split_strategy == "sentences":
        splitted_text = text.split(". ")
    elif split_strategy == "paragraphs":
        splitted_text = text.split("\n")
    splitted_text = [clean_text(i) for i in splitted_text]
    return splitted_text


def construct_documents(splitted_text):
    """we need to fit max number of words in a elastic-search document. 
    since as per sbert docs:
    'A common value for BERT-based models are 512 tokens, which corresponds to about 300-400 words (for English)'.
    we would try to group together the splitted text so that one document can range between 300-400.
    """
    sbert_word_limit = 300
    documents = []
    for text in splitted_text:
        if len(documents) == 0:
            documents.append(text)
        
        text_split = text.split()
        last_document = documents[-1]
        last_document_split = documents[-1].split()
        if len(text_split) > sbert_word_limit:
            # cut off the text at last full stop before sbert word limit
            possible_parts = math.ceil(len(text_split)/sbert_word_limit)
            chunking_first_index = 0
            chunking_last_index = sbert_word_limit
            for _ in range(possible_parts):
                new_document = " ".join(text_split[chunking_first_index:chunking_last_index])
                documents.append(new_document)
                chunking_first_index = chunking_last_index
                chunking_last_index = chunking_last_index + sbert_word_limit
            continue
        if len(last_document_split) + len(text_split) <= sbert_word_limit:
            last_document = last_document + " " + text
            documents[-1] = last_document
        else:
            documents.append(text)
    # print(documents)
    return documents


def create_index_if_not_exists(index_name="user_uploaded_docs"):
    # Check if the index already exists
    if not elastic_client.indices.exists(index=index_name):
        # Define the settings and mappings for the index
        settings = {
            "mappings": {
                "properties": {
                    "text": {
                        "type": "text"
                    },
                    "vector": {
                        "type": "dense_vector",
                        "dims": 384,  # Replace with the dimensionality of your vectors
                        "similarity": "cosine",
                        "index": True # Enable indexing for the vector field
                    }
                }
            }
        }
        
        # Create the index with the specified settings and mappings
        elastic_client.indices.create(index=index_name, body=settings)
        print(f"Index '{index_name}' created.")
    else:
        print(f"Index '{index_name}' already exists.")

# Call the function to create the index if it doesn't exist

from elasticsearch.helpers import BulkIndexError
    
def index_documents(documents, index_name="user_uploaded_docs"):
    print(elastic_client.info(), "ELASTIC CLIENT")
    actions = []
    for document in documents:
        # Generate the vector embeddings for the document's text
        vector = generate_vectors(document)[0]
        print(vector)
        actions.append({
            "_index": index_name,
            "_source": {
                "text": document,
                "vector": vector.tolist()
            }
        })

    try:
        helpers.bulk(elastic_client, actions)
        print("Documents indexed successfully.")
    except BulkIndexError as e:
        print("Bulk index error:", e)
        for error in e.errors:
            print(error)

# Delete the existing index
def delete_index(index_name="user_uploaded_docs"):
    if elastic_client.indices.exists(index=index_name):
        elastic_client.indices.delete(index=index_name)
        print(f"Index '{index_name}' deleted.")
def process_text(args):
    text = args["text"]
    split_strategy = args["split_strategy"]
    splitted_text = splitting(text=text, split_strategy=split_strategy)
    documents = construct_documents(splitted_text=splitted_text)
    # delete_index()
    create_index_if_not_exists()
    index_documents(documents, ELASTICSEARCH_INDEX)
    print("OK")

    


    



# def generate_random_string(length=10):
#     return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

# Function to dynamically create a new database and generate tables
# async def create_user_database(POSTGRES_CONN_DICT, user_first_name, user_last_name):
#     random_string = generate_random_string()
#     new_db_name = f"{user_first_name}_{user_last_name}_{random_string}"

#     # Construct the new database URL
#     new_db_url = f"postgresql://{POSTGRES_CONN_DICT['user']}:{POSTGRES_CONN_DICT['password']}@{POSTGRES_CONN_DICT['host']}/{new_db_name}"

#     # Create the new database
#     if not database_exists(new_db_url):
#         create_database(new_db_url)  # This creates the new database

#     # Create a new engine for the new database
#     engine = create_engine(new_db_url)
    
#     # Create the tables in the new database
#     Base.metadata.create_all([])  # Base includes Table1, Table2, Table3

#     return new_db_name, engine




