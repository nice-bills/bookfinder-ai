FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/
COPY data/ ./data/
COPY scripts/ ./scripts/

ENV PYTHONPATH=/app

CMD ["python", "-m", "streamlit", "run", "src/book_recommender/apps/main_app.py"]