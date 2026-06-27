from datetime import datetime

import numpy as np

from .automato import automato
from .malha import calcular_KK, calcular_XY, calcular_soma
from .util import print_title


def codifica(n, Kx, Ky, debug=0):
    Kx_np = np.asarray(Kx)
    Ky_np = np.asarray(Ky)
    return list(np.concatenate([Kx_np.ravel(), Ky_np.ravel()]))


def descodifica(n, codificado, debug=0):
    size = (n + 1) ** 2
    arr  = np.asarray(codificado)
    Kx   = arr[:size].reshape(n + 1, n + 1)
    Ky   = arr[size:2 * size].reshape(n + 1, n + 1)
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
    debug = 0

    print_title(datetime.now().strftime("%c"))

    n = 10
    E = [[1] * n for _ in range(n)]

    Kx, Ky = calcular_KK(n, E, debug - 1)

    modelo = codifica(n, Kx, Ky, debug)

    parm = {'n': n, 'E': E}

    aptidao_inicial = avalia(modelo, parm, debug)
    print(f"##aptidão:{aptidao_inicial}")
    reporta(modelo, parm, debug)

    automato(50, modelo, avalia, reporta, 1000, parm, debug)

    print_title(datetime.now().strftime("%c"))
