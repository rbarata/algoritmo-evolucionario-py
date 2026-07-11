import os
from concurrent.futures import ProcessPoolExecutor
from itertools import repeat

from . import config
from .populacao import Populacao


class Sonda:
    def __init__(self, taxa_de_mutacao, a_eliminar,
                 dimensao, modelo, f_avalia, f_reporta, parm, debug=0):
        self.taxa_de_mutacao = taxa_de_mutacao
        self.a_eliminar      = a_eliminar
        self.f_avalia        = f_avalia
        self.f_reporta       = f_reporta
        self.parm            = parm

        n_workers = min(os.cpu_count() or 1, config.MAX_WORKERS)
        self._executor = ProcessPoolExecutor(max_workers=n_workers) if n_workers > 1 else None

        self.populacao = Populacao(dimensao, modelo, debug - 1)
        for n in range(dimensao):
            if debug > 0:
                print(f"#A mutar - passagem {n}")
            self.populacao.diverge(config.DIVERGE_RATE, debug - 1)

    def __del__(self):
        if getattr(self, '_executor', None):
            self._executor.shutdown(wait=False)

    def print_sonda(self, tab=0):
        print("#" + "\t" * tab + "Sonda:")
        print("#" + "\t" * (tab + 1) + f"Taxa de mutação:{self.taxa_de_mutacao}")
        print("#" + "\t" * (tab + 1) + f"A eliminar:{self.a_eliminar}")
        self.populacao.print_populacao(tab + 1)

    def gera(self, debug=0):
        self.populacao.refresh(self.taxa_de_mutacao, debug - 1)

    def avalia(self, debug=0):
        self.calcula_aptidao(self.f_avalia, debug - 1)
        self.populacao.selecciona(self.a_eliminar, debug - 1)

    def calcula_aptidao(self, avalia_fn, debug=0):
        pop  = self.populacao
        parm = self.parm
        dim  = pop.dimensao
        chromosomes = [pop.individuos[n].cromossoma.valor() for n in range(dim)]

        if self._executor is not None:
            aptidoes = list(self._executor.map(
                avalia_fn, chromosomes, repeat(parm), repeat(0),
            ))
        else:
            aptidoes = [avalia_fn(c, parm, 0) for c in chromosomes]

        max_apt, nmax = 0.0, -1
        min_apt, nmin = 1e10, -1
        for n, apt in enumerate(aptidoes):
            pop.individuos[n].aptidao = apt
            if apt < min_apt:
                min_apt, nmin = apt, n
            if apt > max_apt:
                max_apt, nmax = apt, n
        pop.campeao = nmax
        pop.besta   = nmin

    def reporta(self, iteracao, debug=0):
        pop     = self.populacao
        campeao = pop.campeao
        print("#***************************************")
        print(f"#iteração {iteracao}")
        print(f"#campeão {campeao}")
        if campeao == -1:
            print("#Não há valores...")
        else:
            ind = pop.individuos[campeao]
            print(f"#aptidão {ind.aptidao}")
            print(f"#idade {ind.idade}")
            ind.cromossoma.print_cromossoma()
            ind.print_individuo()
            self.f_reporta(ind.cromossoma.valor(), self.parm, debug - 1)
        print("#---------------------------------------")
