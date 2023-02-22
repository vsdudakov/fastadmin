.PHONY: pre-commit-install
pre-commit-install:
	pip install pre-commit
	pre-commit install

.PHONY: pre-commit
pre-commit:
	pre-commit run --all-files
