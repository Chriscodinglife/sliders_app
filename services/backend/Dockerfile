FROM python:3.10.0

WORKDIR /app

COPY requirements.txt requirements.txt
COPY slider.py slider.py
COPY main.py main.py
COPY client_secret.json client_secret.json

RUN pip3 install -r requirements.txt

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5000"]