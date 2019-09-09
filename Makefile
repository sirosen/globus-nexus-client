# default to system python
PYTHON_VERSION ?=
PYTHON_INTERPRETER=python$(PYTHON_VERSION)
VIRTUALENV=.venv$(PYTHON_VERSION)

VERSION=$(shell grep '^__version__' globus_nexus_client/version.py | cut -d '"' -f2)


.PHONY: showvars
showvars:
	@echo "VERSION=$(VERSION)"


$(VIRTUALENV):
	virtualenv --python $(PYTHON_INTERPRETER) $(VIRTUALENV)
	$(VIRTUALENV)/bin/python setup.py develop
	$(VIRTUALENV)/bin/pip install -U twine


.PHONY: release
release: $(VIRTUALENV)
	git tag -s "$(VERSION)" -m "v$(VERSION)"
	rm -rf dist
	$(VIRTUALENV)/bin/python setup.py sdist bdist_wheel
	$(VIRTUALENV)/bin/twine upload dist/*
