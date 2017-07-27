# default to system python
PYTHON_VERSION ?=
PYTHON_INTERPRETER=python$(PYTHON_VERSION)
VIRTUALENV=.venv$(PYTHON_VERSION)

.PHONY: build



help:
	@echo "These are our make targets and what they do."
	@echo "All unlisted targets are internal."
	@echo ""
	@echo "  upload:       [build], but also upload to pypi using twine"


$(VIRTUALENV): setup.py
	virtualenv --python $(PYTHON_INTERPRETER) $(VIRTUALENV)
	$(VIRTUALENV)/bin/python setup.py develop
	# explicit touch to ensure good update time relative to setup.py
	touch $(VIRTUALENV)

build: $(VIRTUALENV)
	$(VIRTUALENV)/bin/python setup.py sdist bdist_egg


$(VIRTUALENV)/bin/twine: $(VIRTUALENV)
	$(VIRTUALENV)/bin/pip install -U twine==1.9.1
upload: $(VIRTUALENV)/bin/twine build
	$(VIRTUALENV)/bin/twine upload dist/*
