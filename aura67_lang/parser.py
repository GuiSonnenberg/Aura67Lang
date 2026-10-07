"""Analisador sintatico (parser) LL(1) recursivo-descendente do AURA67."""

from . import ast_nodes as ast
from .errors import ParserError

OPS_RELACIONAIS = {"IGUAL_IGUAL", "DIFERENTE", "MAIOR", "MAIOR_IGUAL", "MENOR", "MENOR_IGUAL"}
SIMBOLO_OP = {
    "IGUAL_IGUAL": "==", "DIFERENTE": "!=", "MAIOR": ">", "MAIOR_IGUAL": ">=",
    "MENOR": "<", "MENOR_IGUAL": "<=",
    "MAIS": "+", "MENOS": "-", "VEZES": "*", "DIV": "/",
}


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def _atual(self):
        return self.tokens[self.pos]

    def _checar(self, tipo):
        return self._atual().tipo == tipo

    def _avancar(self):
        tok = self.tokens[self.pos]
        if tok.tipo != "EOF":
            self.pos += 1
        return tok

    def _consumir(self, tipo, esperado=None):
        tok = self._atual()
        if tok.tipo != tipo:
            raise ParserError(f"token encontrado '{tok.lexema}', esperado {esperado or tipo}", tok.linha)
        return self._avancar()

    # <Programa> ::= "COMECA_A_FARMAR" { <Declaracao> | <Comando> } "FIM_DA_FARM"
    def parse_programa(self):
        inicio = self._consumir("COMECA_A_FARMAR", "'COMECA_A_FARMAR'")
        comandos = []
        while self._atual().tipo not in ("FIM_DA_FARM", "EOF"):
            comandos.append(self._decl_ou_comando())
        self._consumir("FIM_DA_FARM", "'FIM_DA_FARM'")
        self._consumir("EOF", "fim de arquivo")
        return ast.Programa(comandos, inicio.linha)

    # <Bloco> ::= "FARMA" { <Declaracao> | <Comando> } "PARA_DE_FARMAR"
    def _bloco(self):
        self._consumir("FARMA", "'FARMA'")
        comandos = []
        while self._atual().tipo not in ("PARA_DE_FARMAR", "EOF"):
            comandos.append(self._decl_ou_comando())
        self._consumir("PARA_DE_FARMAR", "'PARA_DE_FARMAR'")
        return comandos

    def _decl_ou_comando(self):
        tipo = self._atual().tipo
        if tipo in ("RIZZ", "AURA"):
            return self._declaracao()
        if tipo == "ID":
            return self._atribuicao()
        if tipo == "FARMA_AURA":
            return self._farma_aura()
        if tipo == "PAGA_TAXA":
            return self._paga_taxa()
        if tipo == "CAPTA_A_VIBE":
            return self._leitura()
        if tipo == "FLEXA":
            return self._escrita()
        if tipo == "SE_TEM_AURA":
            return self._condicional()
        if tipo == "SE_FOR_SEISSETE":
            return self._condicional_ambigua()
        if tipo == "ENQUANTO_FARMANDO":
            return self._repeticao()
        tok = self._atual()
        raise ParserError(f"token encontrado '{tok.lexema}', esperado inicio de declaracao ou comando", tok.linha)

    # <Declaracao> ::= <Tipo> id [ "=" <Expressao> ] ";"
    def _declaracao(self):
        tipo_tok = self._avancar()
        nome_tok = self._consumir("ID", "identificador")
        expr = None
        if self._checar("IGUAL"):
            self._avancar()
            expr = self._expressao()
        self._consumir("PONTOVIRG", "';'")
        return ast.Declaracao(tipo_tok.tipo, nome_tok.lexema, expr, tipo_tok.linha)

    def _atribuicao(self):
        nome_tok = self._consumir("ID")
        self._consumir("IGUAL", "'=' em atribuicao")
        expr = self._expressao()
        self._consumir("PONTOVIRG", "';'")
        return ast.Atribuicao(nome_tok.lexema, expr, nome_tok.linha)

    # <FarmaAura> ::= "FARMA_AURA" id "," <Expressao> ";"   (decisao 1)
    def _farma_aura(self):
        tok = self._consumir("FARMA_AURA")
        nome_tok = self._consumir("ID", "identificador a farmar")
        self._consumir("VIRGULA", "','")
        expr = self._expressao()
        self._consumir("PONTOVIRG", "';'")
        return ast.FarmaAura(nome_tok.lexema, expr, tok.linha)

    def _paga_taxa(self):
        tok = self._consumir("PAGA_TAXA")
        nome_tok = self._consumir("ID", "identificador que paga a taxa")
        self._consumir("VIRGULA", "','")
        expr = self._expressao()
        self._consumir("PONTOVIRG", "';'")
        return ast.PagaTaxa(nome_tok.lexema, expr, tok.linha)

    def _leitura(self):
        tok = self._consumir("CAPTA_A_VIBE")
        self._consumir("ABRE_PAR", "'('")
        nome_tok = self._consumir("ID", "identificador a ser lido")
        self._consumir("FECHA_PAR", "')'")
        self._consumir("PONTOVIRG", "';'")
        return ast.Leitura(nome_tok.lexema, tok.linha)

    def _escrita(self):
        tok = self._consumir("FLEXA")
        self._consumir("ABRE_PAR", "'('")
        if self._checar("STRING"):
            str_tok = self._avancar()
            alvo = str_tok.valor
            eh_string = True
        else:
            alvo = self._expressao()
            eh_string = False
        self._consumir("FECHA_PAR", "')'")
        self._consumir("PONTOVIRG", "';'")
        return ast.Escrita(alvo, eh_string, tok.linha)

    def _condicional(self):
        tok = self._consumir("SE_TEM_AURA")
        self._consumir("ABRE_PAR", "'('")
        cond = self._expr_logica()
        self._consumir("FECHA_PAR", "')'")
        bloco_then = self._bloco()
        bloco_else = None
        if self._checar("SENAO"):
            self._avancar()
            bloco_else = self._bloco()
        return ast.Condicional(cond, bloco_then, bloco_else, tok.linha)

    # <CondicionalAmbigua> (decisao 3): a condicao e uma Expressao, nao uma ExprLogica
    def _condicional_ambigua(self):
        tok = self._consumir("SE_FOR_SEISSETE")
        self._consumir("ABRE_PAR", "'('")
        expr = self._expressao()
        self._consumir("FECHA_PAR", "')'")
        bloco_then = self._bloco()
        bloco_else = None
        if self._checar("SENAO"):
            self._avancar()
            bloco_else = self._bloco()
        return ast.CondicionalAmbigua(expr, bloco_then, bloco_else, tok.linha)

    def _repeticao(self):
        tok = self._consumir("ENQUANTO_FARMANDO")
        self._consumir("ABRE_PAR", "'('")
        cond = self._expr_logica()
        self._consumir("FECHA_PAR", "')'")
        bloco = self._bloco()
        return ast.Repeticao(cond, bloco, tok.linha)

    # ExprLogica ::= ExprConj { OU_ENTAO ExprConj }
    # ExprConj   ::= ExprUn { COMBO ExprUn }
    # ExprUn     ::= [ RESISTE ] ExprRel
    # ExprRel    ::= Expressao OpRel Expressao
    def _expr_logica(self):
        esq = self._expr_conj()
        while self._checar("OU_ENTAO"):
            op_tok = self._avancar()
            dire = self._expr_conj()
            esq = ast.OpBinaria("OU", esq, dire, op_tok.linha)
        return esq

    def _expr_conj(self):
        esq = self._expr_un()
        while self._checar("COMBO"):
            op_tok = self._avancar()
            dire = self._expr_un()
            esq = ast.OpBinaria("E", esq, dire, op_tok.linha)
        return esq

    def _expr_un(self):
        if self._checar("RESISTE"):
            tok = self._avancar()
            operando = self._expr_rel()
            return ast.OpUnaria("NAO", operando, tok.linha)
        return self._expr_rel()

    def _expr_rel(self):
        esq = self._expressao()
        tok = self._atual()
        if tok.tipo not in OPS_RELACIONAIS:
            raise ParserError(f"token encontrado '{tok.lexema}', esperado operador relacional", tok.linha)
        self._avancar()
        dire = self._expressao()
        return ast.OpBinaria(SIMBOLO_OP[tok.tipo], esq, dire, tok.linha)

    # Expressao ::= Termo { (+|-) Termo }    Termo ::= Fator { (*|/) Fator }
    # Fator ::= id | num | SEISSETE | "(" Expressao ")" | "-" Fator
    def _expressao(self):
        esq = self._termo()
        while self._atual().tipo in ("MAIS", "MENOS"):
            tok = self._avancar()
            dire = self._termo()
            esq = ast.OpBinaria(SIMBOLO_OP[tok.tipo], esq, dire, tok.linha)
        return esq

    def _termo(self):
        esq = self._fator()
        while self._atual().tipo in ("VEZES", "DIV"):
            tok = self._avancar()
            dire = self._fator()
            esq = ast.OpBinaria(SIMBOLO_OP[tok.tipo], esq, dire, tok.linha)
        return esq

    def _fator(self):
        tok = self._atual()
        if tok.tipo == "ID":
            self._avancar()
            return ast.Variavel(tok.lexema, tok.linha)
        if tok.tipo == "NUM_INT":
            self._avancar()
            return ast.NumeroLiteral(tok.valor, "RIZZ", tok.linha)
        if tok.tipo == "NUM_REAL":
            self._avancar()
            return ast.NumeroLiteral(tok.valor, "AURA", tok.linha)
        if tok.tipo == "SEISSETE":
            self._avancar()
            return ast.SeisSeteLiteral(tok.linha)
        if tok.tipo == "MENOS":
            self._avancar()
            operando = self._fator()
            return ast.OpUnaria("-", operando, tok.linha)
        if tok.tipo == "ABRE_PAR":
            self._avancar()
            expr = self._expressao()
            self._consumir("FECHA_PAR", "')'")
            return expr
        raise ParserError(f"token encontrado '{tok.lexema}', esperado identificador, numero, SEISSETE ou '('", tok.linha)


def parse(tokens):
    return Parser(tokens).parse_programa()
