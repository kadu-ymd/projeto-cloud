from fastapi import FastAPI, Depends
from sqlmodel import SQLModel, Session, create_engine, Field
from typing import Annotated
from os import getenv
from dotenv import load_dotenv
from hashlib import sha256
import jwt

load_dotenv()

class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str   
    email: str
    password: str

    model_config = {
        'json_schema_extra': {
            'examples': [
                {
                    'name': 'João',
                    'email': 'joao@gmail.com',
                    'password': 's3nh4s3cr3t4'
                }
            ]
        }
    }

DATABASE_URL = f"postgresql+psycopg2://{getenv('DB_USERNAME')}:{getenv('DB_PASSWORD')}@{getenv('DB_HOST')}/{getenv('DB_NAME')}"

SECRET_KEY = f"{getenv('SECRET_KEY')}"

engine = create_engine(DATABASE_URL)

SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post("/registrar")
def registrar(user: User, session: SessionDep):
    hashed_pw = sha256(user.password.encode("utf-8")).hexdigest()
    new_user = User(name=user.name, 
                    email=user.email, 
                    password=hashed_pw)
    
    to_encode = new_user.model_dump()

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm="HS256")

    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    return encoded_jwt

@app.get("/user/{id}")
def retrieve_user(id: int, session: SessionDep):
    return session.get(User, id)