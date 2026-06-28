import heapq
import random
from . import config
from .individuo import Individuo


class Populacao:
    def __init__(self, dimensao, modelo, debug=0):
        self.campiao = 0
        self.besta = 0
        self.dimensao = dimensao
        self.comprimento = len(modelo) - 1
        self.individuos = {n: Individuo(modelo) for n in range(dimensao)}

    def print_populacao(self, tab=0):
        print("#" + "\t" * tab + "População:")
        print("#" + "\t" * (tab + 1) + f"Dimensão:{self.dimensao}")
        print("#" + "\t" * (tab + 1) + f"Campeão:{self.campiao}")
        print("#" + "\t" * (tab + 1) + f"Besta:{self.besta}")
        for m in range(self.dimensao):
            self.individuos[m].print_individuo(tab + 1)

    def refresh(self, taxa_de_mutacao, debug=0):
        for n in range(self.dimensao):
            individuo = self.individuos[n]
            if individuo.estado == 'M':
                pai1 = self._escolher_vivo()
                pai2 = self._escolher_vivo()
                self.individuos[n].cruza(
                    self.individuos[pai1], self.individuos[pai2],
                    self.comprimento, debug - 1
                )
            if random.random() <= taxa_de_mutacao:
                self.individuos[n].muta_cromossoma(self.comprimento, debug - 1)
            if random.random() <= taxa_de_mutacao / config.CONTROL_DIVISOR:
                self.individuos[n].muta_controlo(self.comprimento, debug - 1)

        for n in range(self.dimensao):
            if self.individuos[n].estado == 'N':
                self.individuos[n].estado = 'V'
            if self.individuos[n].estado == 'V':
                self.individuos[n].idade += 1

    def diverge(self, taxa_de_mutacao, debug=0):
        for n in range(self.dimensao):
            if random.random() <= taxa_de_mutacao:
                self.individuos[n].muta_controlo(self.comprimento, debug - 1)

    def selecciona(self, a_eliminar, debug=0):
        vivos = [n for n in range(self.dimensao) if self.individuos[n].estado == 'V']
        piores = heapq.nsmallest(a_eliminar, vivos, key=lambda n: self.individuos[n].aptidao)
        for n in piores:
            self.individuos[n].estado = 'M'

    def _escolher_vivo(self):
        while True:
            idx = random.randrange(self.dimensao)
            if self.individuos[idx].estado == 'V':
                return idx
