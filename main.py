#!/usr/bin/env python3
"""CLI do compilador/transpilador AURA67 -> Python 3.

Uso:
    python3 main.py fonte.a67 [-o saida.py] [--ast]
"""

import argparse
import sys

from aura67_lang.lexer import tokenizar
from aura67_lang.parser import parse
from aura67_lang.semantic import analisar
from aura67_lang.codegen import gerar
from aura67_lang.ast_nodes import dump_arvore
from aura67_lang.errors import Aura67Error


def compilar(caminho_fonte, caminho_saida=None, mostrar_ast=False):
    with open(caminho_fonte, encoding="utf-8") as f:
        codigo = f.read()

    tokens = tokenizar(codigo)
    programa = parse(tokens)

    if mostrar_ast:
        print("=== AST ===")
        print(dump_arvore(programa))
        print()

    analisar(programa)
    codigo_py = gerar(programa)

    if caminho_saida:
        with open(caminho_saida, "w", encoding="utf-8") as f:
            f.write(codigo_py)
        print(f"OK: '{caminho_fonte}' compilado com sucesso -> '{caminho_saida}'")
    else:
        print(codigo_py)

    return codigo_py


def main():
    ap = argparse.ArgumentParser(description="Transpilador AURA67 -> Python 3")
    ap.add_argument("fonte")
    ap.add_argument("-o", "--saida")
    ap.add_argument("--ast", action="store_true")
    args = ap.parse_args()
    try:
        compilar(args.fonte, args.saida, args.ast)
    except Aura67Error as e:
        print(f"ERRO: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
