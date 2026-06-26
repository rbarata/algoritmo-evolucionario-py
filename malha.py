from ponto import Ponto
from quadrilatero import Quadrilatero
from tdma import calcular_tdma
from util import print_title, max_val, min_val


def calcular_KK(n, E, debug=0):
    Kx = []
    if debug > 0:
        print_title("Matriz Kx")
    for i in range(n + 1):
        row = []
        for j in range(n + 1):
            if j == n:
                val = 0.0
            elif i == 0:
                val = E[i][j]
            elif i == n:
                val = E[i - 1][j]
            else:
                val = (E[i - 1][j] + E[i][j]) / 2.0
            row.append(val)
            if debug > 0:
                print(f"#Kx[{i}][{j}]={val}\t", end="")
        if debug > 0:
            print("#")
        Kx.append(row)

    Ky = []
    if debug > 0:
        print_title("Matriz Ky")
    for i in range(n + 1):
        row = []
        for j in range(n + 1):
            if i == n:
                val = 0.0
            elif j == 0:
                val = E[i][j]
            elif j == n:
                val = E[i][j - 1]
            else:
                val = (E[i][j - 1] + E[i][j]) / 2.0
            row.append(val)
            if debug > 0:
                print(f"#Ky[{i}][{j}]={val}\t", end="")
        if debug > 0:
            print("#")
        Ky.append(row)

    return Kx, Ky


def calcular_XY(n, Kx, Ky, Vx, Vy, debug=0):
    X, Y, Vx, Vy = pre_calcular_XY(n, Kx, Ky, Vx, Vy, debug)
    X, Y = pos_calcular_XY(n, Kx, Ky, Vx, Vy, X, Y, debug)
    return X, Y


def pre_calcular_XY(n, Kx, Ky, Vx, Vy, debug=0):
    if debug > 0:
        print_title("Matriz Vx")
    for i in range(n + 1):
        Vx[i][0] = 0.0
        Vx[i][n] = 1.0

    if debug > 0:
        print_title("Matriz Vy")
    for i in range(n + 1):
        Vy[0][i] = 0.0
        Vy[n][i] = 1.0

    if debug > 0:
        print_title("Construir matriz X")
    X = []
    for i in range(n + 1):
        row = []
        for j in range(n + 1):
            val = j / n
            row.append(val)
            if debug > 0:
                print(f"#{val}\t", end="")
        if debug > 0:
            print()
        X.append(row)

    if debug > 0:
        print_title("Construir matriz Y")
    Y = []
    for i in range(n + 1):
        row = []
        for j in range(n + 1):
            val = i / n
            row.append(val)
            if debug > 0:
                print(f"#{val}\t", end="")
        if debug > 0:
            print()
        Y.append(row)

    return X, Y, Vx, Vy


def pos_calcular_XY(n, Kx, Ky, Vx, Vy, X, Y, debug=0):
    dim = n + 1

    if debug > 0:
        print_title("Construir matrizes aP,aE,...,aS,bP")

    aP = [[0.0] * dim for _ in range(dim)]
    aE = [[0.0] * dim for _ in range(dim)]
    aW = [[0.0] * dim for _ in range(dim)]
    aN = [[0.0] * dim for _ in range(dim)]
    aS = [[0.0] * dim for _ in range(dim)]
    bP = [[0.0] * dim for _ in range(dim)]

    for i in range(dim):
        for j in range(dim):
            kx_w = Kx[i][j - 1] if j > 0 else 0.0
            ky_n = Ky[i - 1][j] if i > 0 else 0.0
            aP[i][j] = kx_w + ky_n + Kx[i][j] + Ky[i][j]
            aE[i][j] = Kx[i][j]
            aW[i][j] = kx_w
            aN[i][j] = ky_n
            aS[i][j] = Ky[i][j]

    if debug > 0:
        print_title("Calcular X")
    calcular_tdma(X, aP, aE, aN, aW, aS, bP, Vx, dim, 3, debug - 1)

    if debug > 0:
        print_title("Calcular Y")
    calcular_tdma(Y, aP, aE, aN, aW, aS, bP, Vy, dim, 3, debug - 1)

    return X, Y


def calcular_desvio(n, X, Y, E, debug=0):
    if debug > 0:
        print_title("Cálculo do desvio - diferença entre máximo e mínimo")
    maximo = -1.0
    minimo = 1e100
    for i in range(n):
        for j in range(n):
            quad = Quadrilatero(
                Ponto(X[i][j],     Y[i][j]),
                Ponto(X[i][j+1],   Y[i][j+1]),
                Ponto(X[i+1][j],   Y[i+1][j]),
                Ponto(X[i+1][j+1], Y[i+1][j+1]),
            )
            prod = quad.areaS() * E[i][j]
            if debug > 0:
                print(f"#{prod}\t", end="")
            maximo = max_val(maximo, prod)
            minimo = min_val(minimo, prod)
        if debug > 0:
            print("#")
    maximo = n * n * maximo
    minimo = n * n * minimo
    diferenca = maximo - minimo
    if debug > 0:
        print(f"#max={maximo},min={minimo}, diferenca={diferenca}")
    return diferenca


def calcular_desvio_padrao(n, X, Y, E, debug=0):
    if debug > 0:
        print_title("Cálculo do desvio padrão")
    soma = 0.0
    for i in range(n):
        for j in range(n):
            quad = Quadrilatero(
                Ponto(X[i][j],     Y[i][j]),
                Ponto(X[i][j+1],   Y[i][j+1]),
                Ponto(X[i+1][j],   Y[i+1][j]),
                Ponto(X[i+1][j+1], Y[i+1][j+1]),
            )
            soma += quad.areaS() * E[i][j]
    media = soma / (n * n)
    soma = 0.0
    for i in range(n):
        for j in range(n):
            quad = Quadrilatero(
                Ponto(X[i][j],     Y[i][j]),
                Ponto(X[i][j+1],   Y[i][j+1]),
                Ponto(X[i+1][j],   Y[i+1][j]),
                Ponto(X[i+1][j+1], Y[i+1][j+1]),
            )
            prod = quad.areaS() * E[i][j]
            if debug > 0:
                print(f"#{prod}\t", end="")
            soma += (prod - media) ** 2
        if debug > 0:
            print("#")
    media = soma / (n * n)
    import math
    result = math.sqrt(media)
    if debug > 0:
        print(f"#desvio={result}")
    return result


def calcular_maximo(n, X, Y, E, debug=0):
    if debug > 0:
        print_title("Cálculo do máximo")
    maximo = -1.0
    for i in range(n):
        for j in range(n):
            quad = Quadrilatero(
                Ponto(X[i][j],     Y[i][j]),
                Ponto(X[i][j+1],   Y[i][j+1]),
                Ponto(X[i+1][j],   Y[i+1][j]),
                Ponto(X[i+1][j+1], Y[i+1][j+1]),
            )
            prod = quad.areaS() * E[i][j]
            if debug > 0:
                print(f"#{prod}\t", end="")
            maximo = max_val(maximo, prod)
        if debug > 0:
            print("#")
    maximo = n * n * maximo
    if debug > 0:
        print(f"#max={maximo}")
    return maximo


def calcular_soma(n, X, Y, E, debug=0):
    if debug > 0:
        print_title("Cálculo da soma")
    soma = 0.0
    for i in range(n):
        for j in range(n):
            quad = Quadrilatero(
                Ponto(X[i][j],     Y[i][j]),
                Ponto(X[i][j+1],   Y[i][j+1]),
                Ponto(X[i+1][j],   Y[i+1][j]),
                Ponto(X[i+1][j+1], Y[i+1][j+1]),
            )
            prod = quad.areaS() * E[i][j]
            if debug > 0:
                print(f"#{prod}\t", end="")
            if prod > 0:
                soma += prod
            else:
                soma += (-prod) * 1000
        if debug > 0:
            print("#")
    if debug > 0:
        print(f"\n#soma={soma}")
    return soma
