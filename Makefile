all:
	python setup.py build
	python setup.py install

clean:
	pip uninstall geocomp -y
	rm -rf build
	rm -rf *egg-info
