"""Tests unitarios y de integración para ZHORA."""

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


def test_ripley_plugin(tmp_path):
    h = tmp_path / "plugin.h"
    h.write_text("#define OK (1)\n")
    plugin = ZhoraPlugin()
    res = plugin.run({"source_dir": str(tmp_path)})
    assert res["passed"] is True
    assert "issues" in res
