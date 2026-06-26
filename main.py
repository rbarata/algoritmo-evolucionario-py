#!/usr/bin/env python3
from datetime import datetime

from automato import automato
from malha import calcular_KK, calcular_XY, calcular_soma
from matriz import mat2vec, vec2mat
from util import print_title


def codifica(n, Kx, Ky, debug=0):
    vec_x = mat2vec(n + 1, Kx, debug - 1)
    vec_y = mat2vec(n + 1, Ky, debug - 1)
    codificado = vec_x + vec_y
    if debug > 0:
        print(f"#Codificado:{codificado}")
    return codificado


def descodifica(n, codificado, debug=0):
    if debug > 0:
        print(f"#Descodifica:descodificado={codificado}")
    size = (n + 1) ** 2
    Kx = vec2mat(n + 1, codificado[:size], debug - 1)
    Ky = vec2mat(n + 1, codificado[size:2 * size], debug - 1)
    return Kx, Ky


def _make_boundary(n):
    return [[None] * (n + 1) for _ in range(n + 1)]


def avalia(codificado, parm, debug=0):
    n = parm['n']
    E = parm['E']
    Kx, Ky = descodifica(n, codificado, debug - 1)
    Vx = _make_boundary(n)
    Vy = _make_boundary(n)
    X, Y = calcular_XY(n, Kx, Ky, Vx, Vy, debug - 1)
    desvio = calcular_soma(n, X, Y, E, debug - 1)
    aptidao = 1.0 / (1.0 + desvio)
    if debug > 0:
        print(f"#aptidao=1/(1+{desvio})={aptidao}")
    return aptidao


def reporta(codificado, parm, debug=0):
    n = parm['n']
    E = parm['E']
    Kx, Ky = descodifica(n, codificado, debug - 1)
    Vx = _make_boundary(n)
    Vy = _make_boundary(n)
    X, Y = calcular_XY(n, Kx, Ky, Vx, Vy, debug - 1)
    for i in range(n):
        for j in range(n):
            print(f"{X[i][j]} {Y[i][j]}")
            print(f"{X[i+1][j]} {Y[i+1][j]}")
            print(f"{X[i+1][j+1]} {Y[i+1][j+1]}")
            print(f"{X[i][j+1]} {Y[i][j+1]}")
            print(f"{X[i][j]} {Y[i][j]}")
        print()


def main():
    debug = 0

    print_title(datetime.now().strftime("%c"))

    n = 10
    E = [[1] * n for _ in range(n)]

    Kx, Ky = calcular_KK(n, E, debug - 1)

    Vx = _make_boundary(n)
    Vy = _make_boundary(n)
    calcular_XY(n, Kx, Ky, Vx, Vy, debug - 1)

    modelo = codifica(n, Kx, Ky, debug)

    populacao = 50
    iteracoes = 1000
    parm = {'n': n, 'E': E}

    aptidao_inicial = avalia(modelo, parm, debug)
    print(f"##aptidão:{aptidao_inicial}")
    reporta(modelo, parm, debug)

    automato(populacao, modelo, avalia, reporta, iteracoes, parm, debug)

    print_title(datetime.now().strftime("%c"))


if __name__ == '__main__':
    main()
