help:
	@cat ./Makefile | grep -E '^[a-zA-Z_-]+:.*?## .*$$' | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

install: ## Install dependencies
	pip install . -r requirements.txt

dev: ## Install dependencies for development
	pip install -e .
	pip install -r requirements-dev.txt

test: ## Run tests
	pytest tests --doctest-modules --cov=src

lint: ## Check code style
	flake8 src --count --select=E9,F63,F7,F82 --show-source --statistics
	flake8 src --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics

fix: ## Format code
	black -l79 src

release: ## Create a release: make release v=0.1.0
	@if [ -z "$(v)" ]; then echo "Missing version number:\nUse: make release v=0.1"; exit 1; fi
	@sed -i -e "s/version = \".*\"/version = \"$(v)\"/" pyproject.toml
	@sed -i -e "s/__version__ = \".*\"/__version__ = \"$(v)\"/" src/i3_agenda/__init__.py
	@sed -i -e "s/archive\/[0-9]\+\.[0-9]\+\(\.[0-9]\+\)\?\.tar\.gz/archive\/$(v).tar.gz/" pyproject.toml
	@git diff
	@# ideally we would use the following
	@# git add pyproject.toml src/i3_agenda/__init__.py
	@# git commit -m "Release v$(v)"
	@# git tag -a v$(v) -m "Release v$(v)"
	@# git push
	@# git push --tags
