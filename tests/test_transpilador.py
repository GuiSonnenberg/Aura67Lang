import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from aura67_lang import lexer, parser, semantic, codegen, ast_nodes as ast
from aura67_lang.errors import LexError, ParserError, SemanticError


def compilar_fonte(codigo_fonte):
    tokens = lexer.tokenizar(codigo_fonte)
    programa = parser.parse(tokens)
    semantic.analisar(programa)
    return programa, codegen.gerar(programa)


class TesteLexico(unittest.TestCase):
    def test_tokeniza_palavras_reservadas(self):
        tokens = lexer.tokenizar("COMECA_A_FARMAR FIM_DA_FARM RIZZ AURA FARMA PARA_DE_FARMAR")
        tipos = [t.tipo for t in tokens[:-1]]
        self.assertEqual(
            tipos, ["COMECA_A_FARMAR", "FIM_DA_FARM", "RIZZ", "AURA", "FARMA", "PARA_DE_FARMAR"]
        )

    def test_tokeniza_identificador_comum(self):
        tokens = lexer.tokenizar("aura_total")
        self.assertEqual(tokens[0].tipo, "ID")
        self.assertEqual(tokens[0].lexema, "aura_total")

    def test_tokeniza_numero_inteiro_e_real(self):
        tokens = lexer.tokenizar("42 3.14")
        self.assertEqual((tokens[0].tipo, tokens[0].valor), ("NUM_INT", 42))
        self.assertEqual((tokens[1].tipo, tokens[1].valor), ("NUM_REAL", 3.14))

    def test_tokeniza_string(self):
        tokens = lexer.tokenizar('"farmando aura"')
        self.assertEqual(tokens[0].tipo, "STRING")
        self.assertEqual(tokens[0].valor, "farmando aura")

    def test_operadores_de_maior_correspondencia(self):
        tokens = lexer.tokenizar("== = >= > <= < !=")
        tipos = [t.tipo for t in tokens[:-1]]
        self.assertEqual(
            tipos,
            ["IGUAL_IGUAL", "IGUAL", "MAIOR_IGUAL", "MAIOR", "MENOR_IGUAL", "MENOR", "DIFERENTE"],
        )

    def test_comentario_de_linha_e_ignorado(self):
        tokens = lexer.tokenizar("-- isso e um comentario\nRIZZ")
        self.assertEqual(tokens[0].tipo, "RIZZ")

    def test_caractere_invalido_gera_lexerror(self):
        with self.assertRaises(LexError):
            lexer.tokenizar("RIZZ x = 5$;")


class TesteSintatico(unittest.TestCase):
    def test_parse_programa_minimo(self):
        programa = parser.parse(lexer.tokenizar("COMECA_A_FARMAR FIM_DA_FARM"))
        self.assertIsInstance(programa, ast.Programa)
        self.assertEqual(programa.comandos, [])

    def test_parse_declaracao_com_inicializador(self):
        programa = parser.parse(lexer.tokenizar("COMECA_A_FARMAR RIZZ x = 5; FIM_DA_FARM"))
        decl = programa.comandos[0]
        self.assertIsInstance(decl, ast.Declaracao)
        self.assertEqual((decl.tipo, decl.nome), ("RIZZ", "x"))
        self.assertIsInstance(decl.expr, ast.NumeroLiteral)

    def test_parse_farma_aura_exige_virgula(self):
        with self.assertRaises(ParserError):
            parser.parse(lexer.tokenizar("COMECA_A_FARMAR AURA a = 1.0; FARMA_AURA a 5; FIM_DA_FARM"))

    def test_parse_precedencia_aritmetica(self):
        programa = parser.parse(lexer.tokenizar("COMECA_A_FARMAR RIZZ x = 2 + 3 * 4; FIM_DA_FARM"))
        expr = programa.comandos[0].expr
        # a raiz deve ser o '+', e o lado direito o '*' (precedencia correta)
        self.assertEqual(expr.op, "+")
        self.assertEqual(expr.dire.op, "*")

    def test_parse_bloco_usa_farma_para_de_farmar(self):
        fonte = (
            "COMECA_A_FARMAR SE_TEM_AURA (1 == 1) FARMA PARA_DE_FARMAR "
            "SENAO FARMA PARA_DE_FARMAR FIM_DA_FARM"
        )
        programa = parser.parse(lexer.tokenizar(fonte))
        cond = programa.comandos[0]
        self.assertIsInstance(cond, ast.Condicional)
        self.assertIsNotNone(cond.bloco_else)

    def test_parse_leitura_exige_parenteses(self):
        with self.assertRaises(ParserError):
            parser.parse(lexer.tokenizar("COMECA_A_FARMAR RIZZ x = 1; CAPTA_A_VIBE x; FIM_DA_FARM"))

    def test_parse_condicional_ambigua_usa_expressao_simples(self):
        fonte = "COMECA_A_FARMAR SE_FOR_SEISSETE (SEISSETE) FARMA PARA_DE_FARMAR FIM_DA_FARM"
        programa = parser.parse(lexer.tokenizar(fonte))
        self.assertIsInstance(programa.comandos[0], ast.CondicionalAmbigua)

    def test_token_inesperado_gera_parsererror(self):
        with self.assertRaises(ParserError):
            parser.parse(lexer.tokenizar("COMECA_A_FARMAR ; FIM_DA_FARM"))


class TesteSemantico(unittest.TestCase):
    def test_declaracao_duplicada_gera_erro(self):
        with self.assertRaises(SemanticError):
            compilar_fonte("COMECA_A_FARMAR RIZZ x = 1; RIZZ x = 2; FIM_DA_FARM")

    def test_uso_antes_da_declaracao_gera_erro(self):
        with self.assertRaises(SemanticError):
            compilar_fonte("COMECA_A_FARMAR y = 1; FIM_DA_FARM")

    def test_promocao_rizz_para_aura_e_permitida(self):
        compilar_fonte("COMECA_A_FARMAR AURA a = 1; FIM_DA_FARM")  # nao deve lancar excecao

    def test_atribuir_aura_em_rizz_e_erro(self):
        with self.assertRaises(SemanticError):
            compilar_fonte("COMECA_A_FARMAR RIZZ x = 1.5; FIM_DA_FARM")

    def test_seissete_igual_a_6_marca_sempre_verdadeiro(self):
        fonte = "COMECA_A_FARMAR SE_TEM_AURA (SEISSETE == 6) FARMA PARA_DE_FARMAR FIM_DA_FARM"
        programa, _ = compilar_fonte(fonte)
        self.assertTrue(programa.comandos[0].condicao.sempre_verdadeiro)

    def test_6_igual_seissete_tambem_marca_sempre_verdadeiro(self):
        fonte = "COMECA_A_FARMAR SE_TEM_AURA (6 == SEISSETE) FARMA PARA_DE_FARMAR FIM_DA_FARM"
        programa, _ = compilar_fonte(fonte)
        self.assertTrue(programa.comandos[0].condicao.sempre_verdadeiro)

    def test_seissete_igual_a_outro_numero_nao_marca(self):
        fonte = "COMECA_A_FARMAR SE_TEM_AURA (SEISSETE == 8) FARMA PARA_DE_FARMAR FIM_DA_FARM"
        programa, _ = compilar_fonte(fonte)
        self.assertFalse(programa.comandos[0].condicao.sempre_verdadeiro)


class TesteGeracaoCodigo(unittest.TestCase):
    def test_gera_declaracao_com_anotacao_de_tipo(self):
        _, codigo_py = compilar_fonte("COMECA_A_FARMAR RIZZ x = 5; FIM_DA_FARM")
        self.assertIn("x: int = 5", codigo_py)

    def test_import_random_so_aparece_quando_necessario(self):
        _, sem_seissete = compilar_fonte("COMECA_A_FARMAR RIZZ x = 5; FIM_DA_FARM")
        self.assertNotIn("import random", sem_seissete)

        _, com_seissete = compilar_fonte("COMECA_A_FARMAR RIZZ x = SEISSETE; FIM_DA_FARM")
        self.assertIn("import random", com_seissete)
        self.assertIn("def seissete():", com_seissete)

    def test_seissete_gera_chamada_de_funcao(self):
        _, codigo_py = compilar_fonte("COMECA_A_FARMAR RIZZ x = SEISSETE; FIM_DA_FARM")
        self.assertIn("x: int = seissete()", codigo_py)

    def test_comparacao_sempre_verdadeira_vira_literal_true(self):
        fonte = "COMECA_A_FARMAR SE_TEM_AURA (SEISSETE == 7) FARMA PARA_DE_FARMAR FIM_DA_FARM"
        _, codigo_py = compilar_fonte(fonte)
        self.assertIn("if True:", codigo_py)

    def test_divisao_entre_inteiros_usa_floor_division(self):
        _, codigo_py = compilar_fonte("COMECA_A_FARMAR RIZZ x = 7 / 2; FIM_DA_FARM")
        self.assertIn("//", codigo_py)

    def test_divisao_envolvendo_aura_usa_divisao_real(self):
        _, codigo_py = compilar_fonte("COMECA_A_FARMAR AURA a = 7.0 / 2; FIM_DA_FARM")
        self.assertIn("7.0 / 2", codigo_py)
        self.assertNotIn("7.0 // 2", codigo_py)

    def test_condicional_ambigua_com_aura_usa_round(self):
        fonte = "COMECA_A_FARMAR AURA a = 6.0; SE_FOR_SEISSETE (a) FARMA PARA_DE_FARMAR FIM_DA_FARM"
        _, codigo_py = compilar_fonte(fonte)
        self.assertIn("round(", codigo_py)

    def test_condicional_ambigua_com_rizz_nao_usa_round(self):
        fonte = "COMECA_A_FARMAR RIZZ x = 6; SE_FOR_SEISSETE (x) FARMA PARA_DE_FARMAR FIM_DA_FARM"
        _, codigo_py = compilar_fonte(fonte)
        self.assertNotIn("round(", codigo_py)

    def test_paga_taxa_em_variavel_aura_gera_checagem_negativa(self):
        _, codigo_py = compilar_fonte("COMECA_A_FARMAR AURA a = 1.0; PAGA_TAXA a, 5.0; FIM_DA_FARM")
        self.assertIn("if a < 0:", codigo_py)
        self.assertIn("aura negativa detectada em 'a'!", codigo_py)

    def test_paga_taxa_em_variavel_rizz_nao_gera_checagem(self):
        _, codigo_py = compilar_fonte("COMECA_A_FARMAR RIZZ x = 1; PAGA_TAXA x, 5; FIM_DA_FARM")
        self.assertNotIn("aura negativa", codigo_py)

    def test_flexa_string_nao_tem_newline_automatico(self):
        _, codigo_py = compilar_fonte('COMECA_A_FARMAR FLEXA("oi"); FIM_DA_FARM')
        self.assertIn('print("oi", end="")', codigo_py)

    def test_flexa_expressao_usa_print_normal(self):
        _, codigo_py = compilar_fonte("COMECA_A_FARMAR RIZZ x = 1; FLEXA(x); FIM_DA_FARM")
        self.assertIn("print(x)", codigo_py)


if __name__ == "__main__":
    unittest.main()
