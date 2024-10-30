FROM python:3.10-slim

WORKDIR /code

COPY requirements.txt /code/requirements.txt

COPY .env /code/.env

RUN pip install -r /code/requirements.txt

COPY ./app /code/app

CMD [ "fastapi", "run", "app/main.py", "--port", "8000" ]