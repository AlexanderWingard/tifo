
miniconda:
	curl -O https://repo.continuum.io/miniconda/Miniconda-latest-MacOSX-x86_64.sh
	sh Miniconda-latest-MacOSX-x86_64.sh -b -p ./miniconda
	rm Miniconda-latest-MacOSX-x86_64.sh
	miniconda/bin/conda install -c https://conda.anaconda.org/menpo opencv
	miniconda/bin/pip install Twisted
