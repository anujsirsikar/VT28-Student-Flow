Uses ortools, which is not supported by python 3.12 or earlier.
We are running this project in a virtual environment in python 3.10.

To set up on Mac (need homebrew installed)

brew install python@3.10

python 3.10 -m venv ortools_env
source ortools_env/bin/activate

pip install ortools


To activate environmnent on Mac:

source ortools-env/bin/activate


To deactivate the environment (allowing new python again)

deactivate
