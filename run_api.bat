@echo off
set PYTHONPATH=%CD%\src
call .venv\Scripts\activate.bat
uv run uvicorn book_recommender.api.main:app --host 0.0.0.0 --port 8000 --reload