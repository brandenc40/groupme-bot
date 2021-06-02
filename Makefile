VENV := venv

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
build: venv clean-build
	@./venv/bin/pip3 install twine wheel
	@./venv/bin/python3 setup.py sdist
	@./venv/bin/python3 setup.py bdist_wheel --universal

.PHONY: upload
upload: venv
	@./venv/bin/twine upload dist/*

.PHONY: run-example
run-example: venv
	@./venv/bin/python3 setup.py install
	@./venv/bin/uvicorn examples.multi-bot-router.main:app --workers=1

$(VENV)/bin/activate: requirements.txt
	python3 -m venv $(VENV)
	./$(VENV)/bin/pip install -r requirements.txt

# venv is a shortcut target
venv: $(VENV)/bin/activate
