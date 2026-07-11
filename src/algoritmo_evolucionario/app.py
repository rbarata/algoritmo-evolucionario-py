from datetime import datetime

import numpy as np

from .automato import automato
from . import config
from .hilbert import hilbert_order
from .malha import calcular_KK, calcular_XY, calcular_soma
from .util import print_title


def codifica(n, Kx, Ky, debug=0):
    # Strip neutral boundary genes, log-encode, then reorder by Hilbert curve
    # so spatially close cells are adjacent in the chromosome.
    kx = np.log(np.asarray(Kx, dtype=float)[:, :n])   # (n+1, n)
    ky = np.log(np.asarray(Ky, dtype=float)[:n, :])   # (n, n+1)
    kx_idx = hilbert_order(n + 1, n)
    ky_idx = hilbert_order(n, n + 1)
    kx_i, kx_j = zip(*kx_idx)
    ky_i, ky_j = zip(*ky_idx)
    return list(kx[kx_i, kx_j]) + list(ky[ky_i, ky_j])


def descodifica(n, codificado, debug=0):
    kx_idx = hilbert_order(n + 1, n)
    ky_idx = hilbert_order(n, n + 1)
    kx_size = len(kx_idx)
    arr = np.asarray(codificado)
    Kx = np.zeros((n + 1, n + 1))
    Ky = np.zeros((n + 1, n + 1))
    kx_i, kx_j = zip(*kx_idx)
    ky_i, ky_j = zip(*ky_idx)
    Kx[kx_i, kx_j] = np.exp(arr[:kx_size])
    Ky[ky_i, ky_j] = np.exp(arr[kx_size:])
    return Kx, Ky


def avalia(codificado, parm, debug=0):
    n       = parm['n']
    E       = parm['E']
    Kx, Ky  = descodifica(n, codificado)
    X, Y    = calcular_XY(n, Kx, Ky)
    desvio  = calcular_soma(n, X, Y, E)
    aptidao = 1.0 / (1.0 + desvio)
    if debug > 0:
        print(f"#aptidao=1/(1+{desvio})={aptidao}")
    return aptidao


def reporta(codificado, parm, debug=0):
    n      = parm['n']
    Kx, Ky = descodifica(n, codificado)
    X, Y   = calcular_XY(n, Kx, Ky)
    for i in range(n):
        for j in range(n):
            print(f"{X[i, j]} {Y[i, j]}")
            print(f"{X[i+1, j]} {Y[i+1, j]}")
            print(f"{X[i+1, j+1]} {Y[i+1, j+1]}")
            print(f"{X[i, j+1]} {Y[i, j+1]}")
            print(f"{X[i, j]} {Y[i, j]}")
        print()


def main():
    import argparse
    p = argparse.ArgumentParser(description="Algoritmo Evolucionário — optimização de malha 2D")
    p.add_argument(
        "--config", default="default", metavar="NOME",
        help="configuração a usar (ficheiro em configs/; omitir → default)",
    )
    p.add_argument(
        "--list-configs", action="store_true",
        help="listar configurações disponíveis e sair",
    )
    args = p.parse_args()

    if args.list_configs:
        from .config import _list_available
        print("\n".join(_list_available()))
        return

    config.load(args.config)

    debug = 0

    print_title(datetime.now().strftime("%c"))

    n = config.MESH_N
    E = config.E_MATRIX

    Kx, Ky = calcular_KK(n, E, debug - 1)

    modelo = codifica(n, Kx, Ky, debug)

    parm = {'n': n, 'E': E}

    aptidao_inicial = avalia(modelo, parm, debug)
    print(f"##aptidão:{aptidao_inicial}")
    reporta(modelo, parm, debug)

    automato(config.POPULATION, modelo, avalia, reporta, config.GENERATIONS, parm, debug)

    print_title(datetime.now().strftime("%c"))
