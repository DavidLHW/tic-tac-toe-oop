.PHONY: clean-pyc

help:
	@echo "    init"
	@echo "        Initializes project requirements"
	@echo "    shell"
	@echo "        Enters Python virtual environment"
	@echo "    clean-pyc"
	@echo "        Remove python artifacts."
	@echo "    test"
	@echo "        Run py.test"

init:
	@./scripts/init

shell:
	@pipenv shell

clean-pyc:
	@find . -name '*.pyc' -exec rm -f {} +
	@find . -name '*.pyo' -exec rm -f {} +
	@find . -name '*~' -exec rm -f {} +
	@find . -name '__pycache__' -exec rm -fr {} +
	@rm -rf test-results

test:
	@./scripts/test
