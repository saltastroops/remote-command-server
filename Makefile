.DEFAULT_GOAL := help

define BROWSER_PYSCRIPT
import os, webbrowser, sys

try:
        from urllib import pathname2url
except:
        from urllib.request import pathname2url

webbrowser.open("file://" + pathname2url(os.path.abspath(sys.argv[1])))
endef
export BROWSER_PYSCRIPT

define PRINT_HELP_PYSCRIPT
import re, sys

for line in sys.stdin:
        match = re.match(r'^([a-zA-Z_-]+):.*?## (.*)$$', line)
        if match:
                target, help = match.groups()
                print("%-20s %s" % (target, help))
endef
export PRINT_HELP_PYSCRIPT

BROWSER := python -c "$$BROWSER_PYSCRIPT"

help:
	@python -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST)

bandit:
	bandit -r remote_command_server

clean: ## remove test and coverage artifacts
	rm -fr .tox/
	rm -f .coverage
	rm -fr htmlcov/
	rm -fr .pytest_cache

coverage: ## check code coverage quickly with the default Python
	pytest --cov-report html
	$(BROWSER) htmlcov/index.html

black: ## format code with black
	black remote_command_server tests

flake8: ## check style with flake8
	flake8 remote_command_server tests

isort: ## sort import statements with isort
	isort remote_command_server tests

mkdocs: ## start the documentation server
	mkdocs serve

mypy: ## check types with mypy
	mypy --config-file mypy.ini .

pytest: ## run tests quickly with the default Python
	pytest

test: ## run various tests
	mypy --config-file mypy.ini .
	bandit -r remote_command_server
	flake8
	isort --check .
	black --check .
	pytest

tox: ## run tests on every Python version with tox
	tox
