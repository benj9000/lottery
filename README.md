# Lottery Ticket Evaluator

A command-line interface for evaluating German lottery tickets (LOTTO 6aus49, Spiel77, Super6)
against historical draw results.

Supported games:

- LOTTO 6aus49
- Spiel77
- Super6

I do not recommend playing the lottery, since the expected value is typically negative. Still,
people I like buy tickets – so this project was built to make evaluation easy and to confirm what we
already suspect: most of the time, we do not win.

## Installation

- Make sure to have a compatible Python version in use (compare `pyproject.toml`).
- Clone the repository, `git clone https://github.com/benj9000/lottery`.
- Enter the repository, `cd lottery`.

Then, install the Python application…

### Using `pip`

1. Create a virtual environment.
```sh
python -m venv venv
```

2. Activate the virtual environment.
```sh
source venv/bin/activate
```

3. Install the package into the virtual environment.
```sh
pip install .
```

### Using `pip` via [`uv`](https://docs.astral.sh/uv/)

1. Create a virtual environment.
```sh
uv venv venv
```

2. Activate the virtual environment.
```sh
source venv/bin/activate
```

3. Install the package into the virtual environment.
```sh
uv pip install .
```

### Using Nix

This project provides a Nix flake. With Nix flakes enabled…

- You can start a Nix shell with the CLI available.
```sh
nix shell .#lottery-ticket
```

- Or run the CLI directly, for instance.
```sh
nix run .#lottery-ticket -- --help
```

- You do not even need to clone the repository by using the GitHub repository reference.
```sh
nix shell github:benj9000/lottery
nix run github:benj9000/lottery#lottery-ticket -- --help
```

- The package can be installed like you would usually install a package from a Nix flake.

## Setup

1. Use the CLI to initialize a data directory for your lottery tickets:
```sh
lottery-ticket init /path/to/data-dir
```

2. Edit the generated `ticket.py` file in the data directory with your lottery numbers and game
preferences.

## Usage

The CLI supports evaluating your lottery tickets against specific draws or generating historical
evaluation reports.

For detailed help for any command, use the help option `--help`:

```sh
lottery-ticket --help
lottery-ticket init --help
lottery-ticket history --help
lottery-ticket evaluate --help
```
