.PHONY: run


OS := $(shell uname)
ifeq ($(OS), Linux)
  CONDAURL := "https://repo.continuum.io/miniconda/Miniconda-latest-Linux-x86_64.sh"
else ifeq ($(OS), Darwin)
  CONDAURL := "https://repo.continuum.io/miniconda/Miniconda-latest-MacOSX-x86_64.sh"
endif

run: miniconda
	miniconda/bin/python server.py

miniconda:
	curl $(CONDAURL) -o miniconda.sh
	chmod a+x miniconda.sh
	./miniconda.sh -b -p ./miniconda
	rm miniconda.sh
	miniconda/bin/conda install -y -c https://conda.anaconda.org/menpo opencv
	miniconda/bin/pip install Twisted autobahn
