.PHONY: clean-pyc build test

test:
	tox

all: build install

build:
	python setup.py sdist

install:
	python setup.py install

dist-without-source:
	python setup.py bdist_egg --exclude-source-files

clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +

#upload_to_pypi:
#	python setup.py register
#	python setup.py sdist upload
