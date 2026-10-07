# AURA67

Linguagem tematica criada para o Trabalho Pratico 1 da disciplina
Linguagens Formais e Compiladores (UNIJUI). O tema combina dois memes
de internet: **farmar aura** (aura farming) e **Six Seven / 6 7**.

O compilador funciona como um **transpilador**: le um programa `.a67`
e gera um programa equivalente em **Python 3**, pronto para ser
executado com `python3 arquivo.py` -- sem precisar de nenhum
compilador.

## Pre-requisitos

- Python 3.8 ou superior (nenhuma biblioteca externa e necessaria)
- Bash (para rodar `run_tests.sh`)

## Estrutura do projeto

```
aura67-lang/
├── aura67_lang/
│   ├── errors.py      # hierarquia de erros (Erro lexico/sintatico/semantico)
│   ├── lexer.py        # analisador lexico (codigo .a67 -> tokens)
│   ├── ast_nodes.py     # nos da AST + utilitarios (dump_arvore, contem_seissete)
│   ├── parser.py        # analisador sintatico LL(1) recursivo-descendente
│   ├── semantic.py       # analisador semantico (tabela de simbolos, tipos)
│   └── codegen.py        # gerador de codigo -> Python 3
├── main.py               # CLI do compilador
├── tests/
│   ├── 01_valido_basico.a67
│   ├── 02_valido_completo.a67
│   ├── 03_erro_lexico.a67
│   ├── 04_erro_sintatico.a67
│   ├── 05_erro_semantico.a67
│   ├── test_transpilador.py   # testes unitarios (unittest)
│   ├── generated/              # .py gerados pelos testes validos
│   └── generated_errors/       # saidas de erro dos testes invalidos
├── run_tests.sh
└── README.md
```

## Como executar

Compilar um programa `.a67` e salvar o Python gerado:

```bash
python3 main.py tests/01_valido_basico.a67 -o saida.py
python3 saida.py
```

Compilar e imprimir o Python gerado direto no terminal (sem `-o`):

```bash
python3 main.py tests/01_valido_basico.a67
```

Ver a AST antes do codigo gerado:

```bash
python3 main.py tests/01_valido_basico.a67 --ast
```

Rodar a suite completa (5 casos obrigatorios + testes unitarios):

```bash
bash run_tests.sh
```

## O tema e as decisoes de design

A linguagem usa palavras-chave do vocabulario de "farmar aura" (o
habito de acumular carisma/confianca atraves de gestos, estilo e
atitude, viralizado em videos curtos) misturado com o meme "Six Seven"
(gesto ambiguo de mao que significa "pode ser isso, pode ser aquilo",
eleito "palavra do ano" de 2025 pelo Dictionary.com). Um bloco em
AURA67 e sempre delimitado por `FARMA ... PARA_DE_FARMAR` (nao por
chaves), e comandos de entrada/saida usam parenteses, como uma chamada
de funcao: `FLEXA(...)` e `CAPTA_A_VIBE(...)`.

Isto nao e um reskin de palavras-chave sobre uma linguagem generica:
tres decisoes estruturais genuinamente mudam a gramatica e a
semantica:

1. **FARMA_AURA/PAGA_TAXA exigem virgula + valor explicito.** Ao
   contrario de um `x++` tradicional, incrementar ou decrementar
   "aura" sempre exige dizer *o quanto* esta sendo farmado ou pago de
   taxa (`FARMA_AURA aura, 10;`). Alem disso, pagar taxa em uma
   variavel do tipo `AURA` gera automaticamente, no Python final, uma
   checagem de "aura negativa" apos a operacao.

2. **O literal `SEISSETE` e ambiguo por definicao.** Seu valor (6 ou
   7) e sorteado em tempo de execucao pela funcao `seissete()` gerada
   no Python de saida. Mas se o programador compara `SEISSETE` com a
   constante `6` ou `7` diretamente no codigo fonte, o analisador
   semantico prova estaticamente que o resultado e sempre verdadeiro,
   e o gerador de codigo emite a constante `True` em vez de uma
   chamada de funcao -- uma forma de constant folding guiada pela
   semantica.

3. **`SE_FOR_SEISSETE` testa um valor, nao uma comparacao.** Em vez de
   escrever uma condicao booleana, o programador passa uma expressao
   numerica qualquer, e o comando verifica se o *valor* dela "da
   seissete" (arredonda para 6 ou 7). Quando a expressao e do tipo
   `AURA` (float), o Python gerado usa `round()`; quando e `RIZZ`
   (inteiro), a comparacao e direta.

## Suite de testes

| Caso | Tipo | O que verifica |
|---|---|---|
| `01_valido_basico.a67` | valido | declaracao, atribuicao, saida |
| `02_valido_completo.a67` | valido | laco, FARMA_AURA/PAGA_TAXA, ambos condicionais, entrada (CAPTA_A_VIBE), precedencia, SEISSETE |
| `03_erro_lexico.a67` | invalido | caractere invalido (`$`) |
| `04_erro_sintatico.a67` | invalido | falta a virgula obrigatoria em `FARMA_AURA` |
| `05_erro_semantico.a67` | invalido | uso de variavel nao declarada |

Os dois casos validos sao de fato compilados para Python e executados
por `run_tests.sh` (o teste 2 le uma entrada via `CAPTA_A_VIBE`, por
isso o script alimenta um valor fixo via stdin); os tres casos
invalidos tem a mensagem de erro exata (`[Fase] linha L: mensagem`)
capturada em `tests/generated_errors/`.

## Uso de IA

Este trabalho foi desenvolvido com apoio do Claude (Anthropic) como
assistente de programacao: discussao e validacao do tema, da
gramatica EBNF, implementacao do lexer/parser/analisador
semantico/gerador de codigo, escrita dos testes e deste relatorio. Todo
o codigo gerado foi revisado, executado e validado manualmente antes
da entrega.
