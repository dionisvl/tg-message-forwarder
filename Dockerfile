FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN mkdir sessions templates
COPY src/ .
COPY templates/ templates/

CMD ["python", "app.py"]
