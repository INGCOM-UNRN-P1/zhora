"""Linter de macros C (#define) y análisis de efectos colaterales."""

import re
from pathlib import Path
from typing import List, Tuple
from zhora.core.models import MacroIssue

# Patrón para capturar #define con o sin parámetros
MACRO_DEF_PATTERN = re.compile(
    r'^\s*#\s*define\s+([a-zA-Z_][a-zA-Z0-9_]*)(?:\(([^)]*)\))?\s+(.+)$',
    re.MULTILINE
)


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

        # ZH002: Parámetros no encerrados entre paréntesis en el cuerpo
        for p in params:
            # Buscar el parámetro aislado no precedido/seguido por '(' o ')'
            param_usage = re.findall(rf'(?<![a-zA-Z0-9_\(\)]){re.escape(p)}(?![a-zA-Z0-9_\(\)])', body_clean)
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
                    suggestion=f"Reemplazá la macro por una función 'static inline' o asegurate de que los argumentos se evalúen una única vez."
                ))

            # Verificar si no está encerrado entre paréntesis defensivos
            if f"({p})" not in body_clean:
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
    """Escanea y audita todas las macros en un archivo C o H."""
    issues = []
    content = file_path.read_text(encoding="utf-8", errors="replace")
    lines = content.splitlines()

    for idx, line in enumerate(lines, 1):
        stripped = line.strip()
        if not stripped.startswith("#"):
            continue

        match = MACRO_DEF_PATTERN.match(line)
        if match:
            name = match.group(1)
            params = match.group(2)
            body = match.group(3)
            issues.extend(lint_macro_definition(
                name, params, body, str(file_path), idx, stripped
            ))

    return issues
