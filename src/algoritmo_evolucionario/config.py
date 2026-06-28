# config.py — all tuneable parameters in one place

# ── Problem ───────────────────────────────────────────────────────────────────
MESH_N        = 10     # grid resolution: MESH_N×MESH_N cells, (MESH_N+1)² nodes
E_UNIFORM     = 1.0    # material property value for the uniform starting grid

# ── EA ────────────────────────────────────────────────────────────────────────
POPULATION    = 50     # number of individuals
GENERATIONS   = 1000   # number of EA iterations
MUTATION_RATE = 0.2    # chromosome mutation probability per individual per generation
CONTROL_DIVISOR = 5    # control mutation rate = MUTATION_RATE / CONTROL_DIVISOR
DIVERGE_RATE  = 0.5    # step-size mutation rate during initial population diversification

# ── Self-adaptive step sizes ──────────────────────────────────────────────────
INITIAL_STEP  = 1.0    # starting controlo value for every gene
STEP_FACTOR   = 2      # step sizes are multiplied or divided by this on mutation
MUTATION_BIAS = 0.5    # probability of adding (vs subtracting) the step

# ── Fitness ───────────────────────────────────────────────────────────────────
FOLD_PENALTY  = 1000.0  # weight applied to folded (negative-area) cells

# ── Performance ───────────────────────────────────────────────────────────────
MAX_WORKERS   = 8      # upper cap on parallel evaluation worker processes
