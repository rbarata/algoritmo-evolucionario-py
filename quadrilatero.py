from ponto import Ponto


class Quadrilatero:
    def __init__(self, p00, p01, p10, p11):
        self.p00 = p00
        self.p01 = p01
        self.p10 = p10
        self.p11 = p11

    def area(self):
        u = Ponto.subtrai(self.p00, self.p01)
        v = Ponto.subtrai(self.p10, self.p01)
        w = Ponto.subtrai(self.p11, self.p01)
        a1 = abs(u.x * v.y - v.x * u.y) / 2
        a2 = abs(w.x * v.y - v.x * w.y) / 2
        return a1 + a2

    def areaS(self):
        u = Ponto.subtrai(self.p00, self.p01)
        v = Ponto.subtrai(self.p10, self.p01)
        w = Ponto.subtrai(self.p11, self.p01)
        a1 = (u.x * v.y - v.x * u.y) / 2
        a2 = (w.x * v.y - v.x * w.y) / 2
        return a1 + a2

    def print_quad(self, tab=0):
        print("#" + "\t" * tab + "Quadrilatero:")
        self.p00.print_ponto(tab + 1)
        self.p10.print_ponto(tab + 1)
        self.p01.print_ponto(tab + 1)
        self.p11.print_ponto(tab + 1)
