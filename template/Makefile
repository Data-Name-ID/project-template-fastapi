args = $(wordlist 2, $(words $(MAKECMDGOALS)), $(MAKECMDGOALS))

run:
	fastapi dev main.py

ruff:
	ruff check .

mypy:
	mypy .

lint: ruff mypy

current:
	alembic current

history:
	alembic history

upgrade:
	alembic upgrade head

downgrade:
	alembic downgrade $(args)

revision:
	alembic revision --autogenerate -m "$(args)"

%:
	@:
