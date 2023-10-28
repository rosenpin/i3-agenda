install:
	pip install . -r requirements.txt

dev:
	pip install -e .
	pip install -r requirements-dev.txt

test:
	pytest tests --junitxml=../junit/test-results.xml
	pytest tests --doctest-modules --cov=. --cov-report=xml:../coverage/cov.xml --cov-report=html:../coverage/

lint:
	flake8 src --count --select=E9,F63,F7,F82 --show-source --statistics
	flake8 src --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics

fix:
	black -l79 src
