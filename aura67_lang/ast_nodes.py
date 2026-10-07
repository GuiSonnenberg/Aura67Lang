"""Nos da arvore sintatica abstrata (AST) do AURA67.

Guardam apenas a informacao semantica relevante (tipo, nome,
subexpressoes, linha) -- nunca o texto original do token. E por isso
que a mesma AST serve tanto para gerar C quanto para gerar Python: so
o gerador de codigo muda.
"""


class No:
    def __init__(self, linha):
        self.linha = linha


class Programa(No):
    def __init__(self, comandos, linha=1):
        super().__init__(linha)
        self.comandos = comandos


class Declaracao(No):
    def __init__(self, tipo, nome, expr, linha):
        super().__init__(linha)
        self.tipo = tipo          # 'RIZZ' ou 'AURA'
        self.nome = nome
        self.expr = expr         # pode ser None


class Atribuicao(No):
    def __init__(self, nome, expr, linha):
        super().__init__(linha)
        self.nome = nome
        self.expr = expr


class FarmaAura(No):   # FARMA_AURA id, expr;  (decisao 1)
    def __init__(self, nome, expr, linha):
        super().__init__(linha)
        self.nome = nome
        self.expr = expr


class PagaTaxa(No):    # PAGA_TAXA id, expr;   (decisao 1)
    def __init__(self, nome, expr, linha):
        super().__init__(linha)
        self.nome = nome
        self.expr = expr


class Leitura(No):
    def __init__(self, nome, linha):
        super().__init__(linha)
        self.nome = nome


class Escrita(No):
    def __init__(self, alvo, eh_string, linha):
        super().__init__(linha)
        self.alvo = alvo
        self.eh_string = eh_string


class Condicional(No):
    def __init__(self, condicao, bloco_then, bloco_else, linha):
        super().__init__(linha)
        self.condicao = condicao
        self.bloco_then = bloco_then
        self.bloco_else = bloco_else


class CondicionalAmbigua(No):   # SE_FOR_SEISSETE (decisao 3)
    def __init__(self, expr, bloco_then, bloco_else, linha):
        super().__init__(linha)
        self.expr = expr
        self.bloco_then = bloco_then
        self.bloco_else = bloco_else


class Repeticao(No):
    def __init__(self, condicao, bloco, linha):
        super().__init__(linha)
        self.condicao = condicao
        self.bloco = bloco


class OpBinaria(No):
    def __init__(self, op, esq, dire, linha):
        super().__init__(linha)
        self.op = op
        self.esq = esq
        self.dire = dire
        self.sempre_verdadeiro = False   # usado na decisao 2 (SEISSETE)


class OpUnaria(No):
    def __init__(self, op, operando, linha):
        super().__init__(linha)
        self.op = op
        self.operando = operando


class Variavel(No):
    def __init__(self, nome, linha):
        super().__init__(linha)
        self.nome = nome


class NumeroLiteral(No):
    def __init__(self, valor, tipo, linha):
        super().__init__(linha)
        self.valor = valor
        self.tipo = tipo


class SeisSeteLiteral(No):   # o literal SEISSETE (decisao 2)
    def __init__(self, linha):
        super().__init__(linha)


def dump_arvore(no, prefixo="", ultimo=True):
    """Imprime a AST como uma arvore em texto, para depuracao (--ast)."""
    conector = "`-- " if ultimo else "|-- "
    nome = type(no).__name__
    extra = ""
    if isinstance(no, Declaracao):
        extra = f" ({no.tipo} {no.nome})"
    elif isinstance(no, (Atribuicao, FarmaAura, PagaTaxa, Leitura, Variavel)):
        extra = f" ({no.nome})"
    elif isinstance(no, Escrita):
        extra = f" (string)" if no.eh_string else ""
    elif isinstance(no, NumeroLiteral):
        extra = f" ({no.valor}:{no.tipo})"
    elif isinstance(no, OpBinaria):
        extra = f" ({no.op}{', sempre_verdadeiro' if no.sempre_verdadeiro else ''})"
    elif isinstance(no, OpUnaria):
        extra = f" ({no.op})"

    linhas = [f"{prefixo}{conector}{nome}{extra}"]
    novo_prefixo = prefixo + ("    " if ultimo else "|   ")
    filhos = _filhos(no)
    for idx, filho in enumerate(filhos):
        linhas.append(dump_arvore(filho, novo_prefixo, idx == len(filhos) - 1))
    return "\n".join(linhas)


def _filhos(no):
    if isinstance(no, Programa):
        return list(no.comandos)
    if isinstance(no, Declaracao):
        return [no.expr] if no.expr is not None else []
    if isinstance(no, (Atribuicao, FarmaAura, PagaTaxa)):
        return [no.expr]
    if isinstance(no, Escrita):
        return [] if no.eh_string else [no.alvo]
    if isinstance(no, Condicional):
        f = [no.condicao] + list(no.bloco_then)
        if no.bloco_else is not None:
            f += list(no.bloco_else)
        return f
    if isinstance(no, CondicionalAmbigua):
        f = [no.expr] + list(no.bloco_then)
        if no.bloco_else is not None:
            f += list(no.bloco_else)
        return f
    if isinstance(no, Repeticao):
        return [no.condicao] + list(no.bloco)
    if isinstance(no, OpBinaria):
        return [no.esq, no.dire]
    if isinstance(no, OpUnaria):
        return [no.operando]
    return []


def contem_seissete(no):
    """Varredura recursiva: existe algum SeisSeteLiteral em qualquer lugar da AST?"""
    if isinstance(no, SeisSeteLiteral):
        return True
    if isinstance(no, Programa):
        return any(contem_seissete(c) for c in no.comandos)
    if isinstance(no, Declaracao):
        return no.expr is not None and contem_seissete(no.expr)
    if isinstance(no, (Atribuicao, FarmaAura, PagaTaxa)):
        return contem_seissete(no.expr)
    if isinstance(no, Escrita):
        return (not no.eh_string) and contem_seissete(no.alvo)
    if isinstance(no, Condicional):
        if contem_seissete(no.condicao):
            return True
        if any(contem_seissete(c) for c in no.bloco_then):
            return True
        if no.bloco_else is not None and any(contem_seissete(c) for c in no.bloco_else):
            return True
        return False
    if isinstance(no, CondicionalAmbigua):
        if contem_seissete(no.expr):
            return True
        if any(contem_seissete(c) for c in no.bloco_then):
            return True
        if no.bloco_else is not None and any(contem_seissete(c) for c in no.bloco_else):
            return True
        return False
    if isinstance(no, Repeticao):
        if contem_seissete(no.condicao):
            return True
        return any(contem_seissete(c) for c in no.bloco)
    if isinstance(no, OpBinaria):
        return contem_seissete(no.esq) or contem_seissete(no.dire)
    if isinstance(no, OpUnaria):
        return contem_seissete(no.operando)
    return False
