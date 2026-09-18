"""Regresión de ZHORA-D0302: ZH003 comparaba por subcadena.

`f"({p})" not in body` marcaba `(++x)` (falso positivo) y no marcaba
`((x) + x)`, que tiene un uso sin proteger (falso negativo).
"""

import pytest

from zhora.core.macro_linter import _usos_sin_proteger, lint_file_macros


def _codigos(tmp_path, definicion):
    h = tmp_path / "m.h"
    h.write_text(definicion + "\n", encoding="utf-8")
    return {i.code for i in lint_file_macros(h)}


@pytest.mark.parametrize(
    "definicion",
    [
        "#define INC(x) (++x)",
        "#define DEC(x) (x--)",
        "#define CUAD(x) ((x) * (x))",
        "#define LLAMA(x) (foo(x))",
        "#define LLAMA2(x, y) (foo(x, y))",
        "#define IDX(a, i) ((a)[i])",
        "#define TXT(x) (#x)",
        "#define PEGA(a, b) (a##b)",
        '#define LIT(x) ((x) + sizeof("x"))',
        "#define CAMPO(x) ((x).campo)",
        "#define SIG(x) (sizeof(x))",
    ],
)
def test_no_se_reporta_ZH003_cuando_todos_los_usos_estan_protegidos(tmp_path, definicion):
    assert "ZH003" not in _codigos(tmp_path, definicion)


@pytest.mark.parametrize(
    "definicion",
    [
        "#define MULT(a, b) a * b",
        "#define MEZCLA(x) ((x) + x)",
        "#define CAMPO(x) (x.campo)",
        "#define ID(x) x",
        "#define SUMA1(x) (x + 1)",
    ],
)
def test_se_reporta_ZH003_si_algun_uso_queda_sin_proteger(tmp_path, definicion):
    assert "ZH003" in _codigos(tmp_path, definicion)


def test_un_parametro_dentro_de_un_literal_no_cuenta_como_uso():
    assert _usos_sin_proteger("x", '((x) + sizeof("x y"))') == 0


def test_la_continuacion_de_linea_no_rompe_la_deteccion():
    assert _usos_sin_proteger("x", "((x) + \\\n x)") == 1
