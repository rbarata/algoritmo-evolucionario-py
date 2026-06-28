from .config import MUTATION_RATE
from .sonda import Sonda


def automato(populacao, modelo, avalia, reporta, iteracoes, parm, debug=0):
    sonda = Sonda(
        taxa_de_mutacao=MUTATION_RATE,
        a_eliminar=populacao // 2,
        dimensao=populacao,
        modelo=modelo,
        f_avalia=avalia,
        f_reporta=reporta,
        parm=parm,
        debug=debug - 1,
    )

    for n in range(iteracoes):
        sonda.gera(debug - 1)
        sonda.avalia(debug - 1)
        sonda.reporta(n, debug - 1)
        if debug > 0:
            sonda.print_sonda()

    campiao = sonda.populacao.campiao
    return sonda.populacao.individuos[campiao].cromossoma.valor()
