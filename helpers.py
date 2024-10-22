# import random
# import string
from passlib.context import CryptContext
from sqlalchemy_utils import database_exists, create_database

# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker
# from sqlalchemy.ext.declarative import declarative_base

# # Define the base class for models
# Base = declarative_base()


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