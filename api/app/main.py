from fastapi import FastAPI, HTTPException, Depends, status
from sqlmodel import SQLModel, Session, create_engine, Field, select
from typing import Annotated
from os import getenv
from dotenv import load_dotenv
from hashlib import sha256
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
import jwt
from .utils import *
from .models import *

load_dotenv()

DATABASE_URL = f"postgresql+psycopg2://{getenv('DB_USERNAME')}:{getenv('DB_PASSWORD')}@{getenv('DB_HOST')}/{getenv('DB_NAME')}"

SECRET_KEY = f"{getenv('SECRET_KEY')}"

HASH_ALGORITHM = "HS256"

KEY_API = f"{getenv('KEY_API')}"

API_URL = "https://www.googleapis.com/youtube/v3/videos"

engine = create_engine(DATABASE_URL)

SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]

app = FastAPI(
    title="Projeto - Computação em Nuvem 2024.2",
    description="Esta API gerencia e trata dados relativos ao registro e à autenticação de um usuário em um banco de dados.",
    openapi_tags=Tags.__metadata__,
    tags=[Tags.auth]
)

security = HTTPBearer()

@app.post("/registrar",
    status_code=status.HTTP_201_CREATED,
    tags=[Tags.auth],
    summary="Realiza o cadastro de um usuário.",
    responses={
        201: {
            "content": {
                "application/json": {
                    "example": {
                        "token": "tokenJWT"
                    }
                }
            }
        },
        409: {
            "content": {
                "application/json": {
                    "example": {
                        "detail": "E-mail já está cadastrado."
                    }
                }
            }
        }
    }
)
def registrar(user: User, session: SessionDep) -> dict[str, str]:
    '''
    Realiza o cadastro de um usuário na base de dados. São necessários os seguintes dados:

    - **usuário** (*name*): nome do usuário;
    - **e-mail** (*email*): e-mail do usuário;
    - **senha** (*password*): senha a ser cadastrada;
    '''
    
    results = session.exec(select(User))

    for user_email in results:
        if user_email.email == user.email:
            raise HTTPException(status.HTTP_409_CONFLICT, detail="E-mail já está cadastrado.")

    hashed_pw = hash_password(user.password)
    new_user = User(name=user.name, 
                    email=user.email, 
                    password=hashed_pw)

    session.add(new_user)
    session.commit()
    session.refresh(new_user)

    return {"token": jwt_encode({"email": user.email}, SECRET_KEY, HASH_ALGORITHM)}

@app.post("/login",
    status_code=status.HTTP_200_OK,
    tags=[Tags.auth],
    summary="Realiza o login do usuário.",
    responses={
        200: {
            "content": {
                "application/json": {
                    "example": {
                        "token": "tokenJWT"
                    }
                }
            }
        },
        401: {
            "content": {
                "application/json": {
                    "examples": {
                        "Dados inválidos": {
                            "value": {
                                "detail": "E-mail e/ou senha inválidos."
                            }
                        },
                        "E-mail não existe": {
                            "value": {
                                "detail": "E-mail não encontrado."
                            }
                        }
                    }
                }
            }
        }
    }
)
def login(user_login: UserLogin, session: SessionDep) -> dict[str, str]:
    '''
    Realiza o log-in do usuário no sistema. Requer:

    - **e-mail** (*email*): e-mail do usuário;
    - **senha** (*password*): senha do usuário;
    '''

    results = session.exec(select(User))

    for user in results:
        if (user_login.email == user.email):
            if (hash_password(user_login.password) == user.password):
                return {"token": jwt_encode({"name": user.name}, SECRET_KEY, HASH_ALGORITHM)}
            else:
                raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="E-mail e/ou senha inválidos.")

    raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="E-mail não encontrado.")

@app.get("/consultar",
    status_code=status.HTTP_200_OK,
    tags=[Tags.auth],
    summary="Utiliza o token JWT gerado no login para fazer uma autenticação do tipo Bearer.",
    responses={
        200: {
            "content": {
                "application/json": {
                    "example": {
                        "title": "Título do vídeo",
                        "video_id": "ID do vídeo",
                        "description": "Descrição do vídeo",
                        "n_views": "Número de visualizações"
                    }
                }
            }
        },
        403: {
            "content": {
                "application/json": {
                    "examples": {
                        "Token inválido": {
                            "value": {
                                "detail": "Token inválido."
                            }
                        },
                        "Método incorreto": {
                            "value": {
                                "detail": "Método de autenticação inválido."
                            }
                        }
                    }
                }
            }
        }
    }
)
def consultar(credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)]) -> dict[str, str | None]:
    '''
    Esse *endpoint* serve para re-autenticar o usuário utilizando o ***token* JWT** retornado pela *endpoint* de `login`. O *token* é fornecido no cabeçalho utilizando o método `Bearer` para autenticação.
    '''
    
    if credentials.scheme != "Bearer":
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="Método de autenticação inválido.")
    elif not verify_token(credentials.credentials, SECRET_KEY, HASH_ALGORITHM):
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="Token inválido!")
    
    return get_videos(api_key=KEY_API, api_url=API_URL)