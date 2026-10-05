"""ZH005 (QoL #1089) y la función static inline equivalente (QoL #1088)."""

import pytest

from zhora.core.macro_linter import es_multisentencia, lint_file_macros, sugerir_inline


@pytest.mark.parametrize("cuerpo, esperado", [
    ("a = 1; b = 2", True),
    ("{ a = 1; b = 2; }", True),
    ("x = 1; \\\n y = 2", True),
    ("do { a = 1; b = 2; } while (0)", False),
    ("do { \\\n a = 1; \\\n } while(0)", False),
    ("((a) + (b))", False),
    ('printf("a; b")', False),
])
def test_multisentencia(cuerpo, esperado):
    assert es_multisentencia(cuerpo) is esperado


def test_sugerencia_inline():
    assert sugerir_inline("CUADRADO", ["x"], "((x) * (x))") == (
        "static inline int cuadrado(int x)  /* ajustá los tipos */\n{\n    return x * x;\n}")
    assert sugerir_inline("SWAP", ["a", "b"], "do { int t = a; a = b; b = t; } while (0)") is None
    assert sugerir_inline("STR", ["x"], "#x") is None


def test_en_un_archivo(tmp_path):
    f = tmp_path / "m.h"
    f.write_text("#define INIT(v) v = 0; contador++\n#define BIEN(v) do { v = 0; } while (0)\n#define DOBLE(x) x * 2\n",
                 encoding="utf-8")
    issues = lint_file_macros(f)
    zh005 = [i.macro_name for i in issues if i.code == "ZH005"]
    assert zh005 == ["INIT"]
    doble = [i for i in issues if i.macro_name == "DOBLE" and i.code == "ZH004"]
    assert doble and doble[0].suggested_inline.startswith("static inline int doble(int x)")
