from .populacao import Populacao


class Sonda:
    def __init__(self, taxa_de_mutacao, a_eliminar, idade_maxima,
                 dimensao, modelo, f_avalia, f_reporta, parm, debug=0):
        self.taxa_de_mutacao = taxa_de_mutacao
        self.a_eliminar = a_eliminar
        self.idade_maxima = idade_maxima
        self.f_avalia = f_avalia
        self.f_reporta = f_reporta
        self.parm = parm

        self.populacao = Populacao(dimensao, modelo, debug - 1)
        for n in range(dimensao):
            if debug > 0:
                print(f"#A mutar - passagem {n}")
            self.populacao.diverge(0.5, debug - 1)

    def print_sonda(self, tab=0):
        print("#" + "\t" * tab + "Sonda:")
        print("#" + "\t" * (tab + 1) + f"Taxa de mutação:{self.taxa_de_mutacao}")
        print("#" + "\t" * (tab + 1) + f"A eliminar:{self.a_eliminar}")
        print("#" + "\t" * (tab + 1) + f"Idade máxima:{self.idade_maxima}")
        self.populacao.print_populacao(tab + 1)

    def gera(self, debug=0):
        self.populacao.refresh(self.taxa_de_mutacao, debug - 1)

    def avalia(self, debug=0):
        self.calcula_aptidao(self.f_avalia, debug - 1)
        self.populacao.selecciona(self.a_eliminar, debug - 1)

    def calcula_aptidao(self, avalia_fn, debug=0):
        pop = self.populacao
        parm = self.parm
        for n in range(pop.dimensao):
            pop.individuos[n].aptidao = avalia_fn(
                pop.individuos[n].cromossoma.valor(), parm, debug - 1
            )
        max_apt, nmax = 0.0, -1
        min_apt, nmin = 1e10, -1
        for n in range(pop.dimensao):
            apt = pop.individuos[n].aptidao
            if apt < min_apt:
                min_apt, nmin = apt, n
            if apt > max_apt:
                max_apt, nmax = apt, n
        pop.campiao = nmax
        pop.besta = nmin

    def reporta(self, iteracao, debug=0):
        pop = self.populacao
        campiao = pop.campiao
        print("#***************************************")
        print(f"#iteração {iteracao}")
        print(f"#campeão {campiao}")
        if campiao == -1:
            print("#Não há valores...")
        else:
            ind = pop.individuos[campiao]
            print(f"#aptidão {ind.aptidao}")
            print(f"#idade {ind.idade}")
            ind.cromossoma.print_cromossoma()
            ind.print_individuo()
            self.f_reporta(ind.cromossoma.valor(), self.parm, debug - 1)
        print("#---------------------------------------")
