def print_matrix(dim, matriz, debug=0):
    for i in range(dim):
        for j in range(dim):
            print(f"#{matriz[i][j]}\t", end="")
        print("#")


def mat2vec(n, matriz, debug=0):
    vector = []
    for i in range(n):
        for j in range(n):
            vector.append(matriz[i][j])
    return vector


def vec2mat(n, vector, debug=0):
    if debug > 0:
        print("#Vector->Matriz")
    matriz = []
    for i in range(n):
        row = []
        for j in range(n):
            val = vector[j + i * n]
            row.append(val)
            if debug > 0:
                print(f"#{val}\t", end="")
        if debug > 0:
            print()
        matriz.append(row)
    return matriz


def clone_matrix(matriz):
    return [list(row) for row in matriz]


def _ordenacao_linhas_por_maximo(inicio, A, Ipivot, dimensao):
    pivot_maximo = inicio
    for n in range(inicio, dimensao):
        if abs(A[Ipivot[pivot_maximo]][inicio]) < abs(A[n][inicio]):
            pivot_maximo = n
    if pivot_maximo != inicio:
        Ipivot[pivot_maximo], Ipivot[inicio] = Ipivot[inicio], Ipivot[pivot_maximo]
    return 0


def _condensar_escolha_de_pivot(A, B, Ipivot, debug=0):
    dimensao = len(B)
    if dimensao == 1:
        return 5 if not A[0][0] else 0

    if debug > 0:
        print("#Condensação:")

    Ifail = 0
    last_n = 0
    for n in range(dimensao - 1):
        last_n = n
        erro = _ordenacao_linhas_por_maximo(n, A, Ipivot, dimensao)
        if erro != 0:
            Ifail = erro
            break
        n_reordenado = Ipivot[n]
        pivot = A[n_reordenado][n]
        if pivot == 0:
            Ifail = 2
            break
        if debug > 0:
            print(f"#Condensar {n}ª linha")
        for m in range(n + 1, dimensao):
            m_reordenado = Ipivot[m]
            if A[m_reordenado][n] != 0:
                multiplicador = A[m_reordenado][n] / pivot
                A[m_reordenado][n] = 0
                for k in range(n + 1, dimensao):
                    A[m_reordenado][k] -= multiplicador * A[n_reordenado][k]
                B[m_reordenado] -= multiplicador * B[n_reordenado]

    if Ifail == 0:
        soma = sum(abs(A[Ipivot[last_n]][k]) for k in range(1, dimensao))
        if soma == 0:
            Ifail = 5

    return Ifail


def _solucao(A, B, Ipivot, debug=0):
    dimensao = len(B)
    Ifail = 0
    X = [0.0] * dimensao

    if debug > 0:
        print("#Solução :")

    for n in range(dimensao - 1, -1, -1):
        n_reordenado = Ipivot[n]
        soma_da_linha = 0.0
        for k in range(dimensao - 1, n, -1):
            k_reordenado = Ipivot[k]
            soma_da_linha += A[n_reordenado][k] * B[k_reordenado]
        if A[n_reordenado][n] == 0:
            Ifail = 3
            break
        X[n] = B[n_reordenado] = (B[n_reordenado] - soma_da_linha) / A[n_reordenado][n]

    for i in range(dimensao):
        B[i] = X[i]

    return Ifail


def calcular_pivot_parcial(A, B, debug=0):
    dimensao = len(B)
    Ipivot = list(range(dimensao))

    erro = _condensar_escolha_de_pivot(A, B, Ipivot, debug - 1)
    if erro == 0:
        erro = _solucao(A, B, Ipivot, debug - 1)

    if debug > 0:
        msgs = {
            0: "Não houve erros no cálculo",
            2: "ERRO - Pivot nulo, cálculo interrompido",
            3: "ERRO - Pivot nulo na substituição ascendente",
            4: "ERRO - Impossivel reordenar a matriz",
            5: "ERRO - Matriz singular",
            99: "ERRO - Parâmetro errado em chamada de função",
        }
        print("#" + msgs.get(erro, "Isto não pode acontecer"))

    return erro
