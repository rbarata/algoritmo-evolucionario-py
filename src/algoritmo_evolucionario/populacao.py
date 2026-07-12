import random  # used in refresh (mutation) and diverge
import numpy as np
from . import config
from .individuo import Individuo


class Populacao:
    def __init__(self, dimensao, modelo, debug=0):
        self.campeao = 0
        self.besta = 0
        self.dimensao = dimensao
        self.comprimento = len(modelo) - 1
        self.kx_size = len(modelo) // 2   # (n+1)*n == n*(n+1), always half the chromosome
        self.individuos = {i: Individuo(modelo) for i in range(dimensao)}

    def print_populacao(self, tab=0):
        print("#" + "\t" * tab + "População:")
        print("#" + "\t" * (tab + 1) + f"Dimensão:{self.dimensao}")
        print("#" + "\t" * (tab + 1) + f"Campeão:{self.campeao}")
        print("#" + "\t" * (tab + 1) + f"Besta:{self.besta}")
        for m in range(self.dimensao):
            self.individuos[m].print_individuo(tab + 1)

    def refresh(self, taxa_de_mutacao, debug=0):
        vivos = [n for n in range(self.dimensao) if self.individuos[n].estado == 'V']
        pais_weights = self._pesos_pais(vivos)

        for n in range(self.dimensao):
            individuo = self.individuos[n]
            if individuo.estado == 'M':
                pai1 = int(np.random.choice(vivos, p=pais_weights))
                pai2 = int(np.random.choice(vivos, p=pais_weights))
                self.individuos[n].cruza(
                    self.individuos[pai1], self.individuos[pai2],
                    self.kx_size, debug - 1
                )
                controlo = self.individuos[n].cromossoma.controlo
                self.individuos[n].cromossoma.controlo = [
                    max(config.MIN_STEP, v * config.BIRTH_DECAY)
                    for v in controlo
                ]
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
        n_vivos = len(vivos)
        if n_vivos <= a_eliminar:
            for n in vivos:
                self.individuos[n].estado = 'M'
            return
        aptidoes = np.array([self.individuos[n].aptidao for n in vivos])
        max_apt = aptidoes.max()
        # death weight: gap from best raised to SELECTION_PRESSURE; ε keeps best weight > 0
        weights = (max_apt - aptidoes + 1e-6) ** config.SELECTION_PRESSURE
        weights /= weights.sum()
        piores = np.random.choice(vivos, size=a_eliminar, replace=False, p=weights)
        for n in piores:
            self.individuos[n].estado = 'M'

    def _pesos_pais(self, vivos):
        aptidoes = np.array([self.individuos[n].aptidao for n in vivos])
        min_apt = aptidoes.min()
        weights = (aptidoes - min_apt + 1e-6) ** config.SELECTION_PRESSURE
        weights /= weights.sum()
        return weights
