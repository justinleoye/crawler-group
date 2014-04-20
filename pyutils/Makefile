.PHONY: clean-pyc build

all: build

build:
	python setup.py sdist

install:
	python setup.py install

clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +

#upload_to_pypi:
#	python setup.py register
#	python setup.py sdist upload
