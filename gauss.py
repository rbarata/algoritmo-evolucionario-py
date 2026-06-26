import random


def gauss_rand():
    valor = 0
    for _ in range(50):
        if random.uniform(0, 2) > 1:
            valor += 1
    return valor / 50
