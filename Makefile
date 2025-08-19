# a space-separated list of directories to check
src_dirs = src
test_dirs = tests
all_dirs = $(src_dirs) $(test_dirs)
ignore_dirs = proto
githooks_dir = .githooks

generate-proto:
	poetry run python -m proto.run_codegen

call-health:
	poetry run python -m client.health

call-obj-detection:
	poetry run python -m client.object_detection

call-obj-detection-reflection:
	poetry run python -m client.object_detection_reflection

help:
	@echo "format - format Python code with isort/Black"
	@echo "lint - check style with pylint"
	@echo "mypy - run the static type checker"
	@echo "check - run all static checks and analyzers"
	@echo "commitlint - run the git hooks"
	@echo "pytest - run the tests and measure the code coverage"
	@echo "test - run the code formatter, linter, type checker, tests and coverage"
	@echo "ci-test - run the Continuous Integration (CI) pipeline (check-only)"
	@echo "clean-pyc - remove Python file artifacts"
	@echo "clean-test - remove test and coverage artifacts"

gitsetup:
	git config core.hooksPath $(githooks_dir)
	
format:
	poetry run ruff format $(all_dirs)

lint:
	poetry run ruff check $(all_dirs) --fix

pytest:
	poetry run pytest $(test_dirs)

test: format lint mypy pytest

ci-test: check
	make pytest

clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +
	find . -name '.pytest_cache' -exec rm -fr {} +
	find . -name '.mypy_cache' -exec rm -fr {} +

clean-test:
	rm -f .coverage
	rm -f coverage.xml
	rm -fr reports/
	rm -fr htmlcov

clean: clean-test clean-pyc