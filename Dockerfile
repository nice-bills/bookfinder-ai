FROM python:3.10-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ ./src/
COPY data/ ./data/
COPY scripts/ ./scripts/

# Set PYTHONPATH
ENV PYTHONPATH=/app

# Default command (override in docker-compose)
CMD ["python", "-m", "streamlit", "run", "src/book_recommender/apps/main_app.py"]