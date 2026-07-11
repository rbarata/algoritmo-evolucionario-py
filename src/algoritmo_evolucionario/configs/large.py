# large — intensive run (20×20 mesh, 2000 generations, population 100)

MESH_N          = 20
E_MATRIX        = [[1.0] * MESH_N for _ in range(MESH_N)]

POPULATION        = 100
GENERATIONS       = 2000
SELECTION_RATE    = 0.2
STAGNATION_WINDOW = 200
MUTATION_RATE     = 0.2
CONTROL_DIVISOR   = 5
DIVERGE_RATE      = 0.5

INITIAL_STEP    = 1.0
STEP_FACTOR     = 2
MUTATION_BIAS   = 0.5

FOLD_PENALTY    = 1000.0
MAX_WORKERS     = 8
