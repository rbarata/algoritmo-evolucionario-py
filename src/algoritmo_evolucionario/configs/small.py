# small — quick smoke-test (5×5 mesh, 100 generations, population 20)

MESH_N          = 5
E_MATRIX        = [[1.0] * MESH_N for _ in range(MESH_N)]

POPULATION        = 20
GENERATIONS       = 100
SELECTION_RATE    = 0.2
STAGNATION_WINDOW = 20
MUTATION_RATE     = 0.2
CONTROL_DIVISOR   = 5
DIVERGE_RATE      = 0.5

INITIAL_STEP    = 1.0
STEP_FACTOR     = 2
MUTATION_BIAS   = 0.5

FOLD_PENALTY    = 1000.0
MAX_WORKERS     = 8
