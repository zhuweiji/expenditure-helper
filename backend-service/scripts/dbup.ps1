alembic check; if ($LASTEXITCODE -ne 0) { alembic revision --autogenerate -m "Add new updates" }

alembic upgrade head
uv run python -m src.main