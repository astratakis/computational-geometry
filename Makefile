all:
	python setup.py build
	python setup.py install

clean:
	pip uninstall compgeo
	rm -rf build
	rm -rf *egg-info
