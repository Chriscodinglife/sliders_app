FROM python:3.10.0

WORKDIR /app

COPY requirements.txt requirements.txt
COPY slider.py slider.py

RUN pip3 install -r requirements.txt

COPY main.py main.py

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5000"]