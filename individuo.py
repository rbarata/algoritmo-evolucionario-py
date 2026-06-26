from cromossoma import Cromossoma


class Individuo:
    def __init__(self, cromossoma_ref):
        self.cromossoma = Cromossoma(cromossoma_ref)
        self.aptidao = 0.0
        self.estado = 'V'  # Vivo / Morto / recém-Nascido
        self.idade = 0

    def print_individuo(self, tab=0):
        print("#" + "\t" * tab + "Indivíduo:")
        self.cromossoma.print_cromossoma(tab + 1)
        print("#" + "\t" * (tab + 1) + f"Aptidão:{self.aptidao}")
        print("#" + "\t" * (tab + 1) + f"Estado:{self.estado}")
        print("#" + "\t" * (tab + 1) + f"Idade:{self.idade}")

    def cruza(self, pai1, pai2, comprimento, debug=0):
        self.cromossoma = Cromossoma.cruza(
            pai1.cromossoma, pai2.cromossoma, comprimento, debug - 1
        )
        self.estado = 'N'
        self.aptidao = 0.0
        self.idade = 0

    def muta_cromossoma(self, comprimento, debug=0):
        self.cromossoma.muta_cromossoma(comprimento, debug - 1)

    def muta_controlo(self, comprimento, debug=0):
        self.cromossoma.muta_controlo(comprimento, debug - 1)
