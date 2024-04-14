# UPISAS
Unified Python interface for self-adaptive system exemplars.

Documentation on the experiment runner can be found in [./runner/README.md](./runner/README.md)

### Prerequisites 
Tested with Python 3.9.12


### Installation - Poetry

Ensure you have Poetry for python installed. See [https://python-poetry.org/docs/#installation](https://python-poetry.org/docs/#installing-with-the-official-installer) for instructions. Poetry manages the creation and activation of a virtual environment for the project, alongside creating a lockfile for the project's dependencies.

In a terminal, navigate to the parent folder of the project and issue:
```
poetry install
```

### Installation - Pip

In a terminal, navigate to the parent folder of the project and issue:
```
virtualenv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Run unit tests
In a terminal, navigate to the parent folder of the project and issue:
```
python -m UPISAS.tests.upisas.test_exemplar
python -m UPISAS.tests.upisas.test_strategy
python -m UPISAS.tests.swim.test_swim_interface
```
### Run
In a terminal, navigate to the parent folder of the project and issue:
```
python run.py
```


