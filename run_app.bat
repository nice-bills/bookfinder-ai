@echo off
set PYTHONPATH=%CD%\src
call .venv\Scripts\activate.bat
uv run streamlit run -m book_recommender.apps.main_app