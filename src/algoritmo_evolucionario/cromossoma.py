import random
from . import config


class Cromossoma:
    def __init__(self, ref, controlo=None):
        self.cromossoma = list(ref)
        if controlo is None:
            self.controlo = [config.INITIAL_STEP] * len(self.cromossoma)
        else:
            self.controlo = list(controlo)

    def print_cromossoma(self, tab=0):
        print("#" + "\t" * tab + f"Cromossoma: {self.cromossoma}")
        print("#" + "\t" * tab + f"Controlo: {self.controlo}")

    @staticmethod
    def cruza(pai1, pai2, comprimento, debug=0):
        cross = random.randint(0, comprimento)
        cromossoma = pai1.cromossoma[:cross + 1] + pai2.cromossoma[cross + 1:comprimento + 1]
        controlo = pai1.controlo[:cross + 1] + pai2.controlo[cross + 1:comprimento + 1]
        return Cromossoma(cromossoma, controlo)

    def muta_cromossoma(self, comprimento, debug=0):
        pos = random.randint(0, comprimento)
        if debug > 0:
            print(f"#A mutar cromossoma - {pos}...")
        if random.random() > config.MUTATION_BIAS:
            self.cromossoma[pos] += self.controlo[pos]
        else:
            self.cromossoma[pos] -= self.controlo[pos]
            self.cromossoma[pos] = abs(self.cromossoma[pos])

    def muta_controlo(self, comprimento, debug=0):
        pos = random.randint(0, comprimento)
        if debug > 0:
            print(f"#A mutar controlo - {pos}...")
        if random.random() > config.MUTATION_BIAS:
            self.controlo[pos] *= config.STEP_FACTOR
        else:
            self.controlo[pos] /= config.STEP_FACTOR

    def valor(self):
        return list(self.cromossoma)
