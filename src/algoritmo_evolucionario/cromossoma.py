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
    def cruza(pai1, pai2, kx_size, debug=0):
        # Independent single-point crossover for Kx and Ky regions.
        # Spatial locality is preserved by the Hilbert encoding, so free cuts suffice.
        total = len(pai1.cromossoma)
        cx = random.randint(0, kx_size)
        cy = random.randint(0, total - kx_size)
        cromossoma = (pai1.cromossoma[:cx]
                      + pai2.cromossoma[cx:kx_size]
                      + pai1.cromossoma[kx_size:kx_size + cy]
                      + pai2.cromossoma[kx_size + cy:])
        controlo   = (pai1.controlo[:cx]
                      + pai2.controlo[cx:kx_size]
                      + pai1.controlo[kx_size:kx_size + cy]
                      + pai2.controlo[kx_size + cy:])
        return Cromossoma(cromossoma, controlo)

    def muta_cromossoma(self, comprimento, debug=0):
        pos = random.randint(0, comprimento)
        if debug > 0:
            print(f"#A mutar cromossoma - {pos}...")
        if random.random() > config.MUTATION_BIAS:
            self.cromossoma[pos] += self.controlo[pos]
        else:
            self.cromossoma[pos] -= self.controlo[pos]

    def muta_controlo(self, comprimento, debug=0):
        pos = random.randint(0, comprimento)
        if debug > 0:
            print(f"#A mutar controlo - {pos}...")
        if random.random() > config.MUTATION_BIAS:
            self.controlo[pos] *= config.STEP_FACTOR
        else:
            self.controlo[pos] = max(config.MIN_STEP, self.controlo[pos] / config.STEP_FACTOR)

    def valor(self):
        return list(self.cromossoma)
