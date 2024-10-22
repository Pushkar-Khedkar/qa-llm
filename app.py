from elasticsearch import Elasticsearch
import mlflow
import os
from transformers import pipeline
from fastapi import FastAPI, File, UploadFile, HTTPException, Depends, Request
from text_processor import extract_text_from_docx, extract_text_from_pdf
from dotenv import load_dotenv
from src.pydentic_models import *
from src.models import *
from sqlalchemy.orm import Session
from db_manager import get_elasticsearch_connection, get_postgresql_connection
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import traceback
from sqlalchemy import exc as sqlexc
from helpers import *

app = FastAPI()
load_dotenv("config.env")


# Get the connection details from environment variables 
ELASTICSEARCH_HOST = os.getenv("ELASTICSEARCH_HOST", "localhost")
ELASTICSEARCH_PORT = os.getenv("ELASTICSEARCH_PORT", "9200")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgres")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
POSTGRES_DB = os.getenv("POSTGRES_DB")  
POSTGRES_CONN_DICT = {"host":POSTGRES_HOST, "port":POSTGRES_PORT, "user":POSTGRES_USER, "password":POSTGRES_PASSWORD, "db_name":POSTGRES_DB}
POSTGRES_DB_URI = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"



@app.exception_handler(RequestValidationError) # occurs before api gets hit
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(status_code=422,content={"success": False,"message": "Validation Error","errors": [{}]})

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(status_code=exc.status_code,content=ErrorHandler(success=False,message=exc.detail).model_dump())

async def integrity_error():
    return JSONResponse(status_code=400,content=ErrorHandler(success=False,message="Duplicated entry").model_dump())

# @app.exception_handler(Exception)
async def general_exception_handler(e: Exception):
    tb = traceback.extract_tb(e.__traceback__)
    # Extract the last entry in the traceback which corresponds to the error location
    last_call = tb[-1] if tb else None
    line_number = last_call.lineno if last_call else "unknown line"
    filename = last_call.filename if last_call else "unknown file"
    error = f"Error: {str(e)}, Line: {line_number}, Filename:{filename}"
    return JSONResponse(status_code=500, content=ErrorHandler(success=False,message=str(error)).model_dump())


@app.post("/uploadfile")
async def upload_file(file: UploadFile = File(...)):
    # Check file type
    if not file_extension_is_allowed(file.filename):
        raise HTTPException(status_code=400, detail="File type not allowed. Only PDF, DOCX, and TXT files are accepted.")
    
    file_extension = get_file_extension(file.filename)
    file_bytes = await file.read()
    if file_extension == "pdf":
        extracted_text = extract_text_from_pdf(file_bytes)
    elif file_extension == "docx":
        extracted_text = extract_text_from_docx(file_bytes)
    
    



@app.post("/signup")
async def signup(user_create:UserCreate, db: Session = Depends(lambda: next(get_postgresql_connection(**POSTGRES_CONN_DICT)))):
    try:
        hashed_password = get_password_hash(user_create.password)
        user_create = user_create.model_dump()
        user_create["password"] = hashed_password
        db_user = User(**user_create)
        db.add(db_user)
        try:
            db.commit()
        except sqlexc.IntegrityError:
            response = await integrity_error()
            return response
        db.refresh(db_user)
        response = SuccessHandler(success=True, message="User created successfully", data=user_create)
    except Exception as e:
        response = await general_exception_handler(e)
    return response
    

# authenticate_user
@app.post("/login")
async def login(user_login:UserCreds, db:Session = Depends(lambda: next(get_postgresql_connection(**POSTGRES_CONN_DICT)))):
    # user = authenticate_user(user_login) 
    pass







