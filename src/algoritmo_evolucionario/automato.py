from . import config
from .sonda import Sonda


def automato(populacao, modelo, avalia, reporta, iteracoes, parm, debug=0):
    a_eliminar = max(1, round(populacao * config.SELECTION_RATE))

    sonda = Sonda(
        taxa_de_mutacao=config.MUTATION_RATE,
        a_eliminar=a_eliminar,
        dimensao=populacao,
        modelo=modelo,
        f_avalia=avalia,
        f_reporta=reporta,
        parm=parm,
        debug=debug - 1,
    )

    best_aptidao    = 0.0
    stagnation_count = 0

    for n in range(iteracoes):
        sonda.gera(debug - 1)
        sonda.avalia(debug - 1)
        sonda.reporta(n, debug - 1)

        current_best = sonda.populacao.individuos[sonda.populacao.campeao].aptidao
        if current_best > best_aptidao + 1e-10:
            best_aptidao     = current_best
            stagnation_count = 0
        else:
            stagnation_count += 1

        if stagnation_count >= config.STAGNATION_WINDOW:
            print(f"#reinício na iteração {n}: {config.STAGNATION_WINDOW} gerações sem melhoria")
            sonda.reiniciar()
            stagnation_count = 0

        if debug > 0:
            sonda.print_sonda()

    campeao = sonda.populacao.campeao
    return sonda.populacao.individuos[campeao].cromossoma.valor()
