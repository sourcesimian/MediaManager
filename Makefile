.PHONY:

develop:
	#./setup.sh
	python3 -m venv virtualenv --without-pip
	{ \
		set -e; \
		source ./virtualenv/bin/activate; \
		wget -c -N https://bootstrap.pypa.io/get-pip.py -P virtualenv/bin/; \
		python3 ./virtualenv/bin/get-pip.py; \
		pip3 install pep8 pyflakes pylint pytest nose coverage radon; \
		python3 setup.py develop; \
	}


test:
	trial tests/test_*.py


coverage:
	coverage run tests/test_*.py
	coverage html
	open htmlcov/index.html


clean:
	rm -rf build
	rm -rf _trial*
	rm -rf htmlcov


analyse:
	find MediaManager -name '*.py' | xargs pep8 --ignore E501
	find MediaManager -name '*.py' | xargs pyflakes
	find MediaManager -name '*.py' | xargs pylint -d invalid-name -d locally-disabled -d missing-docstring -d too-few-public-methods -d protected-access


metrics:
	find MediaManager -name '*.py' | xargs radon cc -s -a -nb
	find MediaManager -name '*.py' | xargs radon mi -s


to_pypi_test:
	python setup.py register -r pypitest
	python setup.py sdist upload -r pypitest


to_pypi_live:
	python setup.py register -r pypi
	python setup.py sdist upload -r pypi


dockeret: .PHONY
	docker build \
		--build-arg http_proxy=${http_proxy} \
		--build-arg https_proxy=${https_proxy} \
		--build-arg no_proxy=${no_proxy} \
		-t sourcesimian/mediamanager:1 -f ./dockeret/Dockerfile ./
