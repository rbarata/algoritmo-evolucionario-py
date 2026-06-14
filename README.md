# Mesh Evolution Algorithm - Python Port

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Overview

This project is a Python port of the original Perl-based evolutionary algorithm for optimizing mesh deformation. The algorithm uses genetic algorithms to optimize a mesh grid based on conductivity patterns and geometric constraints.

### What it does

- Optimizes mesh grid deformation using evolutionary algorithms
- Computes coordinate systems based on conductivity matrices
- Solves tridiagonal and Gaussian linear systems
- Calculates mesh quality metrics (fitness functions)
- Supports various fitness evaluation strategies

## Project Status

🚧 **In Development**: Phase 2 - Project Structure Setup Complete

## Installation

### Prerequisites

- Python 3.9 or higher
- pip or conda

### Basic Installation

```bash
# Clone the repository
git clone https://github.com/rbarata/algoritmo-evolucionario-py.git
cd algoritmo-evolucionario-py

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/macOS
# or
venv\\Scripts\\activate  # Windows

# Install dependencies
pip install -r requirements.txt
```

### Development Installation

```bash
pip install -r requirements-dev.txt
```

## Quick Start

```python
from mesh_evolution.main import main

# Run the algorithm with default parameters
main()
```

## Project Structure

```
algorithmo-evolucionario-py/
├── pyproject.toml                 # Project metadata and dependencies
├── requirements.txt               # Core dependencies
├── requirements-dev.txt           # Development dependencies
├── README.md                      # This file
├── .gitignore                     # Git ignore patterns
├── .github/
│   └── workflows/
│       └── tests.yml              # CI/CD workflow
├── src/
│   └── mesh_evolution/
│       ├── __init__.py            # Package initialization
│       ├── main.py                # Main entry point
│       ├── core/
│       │   ├── __init__.py
│       │   ├── automato.py       # Evolutionary algorithm
│       │   ├── mesh.py           # Mesh calculations
│       │   ├── util.py           # Utilities
│       │   └── geometry.py       # Geometric primitives
│       ├── algorithms/
│       │   ├── __init__.py
│       │   ├── matrix.py         # Gaussian elimination
│       │   ├── tdma.py           # Tridiagonal solver
│       │   └── solvers.py        # Numerical solvers
│       └── data/
│           ├── __init__.py
│           └── loaders.py        # Data file handling
├── tests/
│   ├── __init__.py
│   ├── test_geometry.py
│   ├── test_matrix.py
│   ├── test_mesh.py
│   ├── test_automato.py
│   └── test_numerical_accuracy.py
├── scripts/
│   ├── profile_algorithm.py
│   └── generate_reference_data.py
├── data/
│   ├── filme.dat
│   ├── imagem.dat
│   ├── perfil.dat
│   └── info.txt
└── docs/
    ├── MIGRATION_PLAN.md
    ├── API.md
    ├── ALGORITHM.md
    └── DEVELOPMENT.md
```

## Module Descriptions

### Core Modules

#### `geometry.py`
Geometric primitives and calculations:
- `Point`: 2D point representation
- `Quadrilateral`: 4-point polygon with area calculation

#### `mesh.py`
Mesh deformation calculations:
- `MeshCalculator`: Main class for mesh operations
- Calculate K matrices from conductivity
- Compute coordinate systems
- Evaluate fitness metrics

#### `automato.py`
Evolutionary algorithm implementation:
- `Individual`: Population member representation
- `Population`: Population management
- `EvolutionaryAlgorithm`: Main EA orchestrator

#### `util.py`
Utility functions:
- `max_value()`, `min_value()`: Min/max operations
- `print_title()`: Formatted output

### Algorithm Modules

#### `matrix.py`
Matrix operations and solvers:
- `MatrixSolver`: Gaussian elimination with partial pivoting
- Error handling and numerical stability

#### `tdma.py`
Tridiagonal system solver:
- `solve_tdma()`: Thomas Algorithm implementation
- Efficient O(n) tridiagonal system solving

#### `solvers.py`
Numerical solver utilities and abstractions

### Data Handling

#### `loaders.py`
Data file I/O:
- Load/save matrix data
- Parse metadata
- Handle various data formats

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=src/mesh_evolution

# Run specific test file
pytest tests/test_geometry.py

# Run tests matching pattern
pytest -k "test_area"
```

### Code Quality

```bash
# Format code
black src/ tests/ scripts/

# Sort imports
isort src/ tests/ scripts/

# Lint code
flake8 src/ tests/ scripts/

# Type checking
mypy src/
```

### Performance Profiling

```bash
python scripts/profile_algorithm.py
```

## License

MIT License

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and code quality checks
5. Submit a pull request

## Author

**Rui Barata** - Original Perl version and Python migration
