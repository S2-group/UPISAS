# UPISAS
Unified Python interface for self-adaptive system exemplars.

### Prerequisites 
Tested with Python 3.9.12

Ensure you have Poetry for python installed. See [https://python-poetry.org/docs/#installation](https://python-poetry.org/docs/#installing-with-the-official-installer) for instructions. Poetry manages the creation and activation of a virtual environment for the project, alongside creating a lockfile for the project's dependencies.

### Installation
In a terminal, navigate to the parent folder of the project and issue:
```
poetry install
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


