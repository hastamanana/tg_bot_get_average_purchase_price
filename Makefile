# Commands for working with a virtual environment
venv:
	@if [ -z "$(version)" ]; then \
		echo "Usage: make venv version=<python_version>"; \
		exit 1; \
	fi
	python$(version) -m venv .venv
	@echo "Virtual environment created for Python $(version)"

# Poetry commands
poetry-extra-plugins:
	poetry self add poetry-plugin-shell poetry-plugin-export

poetry-start:
	poetry shell

# Linting and formatting
dev-pep8:
	black .
	isort .

dev-lint:
	flake8 .
	mypy .

dev-full:
	make dev-pep8 && make dev-lint

# Other utils
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .mypy_cache
	rm -rf .pytest_cache
	@echo "Cleaned up temporary files."

project_tree:
	tree -a -I ".venv|.git|.vscode|.idea|node_modules|__pycache__"
