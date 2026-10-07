#!/usr/bin/env bash
# Executa a suite de 5 testes do AURA67 (2 validos + 3 invalidos) e,
# em seguida, os testes unitarios automatizados. Alvo da geracao de
# codigo: Python 3 (nao e mais necessario gcc).

set -u
cd "$(dirname "$0")"

PY=python3
if ! python3 --version 2>&1 | grep -Eq "^Python [0-9]+\.[0-9]+"; then
    PY=python
fi

mkdir -p tests/generated tests/generated_errors

FALHOU=0

echo "=============================================="
echo " AURA67 - suite de testes (alvo: Python 3)"
echo "=============================================="

echo
echo "---- Casos validos ----"
for nome in 01_valido_basico 02_valido_completo; do
    echo
    echo ">> $nome.a67"
    if $PY main.py "tests/$nome.a67" -o "tests/generated/$nome.py" >/dev/null; then
        echo "   compilado em tests/generated/$nome.py"
        echo "   saida da execucao:"
        # 02_valido_completo le um bonus (CAPTA_A_VIBE); alimentamos um valor fixo
        echo "10" | $PY "tests/generated/$nome.py" | sed 's/^/   | /'
    else
        echo "   FALHA: nao deveria ter dado erro de compilacao"
        FALHOU=1
    fi
done

echo
echo "---- Casos invalidos (erro esperado) ----"
for nome in 03_erro_lexico 04_erro_sintatico 05_erro_semantico; do
    echo
    echo ">> $nome.a67"
    $PY main.py "tests/$nome.a67" > "tests/generated_errors/$nome.txt" 2>&1
    codigo=$?
    cat "tests/generated_errors/$nome.txt" | sed 's/^/   | /'
    if [ "$codigo" -eq 0 ]; then
        echo "   FALHA: era esperado um erro, mas a compilacao deu certo"
        FALHOU=1
    else
        echo "   OK: erro detectado como esperado (saida em tests/generated_errors/$nome.txt)"
    fi
done

echo
echo "---- Testes unitarios ----"
$PY -m unittest tests.test_transpilador -v
if [ $? -ne 0 ]; then
    FALHOU=1
fi

echo
if [ "$FALHOU" -eq 0 ]; then
    echo "RESULTADO: todos os testes passaram."
else
    echo "RESULTADO: houve falhas, veja acima."
fi
exit $FALHOU
