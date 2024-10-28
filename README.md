# UPISAS
Unified Python interface for self-adaptive system exemplars.

### Prerequisites 
Tested with Python 3.9.12

### Installation
In a terminal, navigate to the parent folder of the project and issue:
```
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

### Using experiment runner 

```
cd experiment-runner
git submodule update --init --recursive
pip install -r requirements.txt
cd ..
sh run.sh 
```


