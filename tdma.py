def calcular_tdma(T, aP, aE, aN, aW, aS, bP, VI, dimensao, iteracoes, debug=0):
    P = [0.0] * dimensao
    Q = [0.0] * dimensao

    for _ in range(iteracoes):

        # W -> E
        for j in range(dimensao):
            for k in range(dimensao):
                if VI[k][j] is None:
                    a = aP[k][j]
                    b = aS[k][j]
                    c = aN[k][j]
                    t_west = T[k][j - 1] if j > 0 else 0.0
                    t_east = T[k][j + 1] if j + 1 < dimensao else 0.0
                    d = aW[k][j] * t_west + aE[k][j] * t_east + bP[k][j]
                else:
                    a, b, c, d = 1.0, 0.0, 0.0, VI[k][j]
                denom = a - (c * P[k - 1] if k > 0 else 0.0)
                P[k] = b / denom
                Q[k] = (d + (c * Q[k - 1] if k > 0 else 0.0)) / denom
            for k in range(dimensao - 1, -1, -1):
                t_next = T[k + 1][j] if k + 1 < dimensao else 0.0
                T[k][j] = P[k] * t_next + Q[k]

        # N -> S
        for j in range(dimensao):
            for k in range(dimensao):
                if VI[j][k] is None:
                    a = aP[j][k]
                    b = aE[j][k]
                    c = aW[j][k]
                    t_north = T[j - 1][k] if j > 0 else 0.0
                    t_south = T[j + 1][k] if j + 1 < dimensao else 0.0
                    d = aN[j][k] * t_north + aS[j][k] * t_south + bP[j][k]
                else:
                    a, b, c, d = 1.0, 0.0, 0.0, VI[j][k]
                denom = a - (c * P[k - 1] if k > 0 else 0.0)
                P[k] = b / denom
                Q[k] = (d + (c * Q[k - 1] if k > 0 else 0.0)) / denom
            for k in range(dimensao - 1, -1, -1):
                t_next = T[j][k + 1] if k + 1 < dimensao else 0.0
                T[j][k] = P[k] * t_next + Q[k]

        # E -> W
        for j in range(dimensao - 1, -1, -1):
            for k in range(dimensao):
                if VI[k][j] is None:
                    a = aP[k][j]
                    b = aS[k][j]
                    c = aN[k][j]
                    t_west = T[k][j - 1] if j > 0 else 0.0
                    t_east = T[k][j + 1] if j + 1 < dimensao else 0.0
                    d = aW[k][j] * t_west + aE[k][j] * t_east + bP[k][j]
                else:
                    a, b, c, d = 1.0, 0.0, 0.0, VI[k][j]
                denom = a - (c * P[k - 1] if k > 0 else 0.0)
                P[k] = b / denom
                Q[k] = (d + (c * Q[k - 1] if k > 0 else 0.0)) / denom
            for k in range(dimensao - 1, -1, -1):
                t_next = T[k + 1][j] if k + 1 < dimensao else 0.0
                T[k][j] = P[k] * t_next + Q[k]

        # S -> N
        for j in range(dimensao - 1, -1, -1):
            for k in range(dimensao):
                if VI[j][k] is None:
                    a = aP[j][k]
                    b = aE[j][k]
                    c = aW[j][k]
                    t_north = T[j - 1][k] if j > 0 else 0.0
                    t_south = T[j + 1][k] if j + 1 < dimensao else 0.0
                    d = aN[j][k] * t_north + aS[j][k] * t_south + bP[j][k]
                else:
                    a, b, c, d = 1.0, 0.0, 0.0, VI[j][k]
                denom = a - (c * P[k - 1] if k > 0 else 0.0)
                P[k] = b / denom
                Q[k] = (d + (c * Q[k - 1] if k > 0 else 0.0)) / denom
            for k in range(dimensao - 1, -1, -1):
                t_next = T[j][k + 1] if k + 1 < dimensao else 0.0
                T[j][k] = P[k] * t_next + Q[k]
