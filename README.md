# Tic Tac Toe

A simple Tic Tac Toe game written in a Test-Driven Development method, using object-oriented principles with relevant error handling.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for interaction, development and testing purposes.

### Prerequisites
For development:

* pipenv
* python 3.8
* make (GNU or cygwin)

### Setting up the project

```bash
# Clone Repository
git clone https://github.com/DavidLHW/tic-tac-toe-oop.git
```

```bash
# Change directory
cd tic-tac-toe-oop
```

Initialize the repository:

```bash
# Bring up pipenv shell and install all dependencies
make init
```

Alternatively, you can initialize with:

```bash
# Setup pipenv
pipenv shell

# Install all dependencies
pipenv install -d
```

### Playing the Game

To start interacting with the CLI, after [setting up](#setting-up-the-project) the project, run the following:

```bash
# Run all tests
python3 app.py
```

### Running Tests

To run all tests:

```bash
# Runs all tests
make test
```

Alternatively, to run all tests by calling shellscript directly (if make is not installed correctly):

```bash
# Runs all tests
./scripts/test
```

Alternatively, to run all tests using pytest CLI:

See all possible flags for [pytest CLI](https://docs.pytest.org/en/6.2.x/reference.html#command-line-flags)

```bash
# Runs all tests
pytest -s -v
```

