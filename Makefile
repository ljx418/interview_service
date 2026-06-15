.PHONY: dev api test

api:
	uvicorn services.api.main:app --reload --host 127.0.0.1 --port 8000

dev: api

test:
	pytest

