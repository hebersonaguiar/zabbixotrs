# PyOTRS helper

build:
	python setup.py sdist bdist_wheel

clean:
	rm -rf .eggs .tox .coverage .coverage.data .cache build
	find ./ -iname "*.pyc" -delete
	find ./ -type d -iname "__pycache__" -delete

test:
	tox
	./docs_cov_build_deploy.sh

upload:
	python setup.py sdist bdist_wheel upload

