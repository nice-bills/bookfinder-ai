@echo off
set PYTHONPATH=%CD%\src
call .venv\Scripts\activate.bat
uv run streamlit run -m book_recommender.apps.analytics_app --server.port=8502