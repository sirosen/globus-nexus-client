VERSION=$(shell grep '^__version__' globus_nexus_client/version.py | cut -d '"' -f2)


.PHONY: showvars
showvars:
	@echo "VERSION=$(VERSION)"


.PHONY: localdev
localdev: .venv
.venv:
	virtualenv --python=python3 .venv
	.venv/bin/python setup.py develop
	.venv/bin/pip install -U twine


.PHONY: release
release: .venv
	git tag -s "$(VERSION)" -m "v$(VERSION)"
	rm -rf dist
	.venv/bin/python setup.py sdist bdist_wheel
	.venv/bin/twine upload dist/*
