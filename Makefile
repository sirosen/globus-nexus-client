VERSION=$(shell grep '^version =' setup.cfg | cut -d '=' -f2 | tr -d ' ')


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
	rm -rf dist build
	.venv/bin/python setup.py sdist bdist_wheel
	.venv/bin/twine upload dist/*
