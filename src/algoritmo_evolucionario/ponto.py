import math


class Ponto:
    def __init__(self, x=None, y=None):
        self.x = x
        self.y = y

    def print_ponto(self, tab=0):
        print("#" + "\t" * tab + f"Ponto:({self.x},{self.y})")

    @staticmethod
    def soma(p1, p2):
        return Ponto(p1.x + p2.x, p1.y + p2.y)

    @staticmethod
    def subtrai(p1, p2):
        return Ponto(p1.x - p2.x, p1.y - p2.y)

    def max_coord(self):
        return self.y if self.x < self.y else self.x

    def trunc(self, div_x, div_y):
        self.x = (0.5 + int(self.x * div_x)) / div_x
        self.y = (0.5 + int(self.y * div_y)) / div_y
        return self

    def norma(self):
        return math.sqrt(self.x * self.x + self.y * self.y)

    def distancia(self, p):
        return math.sqrt(p.x * p.x + p.y * p.y)
