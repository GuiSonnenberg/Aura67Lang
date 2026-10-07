"""Hierarquia de erros do compilador AURA67.

Cada fase do pipeline (lexica, sintatica, semantica) levanta sua propria
subclasse de Aura67Error, carregando o numero da linha onde o problema
foi detectado, para que o diagnostico siga o formato exigido:

    [Fase] linha L: mensagem
"""


class Aura67Error(Exception):
    fase = "Erro"

    def __init__(self, mensagem, linha=None):
        self.mensagem = mensagem
        self.linha = linha
        super().__init__(str(self))

    def __str__(self):
        if self.linha is not None:
            return f"[{self.fase}] linha {self.linha}: {self.mensagem}"
        return f"[{self.fase}] {self.mensagem}"


class LexError(Aura67Error):
    fase = "Erro léxico"


class ParserError(Aura67Error):
    fase = "Erro sintático"


class SemanticError(Aura67Error):
    fase = "Erro semântico"
