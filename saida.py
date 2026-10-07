#!/usr/bin/env python3
# Codigo gerado automaticamente pelo compilador AURA67 (alvo: Python 3)

import random


def seissete():
    """Retorna 6 ou 7, decidido em tempo de execucao (literal SEISSETE)."""
    return random.choice((6, 7))


def main():
    aura: float = 0.0
    contador: int = 0
    sorte: int = seissete()
    bonus: int = 0
    print("A sorte de hoje (seissete aleatorio): ", end="")
    print(sorte)
    print("Digite um bonus de aura (inteiro): ", end="")
    bonus = int(input())
    while (contador < 5):
        aura += (2 + (3 * 2))
        contador += 1
    aura += bonus
    print("Aura apos o loop: ", end="")
    print(aura)
    if ((aura > 20) and (contador == 5)):
        print("Aura alta e loop completo!\n", end="")
    else:
        print("Continue farmando...\n", end="")
    if round((aura / 2)) == 6 or round((aura / 2)) == 7:
        print("O valor metade da aura deu 6 ou 7!\n", end="")
    else:
        print("Nao deu seissete dessa vez.\n", end="")
    aura -= 100.0
    if aura < 0:
        print("aura negativa detectada em 'aura'!")


if __name__ == "__main__":
    main()
