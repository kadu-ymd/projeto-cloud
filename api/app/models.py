from sqlmodel import SQLModel, Field

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
                    'name': 'secret_',
                    'email': 'usuario_secreto@gmail.com',
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
                    'email': 'usuario_secreto@gmail.com',
                    'password': 's3nh4s3cr3t4'
                }
            ]
        }
    }