"""Analisador semantico do AURA67."""

from . import ast_nodes as ast
from .errors import SemanticError

NUMERICOS = ("RIZZ", "AURA")


class TabelaDeSimbolos:
    def __init__(self):
        self._tipos = {}

    def declarar(self, nome, tipo, linha):
        if nome in self._tipos:
            raise SemanticError(f"variavel '{nome}' ja declarada neste escopo", linha)
        self._tipos[nome] = tipo

    def tipo_de(self, nome, linha):
        if nome not in self._tipos:
            raise SemanticError(f"variavel '{nome}' nao declarada", linha)
        return self._tipos[nome]


class AnalisadorSemantico:
    def __init__(self):
        self.tabela = TabelaDeSimbolos()

    def analisar(self, programa):
        for cmd in programa.comandos:
            self._comando(cmd)
        return self.tabela

    def _bloco(self, comandos):
        for cmd in comandos:
            self._comando(cmd)

    def _comando(self, cmd):
        if isinstance(cmd, ast.Declaracao):
            if cmd.expr is not None:
                self._checar_atribuivel(cmd.tipo, self._tipo_expr(cmd.expr), cmd.linha, cmd.nome)
            self.tabela.declarar(cmd.nome, cmd.tipo, cmd.linha)
        elif isinstance(cmd, ast.Atribuicao):
            tipo_var = self.tabela.tipo_de(cmd.nome, cmd.linha)
            self._checar_atribuivel(tipo_var, self._tipo_expr(cmd.expr), cmd.linha, cmd.nome)
        elif isinstance(cmd, (ast.FarmaAura, ast.PagaTaxa)):
            tipo_var = self.tabela.tipo_de(cmd.nome, cmd.linha)
            if tipo_var not in NUMERICOS:
                raise SemanticError(f"variavel '{cmd.nome}' precisa ser RIZZ ou AURA", cmd.linha)
            tipo_expr = self._tipo_expr(cmd.expr)
            tipo_resultado = "AURA" if "AURA" in (tipo_var, tipo_expr) else "RIZZ"
            self._checar_atribuivel(tipo_var, tipo_resultado, cmd.linha, cmd.nome)
        elif isinstance(cmd, ast.Leitura):
            self.tabela.tipo_de(cmd.nome, cmd.linha)
        elif isinstance(cmd, ast.Escrita):
            if not cmd.eh_string:
                self._tipo_expr(cmd.alvo)
        elif isinstance(cmd, ast.Condicional):
            self._tipo_expr(cmd.condicao)
            self._bloco(cmd.bloco_then)
            if cmd.bloco_else is not None:
                self._bloco(cmd.bloco_else)
        elif isinstance(cmd, ast.CondicionalAmbigua):
            if self._tipo_expr(cmd.expr) not in NUMERICOS:
                raise SemanticError("condicao de SE_FOR_SEISSETE precisa ser numerica", cmd.linha)
            self._bloco(cmd.bloco_then)
            if cmd.bloco_else is not None:
                self._bloco(cmd.bloco_else)
        elif isinstance(cmd, ast.Repeticao):
            self._tipo_expr(cmd.condicao)
            self._bloco(cmd.bloco)

    def _checar_atribuivel(self, tipo_alvo, tipo_valor, linha, nome):
        if tipo_alvo == tipo_valor:
            return
        if tipo_alvo == "AURA" and tipo_valor == "RIZZ":
            return  # promocao int -> float
        raise SemanticError(
            f"atribuicao incompativel: variavel '{nome}' e {tipo_alvo}, mas a expressao e {tipo_valor}", linha)

    def _tipo_expr(self, no):
        if isinstance(no, ast.NumeroLiteral):
            return no.tipo
        if isinstance(no, ast.SeisSeteLiteral):
            return "RIZZ"
        if isinstance(no, ast.Variavel):
            return self.tabela.tipo_de(no.nome, no.linha)
        if isinstance(no, ast.OpUnaria):
            if no.op == "-":
                return self._tipo_expr(no.operando)
            self._tipo_expr(no.operando)
            return "LOGICO"
        if isinstance(no, ast.OpBinaria):
            if no.op in ("E", "OU"):
                self._tipo_expr(no.esq)
                self._tipo_expr(no.dire)
                return "LOGICO"
            if no.op in ("==", "!=", ">", ">=", "<", "<="):
                self._tipo_expr(no.esq)
                self._tipo_expr(no.dire)
                # --- decisao de projeto 2: a regra especial do SEISSETE ---
                if no.op == "==":
                    no.sempre_verdadeiro = self._eh_seissete_vs_6_ou_7(no.esq, no.dire)
                return "LOGICO"
            t_esq = self._tipo_expr(no.esq)
            t_dire = self._tipo_expr(no.dire)
            return "AURA" if "AURA" in (t_esq, t_dire) else "RIZZ"
        raise SemanticError(f"expressao nao reconhecida: {type(no).__name__}", getattr(no, "linha", None))

    @staticmethod
    def _eh_seissete_vs_6_ou_7(esq, dire):
        def eh_6_ou_7(no):
            return isinstance(no, ast.NumeroLiteral) and no.tipo == "RIZZ" and no.valor in (6, 7)

        if isinstance(esq, ast.SeisSeteLiteral) and eh_6_ou_7(dire):
            return True
        if isinstance(dire, ast.SeisSeteLiteral) and eh_6_ou_7(esq):
            return True
        return False


def analisar(programa):
    return AnalisadorSemantico().analisar(programa)
