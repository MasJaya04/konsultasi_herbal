PYTHON := .venv/bin/python3
PIP := .venv/bin/pip
MANAGE := $(PYTHON) manage.py

.PHONY: install makemigrations migrate seed shell createsuperuser collectstatic flush reset-db

install:
	python3 -m venv .venv
	$(PIP) install -r requirements.txt

makemigrations:
	$(MANAGE) makemigrations

migrate:
	$(MANAGE) migrate

seed:
	$(MANAGE) seed_mvp

shell:
	$(MANAGE) shell

createsuperuser:
	$(MANAGE) createsuperuser

collectstatic:
	$(MANAGE) collectstatic --noinput

flush:
	$(MANAGE) flush --noinput

reset-db:
	rm -f db.sqlite3
	$(MANAGE) migrate
	$(MANAGE) seed_mvp
