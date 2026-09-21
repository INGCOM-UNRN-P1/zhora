"""Linter de macros C (#define) y análisis de efectos colaterales usando Tree-Sitter AST."""

from __future__ import annotations

import re
from pathlib import Path
from typing import List, Optional, Tuple

import tree_sitter_c as tsc
from tree_sitter import Language, Parser, Node

from zhora.core.models import MacroIssue
from zhora.core.preprocesador import enmascarar_bloques_inactivos

_C_LANGUAGE: Optional[Language] = None
_PARSER: Optional[Parser] = None


def get_c_parser() -> Parser:
    global _C_LANGUAGE, _PARSER
    if _PARSER is None:
        _C_LANGUAGE = Language(tsc.language())
        _PARSER = Parser(_C_LANGUAGE)
    return _PARSER


_LITERAL = re.compile(r"\"(?:\\.|[^\"\\])*\"|'(?:\\.|[^'\\])*'")


def _usos_sin_proteger(param: str, cuerpo: str) -> int:
    """Cuenta los usos de `param` que un argumento con operadores de menor precedencia alteraría.

    Un uso está protegido si es el único contenido de unos paréntesis/corchetes o
    un argumento completo de una llamada (`(x)`, `f(x, y)`, `a[x]`). No se
    reportan los operandos de `#`/`##` (no admiten paréntesis) ni los de `++`/`--`
    (exigen un lvalue, así que un argumento con operadores no compilaría). La
    comprobación previa buscaba la subcadena `(x)` en el cuerpo: `(++x)` la
    incumplía y `((x) + x)` la cumplía pese a tener un uso sin proteger.
    """
    limpio = _LITERAL.sub(lambda m: " " * len(m.group()), cuerpo)
    limpio = re.sub(r"\\\r?\n", "  ", limpio)
    sin_proteger = 0
    for m in re.finditer(rf"\b{re.escape(param)}\b", limpio):
        antes = limpio[:m.start()].rstrip()
        despues = limpio[m.end():].lstrip()
        if antes.endswith("#") or despues.startswith("##"):
            continue
        if antes.endswith(("++", "--")) or despues.startswith(("++", "--")):
            continue
        previo, siguiente = antes[-1:], despues[:1]
        if previo and previo in "([," and siguiente and siguiente in ")],":
            continue
        sin_proteger += 1
    return sin_proteger


def lint_macro_definition(
    macro_name: str,
    params_str: str | None,
    body: str,
    file_path: str,
    line_no: int,
    raw_line: str
) -> List[MacroIssue]:
    """Analiza una definición de macro individual."""
    issues = []
    body_clean = body.strip()

    # Si es macro de guarda de inclusión, ignorar
    if not params_str and not body_clean:
        return []

    # ZH001: Macro con punto y coma final
    if body_clean.endswith(";"):
        issues.append(MacroIssue(
            code="ZH001",
            severity="ERROR",
            macro_name=macro_name,
            file_path=file_path,
            line_number=line_no,
            raw_macro=raw_line,
            message=f"La macro '{macro_name}' finaliza con punto y coma (';').",
            suggestion="Eliminá el punto y coma final del #define para evitar errores sintácticos al invocarla dentro de sentencias if/else."
        ))

    # Si tiene parámetros (macro tipo función)
    if params_str is not None:
        params = [p.strip() for p in params_str.split(",") if p.strip()]

        for p in params:
            # Buscar si el parámetro aparece más de una vez (riesgo de side effects: x++)
            occurrences = len(re.findall(rf'\b{re.escape(p)}\b', body_clean))
            if occurrences > 1:
                issues.append(MacroIssue(
                    code="ZH002",
                    severity="WARNING",
                    macro_name=macro_name,
                    file_path=file_path,
                    line_number=line_no,
                    raw_macro=raw_line,
                    message=f"El parámetro '{p}' se evalúa {occurrences} veces en el cuerpo de la macro (riesgo de efectos de lado con 'x++').",
                    suggestion="Reemplazá la macro por una función 'static inline' o asegurate de que los argumentos se evalúen una única vez."
                ))

            # Verificar si no está encerrado entre paréntesis defensivos
            if _usos_sin_proteger(p, body_clean):
                issues.append(MacroIssue(
                    code="ZH003",
                    severity="ERROR",
                    macro_name=macro_name,
                    file_path=file_path,
                    line_number=line_no,
                    raw_macro=raw_line,
                    message=f"El parámetro '{p}' no está protegido con paréntesis defensivos en '{body_clean}'.",
                    suggestion=f"Escribí '({p})' en cada uso dentro del cuerpo de la macro para evitar alteraciones de precedencia de operadores."
                ))

        # ZH004: Cuerpo global de expresión matemática no protegido
        if any(op in body_clean for op in ['+', '-', '*', '/', '%', '<<', '>>', '&', '|', '^']) and not (body_clean.startswith("(") and body_clean.endswith(")")):
            issues.append(MacroIssue(
                code="ZH004",
                severity="WARNING",
                macro_name=macro_name,
                file_path=file_path,
                line_number=line_no,
                raw_macro=raw_line,
                message=f"El cuerpo completo de la macro '{macro_name}' no está envuelto en paréntesis externos.",
                suggestion=f"Envolvé toda la expresión en '(' y ')': #define {macro_name}(...) ({body_clean})"
            ))

    return issues


def lint_file_macros(file_path: Path) -> List[MacroIssue]:
    """Escanea y audita todas las macros en un archivo C o H usando Tree-Sitter AST."""
    return escanear_macros(file_path)[0]


def escanear_macros(file_path: Path) -> Tuple[List[MacroIssue], int]:
    """Audita un archivo y devuelve (hallazgos, cantidad de macros `#define` analizadas)."""
    issues = []
    total = 0
    content = file_path.read_text(encoding="utf-8", errors="replace")
    # El contenido de un `#if 0` no se compila: enmascararlo evita
    # reportar hallazgos sobre código deliberadamente desactivado.
    content = enmascarar_bloques_inactivos(content)
    source_bytes = content.encode("utf-8")
    parser = get_c_parser()
    tree = parser.parse(source_bytes)

    def _traverse(node: Node) -> None:
        nonlocal total
        if node.type in ("preproc_def", "preproc_function_def"):
            total += 1
            name_node = node.child_by_field_name("name")
            params_node = node.child_by_field_name("parameters")
            val_node = node.child_by_field_name("value")

            macro_name = name_node.text.decode("utf-8", errors="replace") if name_node else "ANON_MACRO"
            params_str = None
            if params_node:
                raw_p = params_node.text.decode("utf-8", errors="replace").strip()
                if raw_p.startswith("(") and raw_p.endswith(")"):
                    raw_p = raw_p[1:-1]
                params_str = raw_p

            body_str = val_node.text.decode("utf-8", errors="replace") if val_node else ""
            line_no = node.start_point.row + 1
            raw_line = node.text.decode("utf-8", errors="replace")

            issues.extend(lint_macro_definition(
                macro_name, params_str, body_str, str(file_path), line_no, raw_line
            ))

        for child in node.children:
            _traverse(child)

    _traverse(tree.root_node)
    return issues, total
