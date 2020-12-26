.PHONY: clean-pyc
clean-pyc:
	@echo "Removing pyc files"
	@find . -name "*.pyc" -exec rm -f {} \;
	@find . -name "*.pyo" -exec rm -f {} \;

.PHONY: clean-build
clean-build:
	@echo "Removing build"
	@rm -f -R build/
	@rm -f -R dist/
	@rm -f -R *.egg-info

.PHONY: release
release: build upload clean-build

.PHONY: build
build: clean-build
	@pip install twine wheel
	@python setup.py sdist
	@python setup.py bdist_wheel --universal

.PHONY: upload
upload:
	@twine upload dist/*

.PHONY: run-example
run-example:
	@python setup.py install
	@uvicorn examples.multi-bot-router.main:app --reload