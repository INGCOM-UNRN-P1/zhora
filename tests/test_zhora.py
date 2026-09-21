"""Tests unitarios y de integración para ZHORA."""

import json
from pathlib import Path
from typer.testing import CliRunner
from zhora.cli import app
from zhora.core.macro_linter import lint_file_macros
from zhora.plugins.ripley_plugin import ZhoraPlugin

runner = CliRunner()


def test_lint_macro_semicolon(tmp_path):
    h = tmp_path / "macro_semi.h"
    h.write_text("#define IMPRIMIR_HOLA() printf(\"Hola\");\n")
    issues = lint_file_macros(h)
    assert any(i.code == "ZH001" for i in issues)


def test_lint_macro_side_effect(tmp_path):
    h = tmp_path / "macro_max.h"
    h.write_text("#define MAX(a, b) (((a) > (b)) ? (a) : (b))\n")
    issues = lint_file_macros(h)
    assert any(i.code == "ZH002" for i in issues)


def test_lint_macro_unparenthesized(tmp_path):
    h = tmp_path / "macro_mult.h"
    h.write_text("#define MULT(a, b) a * b\n")
    issues = lint_file_macros(h)
    assert any(i.code == "ZH003" for i in issues)


def test_lint_safe_macro(tmp_path):
    h = tmp_path / "macro_safe.h"
    h.write_text("#define TAM_MAX (1024)\n")
    issues = lint_file_macros(h)
    assert len(issues) == 0


def test_cli_audit_json(tmp_path):
    h = tmp_path / "test.h"
    h.write_text("#define CONSTANTE (42)\n")
    res = runner.invoke(app, ["audit", str(h), "--json"])
    assert res.exit_code == 0
    assert '"passed": true' in res.output


def test_cli_version():
    res = runner.invoke(app, ["version"])
    assert res.exit_code == 0
    assert "ZHORA" in res.output


def test_cli_doctor():
    res = runner.invoke(app, ["doctor"])
    assert res.exit_code == 0
    assert "doctor" in res.output.lower()

    res_json = runner.invoke(app, ["doctor", "--json"])
    assert res_json.exit_code == 0
    data = json.loads(res_json.output)
    assert data["herramienta"] == "zhora"
    assert data["ok"] is True


def test_ripley_plugin(tmp_path):
    h = tmp_path / "plugin.h"
    h.write_text("#define OK (1)\n")
    plugin = ZhoraPlugin()
    res = plugin.run({"source_dir": str(tmp_path)})
    assert res["passed"] is True
    assert "issues" in res


def test_version_como_opcion_global():
    from zhora import __version__
    for flag in ("--version", "-v"):
        res = runner.invoke(app, [flag])
        assert res.exit_code == 0
        assert __version__ in res.output


def test_total_macros_cuenta_macros_no_hallazgos(tmp_path):
    """ZHORA-D0601: total_macros_scanned era len(issues)."""
    h = tmp_path / "m.h"
    h.write_text("#define A (1)\n#define B (2)\n#define C (3)\n#define MULT(a, b) a * b\n")
    res = runner.invoke(app, ["audit", str(h), "--json"])
    data = json.loads(res.output)
    assert data["total_macros_scanned"] == 4
    assert len(data["issues"]) != 4


def test_archivo_explicito_no_c_se_ignora(tmp_path):
    """ZHORA-D0404: un .txt pasado directo no se analiza."""
    t = tmp_path / "notas.txt"
    t.write_text("#define MULT(a, b) a * b\n")
    res = runner.invoke(app, ["audit", str(t)])
    assert res.exit_code == 0
    assert "MULT" not in res.output.replace("Se ignora", "")
    assert "No se encontraron archivos" in res.output


def test_warnings_no_fallan_el_exit_code(tmp_path):
    """ZHORA-D0403: política documentada: solo ERROR sale 1."""
    h = tmp_path / "w.h"
    h.write_text("#define MAX(a, b) (((a) > (b)) ? (a) : (b))\n")
    res = runner.invoke(app, ["audit", str(h)])
    assert res.exit_code == 0
    assert "ERROR" in runner.invoke(app, ["audit", "--help"]).output


def test_plugin_firma_comun_execute(tmp_path):
    """ZHORA-D0901: execute/is_available como los demás satélites."""
    (tmp_path / "p.h").write_text("#define X(a) a;\n")
    plugin = ZhoraPlugin()
    assert plugin.is_available()
    res = plugin.execute(tmp_path, {})
    assert res["passed"] is False and res["issues_count"] >= 1
