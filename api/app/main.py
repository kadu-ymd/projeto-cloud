from fastapi import FastAPI, HTTPException, Depends, status
from sqlmodel import SQLModel, Session, create_engine, Field, select
from typing import Annotated
from os import getenv
from dotenv import load_dotenv
from hashlib import sha256
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
import jwt
from .utils import get_videos

load_dotenv()

class UserBase(SQLModel):
    email: str
    password: str

class User(UserBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str

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

class UserLogin(UserBase):

    model_config = {
        'json_schema_extra': {
            'examples': [
                {
                    'email': 'joao@gmail.com',
                    'password': 's3nh4s3cr3t4'
                }
            ]
        }
    }

DATABASE_URL = f"postgresql+psycopg2://{getenv('DB_USERNAME')}:{getenv('DB_PASSWORD')}@{getenv('DB_HOST')}/{getenv('DB_NAME')}"

SECRET_KEY = f"{getenv('SECRET_KEY')}"

HASH_ALGORITHM = "HS256"

API_KEY = f"{getenv('API_KEY')}"

API_URL = "https://www.googleapis.com/youtube/v3/videos"

print(SECRET_KEY, API_KEY)

engine = create_engine(DATABASE_URL)

SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

def hash_password(password: str) -> str:
    return sha256(password.encode("utf-8")).hexdigest()

def verify_token(jwt_token: str):
    is_valid: bool = False
    
    try:
        payload = jwt.decode(jwt_token, SECRET_KEY, HASH_ALGORITHM)
        print(payload)
    except:
        payload = None

    if payload:
        is_valid = True

    return is_valid

SessionDep = Annotated[Session, Depends(get_session)]

app = FastAPI()

security = HTTPBearer()

@app.post("/registrar")
def registrar(user: User, session: SessionDep):

    results = session.exec(select(User))

    for user_email in results:
        if user_email.email == user.email:
            raise HTTPException(status.HTTP_409_CONFLICT, detail="E-mail já está cadastrado.")

    hashed_pw = sha256(user.password.encode("utf-8")).hexdigest()
    new_user = User(name=user.name, 
                    email=user.email, 
                    password=hashed_pw)

    session.add(new_user)
    session.commit()
    session.refresh(new_user)

    return jwt.encode({"email": user.email}, SECRET_KEY, algorithm=HASH_ALGORITHM)

@app.post("/login")
def login(user_login: UserLogin, session: SessionDep):

    results = session.exec(select(User))

    for user in results:
        if (user_login.email == user.email):
            if (hash_password(user_login.password) == user.password):
                return jwt.encode({"name": user.name}, SECRET_KEY, algorithm=HASH_ALGORITHM)
            else:
                raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="E-mail e/ou senha inválidos.")

    raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="E-mail não encontrado.")

@app.get("/consultar")
def consultar(credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)]):
    print(credentials.scheme, credentials.credentials)

    if credentials.scheme != "Bearer":
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="Método de autenticação inválido")
    elif not verify_token(credentials.credentials):
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="Token inválido!")
    
    return get_videos(api_key=API_KEY, api_url=API_URL)