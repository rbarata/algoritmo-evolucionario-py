# Algoritmo Evolutivo para Optimização de Malhas 2D

Python port of a 1998 Perl research project. Uses an evolutionary algorithm to optimise the node positions of a 2D computational mesh — relevant for finite element methods (FEM) and computational fluid dynamics (CFD), where mesh quality directly affects simulation accuracy.

## What it does

Given a 2D domain with material properties (matrix `E`), the algorithm finds node positions that minimise cell area variance, producing a well-conditioned mesh.

**How fitness is computed:** the mesh node positions `(X, Y)` are found by solving a diffusion PDE with Dirichlet boundary conditions. The stiffness matrix is assembled as a sparse CSR matrix from a 5-point stencil and solved exactly with `scipy.sparse.linalg.spsolve`. Each quadrilateral cell's signed area is multiplied by the local material property `E[i][j]`. The fitness of a candidate solution is `1 / (1 + soma)`, where `soma` is the sum of those weighted areas — folded cells (negative area) are penalised by a factor of 1000.

**How the EA works:** a population of 50 individuals each encodes a candidate pair of diffusivity matrices `(Kx, Ky)` as a flat vector (the chromosome). Each generation:

1. **Generate** — dead individuals are replaced via single-point crossover between two live parents; all individuals may mutate their chromosome values or their self-adaptive step sizes.
2. **Evaluate** — fitness is computed for every individual in parallel using `ProcessPoolExecutor`.
3. **Select** — the 25 least-fit individuals are marked for replacement next generation.

After 1 000 generations the champion's mesh is returned.

## Project structure

```
.
├── main.py                          # convenience entry point
├── pyproject.toml                   # deps: numpy>=1.21, scipy>=1.7
├── tests/
└── src/
    └── algoritmo_evolucionario/
        ├── app.py                   # top-level logic: codifica, avalia, reporta, main
        ├── automato.py              # EA loop
        ├── config.py                # dynamic config loader (load / list_available)
        ├── configs/
        │   ├── default.py           # standard scenario (n=10, pop=50, gen=1000)
        │   ├── small.py             # quick smoke-test (n=5, pop=20, gen=100)
        │   ├── large.py             # intensive run (n=20, pop=100, gen=2000)
        │   └── single_point.py      # 10×10, single high-diffusivity cell at E[4][5]=10
        ├── sonda.py                 # orchestrates generate → evaluate (parallel) → select
        ├── populacao.py             # population management
        ├── individuo.py             # individual: chromosome + fitness + state + age
        ├── cromossoma.py            # crossover, mutation, self-adaptive step sizes
        ├── malha.py                 # mesh solver: calcular_KK, calcular_XY, calcular_soma
        ├── quadrilatero.py          # quadrilateral geometry and signed area
        ├── ponto.py                 # 2D point
        └── util.py                  # print_title, max_val, min_val
```

## Installation

Requires Python 3.8 or later. Install in a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

## Running

Any of the following three methods work once the package is installed:

```bash
# as a script
python main.py

# as a module
python -m algoritmo_evolucionario

# as a CLI command (after pip install -e .)
algoritmo-evolucionario
```

A named configuration can be selected at runtime:

```bash
algoritmo-evolucionario --config small   # quick 100-generation run
algoritmo-evolucionario --list-configs   # print all available configs
```

Output is printed to stdout: one line per iteration reporting the champion's fitness, followed by the final mesh node coordinates in gnuplot-compatible format (five points per cell, blank line between rows).

## Configuration

All tuneable parameters are defined in `src/algoritmo_evolucionario/configs/`. Each `.py` file in that directory is a selectable scenario. To create a new one, copy any existing file, rename it, and adjust the constants — it will appear in `--list-configs` immediately with no code changes.

Default parameter values (`configs/default.py`):

| Parameter | Value | Description |
|---|---|---|
| `MESH_N` | 10 | Grid resolution (n×n cells, (n+1)² nodes) |
| `E_MATRIX` | `[[1.0]*n]*n` | Material property per cell — define explicitly for non-uniform cases |
| `POPULATION` | 50 | Number of individuals |
| `GENERATIONS` | 1 000 | EA iterations |
| `MUTATION_RATE` | 0.2 | Chromosome mutation probability per individual |
| `CONTROL_DIVISOR` | 5 | Step-size mutation rate = `MUTATION_RATE / CONTROL_DIVISOR` |
| `FOLD_PENALTY` | 1 000 | Weight on folded (negative-area) cells |
| `MAX_WORKERS` | 8 | Max parallel evaluation workers |
| Crossover | — | Single-point |
| Encoding | — | Flattened `Kx` and `Ky` matrices |
| Mesh solve | — | Exact sparse direct solve (SuperLU via scipy) |
| Selection | — | `heapq.nsmallest` — O(n + k log n) |
| Evaluation | — | Parallel — `ProcessPoolExecutor` |

The chromosome also carries a `controlo` (step-size) vector that co-evolves with the chromosome values — a self-adaptive evolution strategy analogous to ES with σ adaptation.
