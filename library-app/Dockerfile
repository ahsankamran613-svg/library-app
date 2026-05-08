FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir flask flask-sqlalchemy werkzeug

COPY . .

RUN python -c "from app import app, db; app.app_context().__enter__(); db.create_all()"

EXPOSE 5000

CMD ["python", "app.py"]
