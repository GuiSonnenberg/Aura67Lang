"""Gerador de codigo do AURA67 -- alvo: Python 3.

Percorre a mesma AST que seria usada para gerar C: nenhuma fase anterior
(lexer, parser, semantic) precisou mudar para trocar o alvo. Cada
traducao depende do tipo e do significado do no, nunca do texto do
token original.
"""

from . import ast_nodes as ast

TIPO_PY = {"RIZZ": "int", "AURA": "float"}
OP_LOGICO_PY = {"E": "and", "OU": "or"}

HELPER_SEISSETE = (
    "def seissete():\n"
    '    """Retorna 6 ou 7, decidido em tempo de execucao (literal SEISSETE)."""\n'
    "    return random.choice((6, 7))\n"
)


class GeradorCodigo:
    def __init__(self):
        self.tabela = {}

    def gerar(self, programa):
        usa_seissete = ast.contem_seissete(programa)
        corpo = self._comandos(programa.comandos, nivel=1)

        linhas = [
            "#!/usr/bin/env python3",
            "# Codigo gerado automaticamente pelo compilador AURA67 (alvo: Python 3)",
            "",
        ]
        if usa_seissete:
            linhas += ["import random", "", "", HELPER_SEISSETE.rstrip("\n"), ""]
        linhas += ["", "def main():"]
        linhas.append(corpo if corpo else "    pass")
        linhas += ["", "", 'if __name__ == "__main__":', "    main()", ""]
        return "\n".join(linhas)

    def _indent(self, nivel):
        return "    " * nivel

    def _comandos(self, comandos, nivel):
        return "\n".join(self._comando(c, nivel) for c in comandos)

    def _comando(self, cmd, nivel):
        ind = self._indent(nivel)

        if isinstance(cmd, ast.Declaracao):
            self.tabela[cmd.nome] = cmd.tipo
            tipo_py = TIPO_PY[cmd.tipo]
            if cmd.expr is not None:
                return f"{ind}{cmd.nome}: {tipo_py} = {self._expr(cmd.expr)}"
            padrao = "0" if cmd.tipo == "RIZZ" else "0.0"
            return f"{ind}{cmd.nome}: {tipo_py} = {padrao}"

        if isinstance(cmd, ast.Atribuicao):
            return f"{ind}{cmd.nome} = {self._expr(cmd.expr)}"

        if isinstance(cmd, ast.FarmaAura):
            return f"{ind}{cmd.nome} += {self._expr(cmd.expr)}"

        if isinstance(cmd, ast.PagaTaxa):
            linhas = [f"{ind}{cmd.nome} -= {self._expr(cmd.expr)}"]
            # --- decisao de projeto 1 (parte b): aviso automatico de aura negativa ---
            if self.tabela.get(cmd.nome) == "AURA":
                linhas.append(f"{ind}if {cmd.nome} < 0:")
                linhas.append(f'{ind}    print("aura negativa detectada em \'{cmd.nome}\'!")')
            return "\n".join(linhas)

        if isinstance(cmd, ast.Leitura):
            conversor = "int" if self.tabela.get(cmd.nome, "RIZZ") == "RIZZ" else "float"
            return f"{ind}{cmd.nome} = {conversor}(input())"

        if isinstance(cmd, ast.Escrita):
            if cmd.eh_string:
                return f'{ind}print("{cmd.alvo}", end="")'
            return f"{ind}print({self._expr(cmd.alvo)})"

        if isinstance(cmd, ast.Condicional):
            linhas = [f"{ind}if {self._expr(cmd.condicao)}:", self._comandos(cmd.bloco_then, nivel + 1)]
            if cmd.bloco_else is not None:
                linhas += [f"{ind}else:", self._comandos(cmd.bloco_else, nivel + 1)]
            return "\n".join(linhas)

        if isinstance(cmd, ast.CondicionalAmbigua):
            # --- decisao de projeto 3: testar o valor contra {6, 7} ---
            tipo_expr = self._tipo_expr(cmd.expr)
            expr_py = self._expr(cmd.expr)
            if tipo_expr == "AURA":
                cond_py = f"round({expr_py}) == 6 or round({expr_py}) == 7"
            else:
                cond_py = f"({expr_py}) == 6 or ({expr_py}) == 7"
            linhas = [f"{ind}if {cond_py}:", self._comandos(cmd.bloco_then, nivel + 1)]
            if cmd.bloco_else is not None:
                linhas += [f"{ind}else:", self._comandos(cmd.bloco_else, nivel + 1)]
            return "\n".join(linhas)

        if isinstance(cmd, ast.Repeticao):
            return "\n".join([
                f"{ind}while {self._expr(cmd.condicao)}:",
                self._comandos(cmd.bloco, nivel + 1),
            ])

        raise ValueError(f"comando nao suportado na geracao de codigo: {type(cmd).__name__}")

    def _tipo_expr(self, no):
        if isinstance(no, ast.NumeroLiteral):
            return no.tipo
        if isinstance(no, ast.SeisSeteLiteral):
            return "RIZZ"
        if isinstance(no, ast.Variavel):
            return self.tabela.get(no.nome, "RIZZ")
        if isinstance(no, ast.OpUnaria):
            return self._tipo_expr(no.operando)
        if isinstance(no, ast.OpBinaria):
            if no.op in ("E", "OU", "==", "!=", ">", ">=", "<", "<="):
                return "LOGICO"
            t_esq = self._tipo_expr(no.esq)
            t_dire = self._tipo_expr(no.dire)
            return "AURA" if "AURA" in (t_esq, t_dire) else "RIZZ"
        return "RIZZ"

    def _expr(self, no):
        if isinstance(no, ast.NumeroLiteral):
            return str(no.valor)

        if isinstance(no, ast.SeisSeteLiteral):
            return "seissete()"

        if isinstance(no, ast.Variavel):
            return no.nome

        if isinstance(no, ast.OpUnaria):
            operando_py = self._expr(no.operando)
            if no.op == "-":
                return f"(-{operando_py})"
            return f"(not {operando_py})"  # NAO

        if isinstance(no, ast.OpBinaria):
            # --- decisao de projeto 2: a comparacao especial vira constante "True" ---
            if getattr(no, "sempre_verdadeiro", False):
                return "True"

            esq_py = self._expr(no.esq)
            dire_py = self._expr(no.dire)

            if no.op == "/":
                tipo_esq = self._tipo_expr(no.esq)
                tipo_dire = self._tipo_expr(no.dire)
                op_py = "//" if (tipo_esq == "RIZZ" and tipo_dire == "RIZZ") else "/"
                return f"({esq_py} {op_py} {dire_py})"

            op_py = OP_LOGICO_PY.get(no.op, no.op)
            return f"({esq_py} {op_py} {dire_py})"

        raise ValueError(f"expressao nao suportada na geracao de codigo: {type(no).__name__}")


def gerar(programa):
    return GeradorCodigo().gerar(programa)
