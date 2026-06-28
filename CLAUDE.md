# Project context for Claude Code

This is a Python port (done June 2026) of a 1998 Perl research project (`algoritmo-evolucionario-2`). It uses an **evolutionary algorithm to optimise the node positions of a 2D computational mesh**. The Perl source is in the sibling folder `../algoritmo-evolucionario-2/`.

---

## What the algorithm does

Given an `n×n` grid of material properties `E[i][j]`, the algorithm finds node positions `(X, Y)` on an `(n+1)×(n+1)` point mesh that minimise area variance across cells.

**Fitness:** `1 / (1 + soma)`, where `soma` is the sum over all quadrilateral cells of `areaS(cell) * E[i][j]`. Folded cells (negative signed area) are penalised ×1000. A perfect uniform mesh on uniform `E=1` gives fitness = 1.

**Chromosome encoding:** the matrices `Kx` and `Ky` (diffusivity coefficients, each `(n+1)×(n+1)`) are flattened row-by-row and concatenated into a vector of length `2*(n+1)²`. These are decoded back to numpy arrays in `avalia` before the PDE solve.

**Mesh solve:** given `Kx` and `Ky`, node positions are found by solving a diffusion PDE with Dirichlet boundary conditions (left/right edges fixed in X; top/bottom fixed in Y). The stencil is assembled as a sparse CSR matrix and solved exactly with `scipy.sparse.linalg.spsolve` (SuperLU). One solve for X, one for Y.

**EA loop (1000 generations, population 50):**
1. Dead individuals replaced via single-point crossover of two live parents.
2. Chromosome mutation: random gene ± step-size value (rate 0.2).
3. Step-size mutation: random step-size ×2 or ÷2 (rate 0.04) — self-adaptive ES.
4. Worst 25 individuals marked dead (truncation selection via `heapq.nsmallest`).
5. Population evaluated in parallel using `ProcessPoolExecutor`.

---

## File map

```
main.py                                      thin entry point — just calls app.main()
pyproject.toml                               build config; deps: numpy>=1.21, scipy>=1.7
src/algoritmo_evolucionario/
    app.py          codifica / descodifica / avalia / reporta / main()
    automato.py     automato(pop, model, avalia_fn, reporta_fn, iters, parm, debug)
    sonda.py        Sonda — wraps Populacao; drives gera/avalia/reporta; parallel eval
    populacao.py    Populacao — holds dict of Individuo; refresh/diverge/selecciona
    individuo.py    Individuo — cromossoma + aptidao + estado ('V'/'M'/'N') + idade
    cromossoma.py   Cromossoma — [cromossoma_list, controlo_list]; cruza/muta_cromossoma/muta_controlo
    malha.py        calcular_KK / calcular_XY / _build_coeffs / _assemble / calcular_soma (+ desvio variants)
    quadrilatero.py Quadrilatero(p00,p01,p10,p11) — area() unsigned, areaS() signed
    ponto.py        Ponto(x,y) — soma/subtrai/norma (static methods on class)
    util.py         print_title(s) / max_val(a,b) / min_val(a,b)
    __main__.py     calls app.main() — enables `python -m algoritmo_evolucionario`
    __init__.py     empty
tests/__init__.py                            empty — no tests yet
```

---

## Key data structures

| Name | Type | Shape | Description |
|------|------|-------|-------------|
| `E` | `list[list[float]]` | `n×n` | material property per cell |
| `Kx`, `Ky` | `np.ndarray` | `(n+1)×(n+1)` | interface diffusivities; last col/row always 0 |
| `X`, `Y` | `np.ndarray` | `(n+1)×(n+1)` | mesh node positions (exact sparse solve) |
| `cromossoma` | `list[float]` | `2*(n+1)²` | flattened `Kx` then `Ky` |
| `controlo` | `list[float]` | same | per-gene mutation step sizes (start at 1.0) |

Boundary conditions are handled internally in `calcular_XY`:
- X solve: column `j=0` → 0, column `j=n` → 1 (Dirichlet)
- Y solve: row `i=0` → 0, row `i=n` → 1 (Dirichlet)

---

## Sparse solver (`calcular_XY` / `_assemble` in `malha.py`)

`calcular_XY(n, Kx, Ky)` builds the stiffness matrix and solves twice.

`_assemble(aP, aE, aN, aW, aS, bP, bnd, bc_vals, ...)` builds a `(N, N)` CSR matrix where `N = (n+1)²`. Nodes are numbered `idx = i*dim + j`.

- **Boundary rows** (`bnd[idx] = True`): identity row, `b[idx] = bc_vals[idx]`.
- **Interior rows**: 5-point stencil `aP·T - aE·T_east - aW·T_west - aS·T_south - aN·T_north = bP`.

The boundary rows enforce Dirichlet values exactly; interior rows reference boundary columns naturally — `spsolve` handles both in one factorisation.

---

## Coefficient stencil (from `_build_coeffs`)

```
aP[i][j] = Kx[i][j-1] + Ky[i-1][j] + Kx[i][j] + Ky[i][j]   (west/north terms zero at boundaries)
aE[i][j] = Kx[i][j]
aW[i][j] = Kx[i][j-1]   (zero when j=0)
aN[i][j] = Ky[i-1][j]   (zero when i=0)
aS[i][j] = Ky[i][j]
bP[i][j] = 0
```

---

## `Kx` / `Ky` construction (from `calcular_KK`)

```
Kx[i][j]:  0           if j == n
           E[i][j]     if i == 0
           E[i-1][j]   if i == n
           avg(E[i-1][j], E[i][j])  otherwise

Ky[i][j]:  0           if i == n
           E[i][j]     if j == 0
           E[i][j-1]   if j == n
           avg(E[i][j-1], E[i][j])  otherwise
```

---

## `app.py` — encode / decode

`codifica(n, Kx, Ky)` flattens the two numpy arrays with `np.concatenate([Kx.ravel(), Ky.ravel()])` and returns a Python `list` (the chromosome format used by `Cromossoma`).

`descodifica(n, codificado)` converts the flat list back to two `(n+1)×(n+1)` numpy arrays via `np.asarray(codificado).reshape(n+1, n+1)`.

---

## `Cromossoma` — mutation mechanics

- `muta_cromossoma(comprimento)`: picks random index `pos ∈ [0, comprimento]`; adds or subtracts `controlo[pos]`; result is `abs()`-floored when subtracting.
- `muta_controlo(comprimento)`: picks random index; doubles or halves `controlo[pos]`.
- `cruza(pai1, pai2, comprimento)`: single-point crossover at random `cross ∈ [0, comprimento]`; copies chromosome AND controlo vectors.

---

## `Populacao` — state machine

Individual `estado` values:
- `'V'` — Vivo (alive, eligible for selection and parenthood)
- `'M'` — Morto (marked for replacement next `refresh`)
- `'N'` — recém-Nascido (just born via crossover; promoted to `'V'` at end of `refresh`)

`selecciona(a_eliminar)`: uses `heapq.nsmallest` to find and mark the `a_eliminar` lowest-fitness live individuals as `'M'` in O(n + k log n). Called with `a_eliminar = populacao // 2 = 25`.

---

## `Sonda` — parallel evaluation

`calcula_aptidao` collects all chromosomes, then evaluates them via `ProcessPoolExecutor.map` (up to 8 workers, falls back to serial on single-CPU machines). The executor is created once at `Sonda.__init__` and shut down via `__del__`.

---

## Running

```bash
# setup (first time)
python3 -m venv .venv && source .venv/bin/activate && pip install -e .

# run
python main.py
python -m algoritmo_evolucionario
algoritmo-evolucionario          # CLI entry point from pyproject.toml
```

Default: `n=10`, population 50, 1000 generations. Output goes to stdout: per-iteration champion stats (prefixed `#`), then final mesh coordinates in gnuplot format (5 points per cell, blank line between rows).

---

## Known decisions / deviations from the Perl original

- The hardcoded `$debug=10` line inside the Perl `avalia()` was a leftover debug artifact — dropped.
- `Vx`/`Vy` boundary matrices (list-of-lists with `None` sentinels) replaced by numpy boolean masks built inside `calcular_XY` — no longer exposed in the API.
- The Perl TDMA iterative solver (3 ADI iterations) replaced by a single exact sparse direct solve via `scipy.sparse.linalg.spsolve`.
- `Populacao.individuos` uses a `dict` keyed by int (matching the Perl `"ind_$n"` hash keys) rather than a list, to stay close to the original structure.
- `Util::max` and `Util::min` in Perl relied on implicit return of the last expression. Python versions are explicit (`max_val`, `min_val`) to avoid shadowing builtins.
- `gauss_rand()`, `matriz.py` (Gaussian elimination, mat2vec, vec2mat), and `tdma.py` were deleted as dead or superseded code.
