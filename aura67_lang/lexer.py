"""Analisador lexico do AURA67."""

from .errors import LexError

PALAVRAS_RESERVADAS = {
    "COMECA_A_FARMAR": "COMECA_A_FARMAR", "FIM_DA_FARM": "FIM_DA_FARM",
    "FARMA": "FARMA", "PARA_DE_FARMAR": "PARA_DE_FARMAR",
    "RIZZ": "RIZZ", "AURA": "AURA", "FLEXA": "FLEXA",
    "CAPTA_A_VIBE": "CAPTA_A_VIBE",
    "SE_TEM_AURA": "SE_TEM_AURA", "SE_FOR_SEISSETE": "SE_FOR_SEISSETE",
    "SENAO": "SENAO", "ENQUANTO_FARMANDO": "ENQUANTO_FARMANDO",
    "COMBO": "COMBO", "OU_ENTAO": "OU_ENTAO", "RESISTE": "RESISTE",
    "FARMA_AURA": "FARMA_AURA", "PAGA_TAXA": "PAGA_TAXA",
    "SEISSETE": "SEISSETE",
}

SIMBOLOS_SIMPLES = {
    "+": "MAIS", "-": "MENOS", "*": "VEZES", "/": "DIV",
    "(": "ABRE_PAR", ")": "FECHA_PAR", ",": "VIRGULA", ";": "PONTOVIRG",
}


class Token:
    __slots__ = ("tipo", "lexema", "valor", "linha")

    def __init__(self, tipo, lexema, valor, linha):
        self.tipo = tipo
        self.lexema = lexema
        self.valor = valor
        self.linha = linha

    def __repr__(self):
        return f"Token({self.tipo!r}, {self.lexema!r}, linha={self.linha})"


def _is_id_start(c):
    return c.isalpha() or c == "_"


def _is_id_part(c):
    return c.isalnum() or c == "_"


def tokenizar(codigo_fonte):
    tokens = []
    i = 0
    linha = 1
    n = len(codigo_fonte)

    while i < n:
        c = codigo_fonte[i]

        if c == "\n":
            linha += 1
            i += 1
            continue
        if c in " \t\r":
            i += 1
            continue

        if c == "-" and i + 1 < n and codigo_fonte[i + 1] == "-":
            while i < n and codigo_fonte[i] != "\n":
                i += 1
            continue

        if _is_id_start(c):
            j = i + 1
            while j < n and _is_id_part(codigo_fonte[j]):
                j += 1
            lexema = codigo_fonte[i:j]
            tipo = PALAVRAS_RESERVADAS.get(lexema, "ID")
            tokens.append(Token(tipo, lexema, lexema, linha))
            i = j
            continue

        if c.isdigit():
            j = i + 1
            while j < n and codigo_fonte[j].isdigit():
                j += 1
            eh_real = False
            if j < n and codigo_fonte[j] == "." and j + 1 < n and codigo_fonte[j + 1].isdigit():
                eh_real = True
                j += 1
                while j < n and codigo_fonte[j].isdigit():
                    j += 1
            lexema = codigo_fonte[i:j]
            valor = float(lexema) if eh_real else int(lexema)
            tokens.append(Token("NUM_REAL" if eh_real else "NUM_INT", lexema, valor, linha))
            i = j
            continue

        if c == '"':
            j = i + 1
            while j < n and codigo_fonte[j] != '"' and codigo_fonte[j] != "\n":
                j += 1
            if j >= n or codigo_fonte[j] != '"':
                raise LexError(f"string nao terminada: {codigo_fonte[i:j]!r}", linha)
            conteudo = codigo_fonte[i + 1:j]
            tokens.append(Token("STRING", codigo_fonte[i:j + 1], conteudo, linha))
            i = j + 1
            continue

        if c == "=":
            if i + 1 < n and codigo_fonte[i + 1] == "=":
                tokens.append(Token("IGUAL_IGUAL", "==", "==", linha)); i += 2
            else:
                tokens.append(Token("IGUAL", "=", "=", linha)); i += 1
            continue

        if c == "!":
            if i + 1 < n and codigo_fonte[i + 1] == "=":
                tokens.append(Token("DIFERENTE", "!=", "!=", linha)); i += 2; continue
            raise LexError(f"simbolo invalido '{c}' (esperava '!=')", linha)

        if c == ">":
            if i + 1 < n and codigo_fonte[i + 1] == "=":
                tokens.append(Token("MAIOR_IGUAL", ">=", ">=", linha)); i += 2
            else:
                tokens.append(Token("MAIOR", ">", ">", linha)); i += 1
            continue

        if c == "<":
            if i + 1 < n and codigo_fonte[i + 1] == "=":
                tokens.append(Token("MENOR_IGUAL", "<=", "<=", linha)); i += 2
            else:
                tokens.append(Token("MENOR", "<", "<", linha)); i += 1
            continue

        if c in SIMBOLOS_SIMPLES:
            tokens.append(Token(SIMBOLOS_SIMPLES[c], c, c, linha)); i += 1
            continue

        raise LexError(f"caractere/lexema invalido '{c}'", linha)

    tokens.append(Token("EOF", "<eof>", None, linha))
    return tokens
