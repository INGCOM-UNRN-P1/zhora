"""CLI principal de ZHORA."""

import json
from pathlib import Path
from typing import List, Optional
import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from zhora.core.models import MacroAuditReport
from zhora.core.macro_linter import escanear_macros

app = typer.Typer(
    name="zhora",
    help="Linter y auditor de seguridad en macros del preprocesador C (#define)",
    add_completion=True
)
console = Console()

SUFIJOS_C = {".c", ".h"}


def _version_callback(value: bool) -> None:
    if value:
        from zhora import __version__
        typer.echo(f"zhora {__version__}")
        raise typer.Exit()


@app.callback()
def main_callback(
    version: Optional[bool] = typer.Option(
        None, "--version", "-v", callback=_version_callback, is_eager=True,
        help="Muestra la versión de zhora y sale.",
    ),
) -> None:
    """Linter y auditor de seguridad en macros del preprocesador C (#define)."""


def _recolectar_archivos(paths: List[Path]) -> List[Path]:
    """Archivos .c/.h a analizar: los directorios se recorren; un archivo explícito debe ser C/H."""
    files: List[Path] = []
    for p in paths:
        if p.is_file():
            if p.suffix.lower() in SUFIJOS_C:
                files.append(p)
            else:
                console.print(f"[yellow]Se ignora '{p}': no es un archivo .c/.h.[/yellow]")
        elif p.is_dir():
            files.extend(sorted(list(p.glob("**/*.h")) + list(p.glob("**/*.c"))))
    return files


def _auditar(files: List[Path]) -> MacroAuditReport:
    all_issues = []
    total_macros = 0
    for f in files:
        issues, n = escanear_macros(f)
        all_issues.extend(issues)
        total_macros += n
    has_errors = any(i.severity == "ERROR" for i in all_issues)
    return MacroAuditReport(
        total_files_scanned=len(files),
        total_macros_scanned=total_macros,
        issues=all_issues,
        passed=not has_errors,
    )


def generar_seccion_markdown(report: MacroAuditReport) -> str:
    """Genera sección de auditoría de seguridad en macros para Dredd."""
    lines = [
        "<!-- dredd-section: zhora v1.0.0 -->\n",
        "## Seguridad en Macros del Preprocesador (Zhora)\n",
    ]
    lines.append(f"- **Archivos escaneados:** {report.total_files_scanned}")
    lines.append(f"- **Problemas en macros:** {len(report.issues)}\n")
    if report.passed:
        lines.append("> [!TIP]\n> **Macros Seguras:** Todas las directivas `#define` están debidamente parentizadas y libres de efectos de lado o punto y coma espurios.\n")
    else:
        lines.append("> [!WARNING]\n> **Riesgo en Macros del Preprocesador:**\n")
        lines.append("| Macro | Ubicación | Código | Severidad | Diagnóstico | Sugerencia |")
        lines.append("| :--- | :--- | :---: | :---: | :--- | :--- |")
        for iss in report.issues:
            mac_limpio = iss.macro_name.replace("|", "&#124;")
            loc_limpio = f"{Path(iss.file_path).name}:{iss.line_number}".replace("|", "&#124;")
            msg_limpio = iss.message.replace("|", "&#124;")
            sug_limpio = iss.suggestion.replace("|", "&#124;")
            lines.append(f"| `{mac_limpio}` | `{loc_limpio}` | `{iss.code}` | **{iss.severity}** | {msg_limpio} | {sug_limpio} |")
        lines.append("")
    return "\n".join(lines)


@app.command("audit")
@app.command("check")
def audit(
    paths: List[Path] = typer.Argument(..., help="Archivos o directorios C a analizar"),
    json_output: bool = typer.Option(False, "--json", help="Emitir salida en formato JSON estructurado"),
    output_md: Optional[Path] = typer.Option(None, "--md", "--output-md", help="Generar sección de reporte en formato Markdown para fusión en Dredd."),
):
    """Audita macros #define en busca de efectos de lado, falta de paréntesis o puntos y coma.

    Exit code: 1 solo si hay hallazgos de severidad ERROR (ZH001, ZH003); los WARNING
    (ZH002, ZH004) se informan pero salen con 0.
    """
    files_to_check = _recolectar_archivos(paths)

    if not files_to_check:
        console.print("[yellow]No se encontraron archivos C/H para auditar macros.[/yellow]")
        raise typer.Exit(code=0)

    report = _auditar(files_to_check)
    all_issues = report.issues

    if output_md:
        md_text = generar_seccion_markdown(report)
        output_md.parent.mkdir(parents=True, exist_ok=True)
        output_md.write_text(md_text, encoding="utf-8")
        console.print(f"[bold green]✓ Sección Markdown generada en:[/bold green] {output_md}")
        raise typer.Exit(code=0 if report.passed else 1)

    if json_output:
        print(json.dumps(report.model_dump(), indent=2, ensure_ascii=False))
        if not report.passed:
            raise typer.Exit(code=1)
        return

    if not all_issues:
        console.print(Panel(
            f"[bold green]✓ Macros 100% Seguras y Defensivas[/bold green]\n"
            f"• Archivos analizados: {len(files_to_check)}\n"
            f"• No se detectaron efectos de lado ni errores de precedencia en #define.",
            title="[bold green]ZHORA Macro Security[/bold green]"
        ))
        return

    table = Table(title="Auditoría de Seguridad en Macros (#define)", show_header=True, header_style="bold magenta")
    table.add_column("Código", style="cyan", width=8)
    table.add_column("Sev", style="bold", width=8)
    table.add_column("Macro", style="yellow")
    table.add_column("Ubicación", style="blue")
    table.add_column("Diagnóstico y Sugerencia", style="white")

    for iss in all_issues:
        sev_color = "red" if iss.severity == "ERROR" else "yellow"
        table.add_row(
            iss.code,
            f"[{sev_color}]{iss.severity}[/{sev_color}]",
            iss.macro_name,
            f"{Path(iss.file_path).name}:{iss.line_number}",
            f"{iss.message}\n[dim]↳ Sugerencia: {iss.suggestion}[/dim]"
        )

    console.print(table)
    if not report.passed:
        raise typer.Exit(code=1)


@app.command("report")
def report_cmd(
    paths: List[Path] = typer.Argument(..., help="Archivos o directorios C a analizar"),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Ruta de destino del archivo Markdown."),
):
    """Genera directamente la sección de reporte Markdown de ZHORA para Dredd."""
    files_to_check: List[Path] = []
    for p in paths:
        if p.is_file():
            files_to_check.append(p)
        elif p.is_dir():
            files_to_check.extend(list(p.glob("**/*.h")) + list(p.glob("**/*.c")))

    report = _auditar(files_to_check)
    all_issues = report.issues
    md_content = generar_seccion_markdown(report)
    if output:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(md_content, encoding="utf-8")
        console.print(f"[bold green]✓ Reporte Markdown generado en:[/bold green] {output}")
    else:
        print(md_content)


CATALOGO_REGLAS_ZHORA = {
    "ZH001": {
        "code": "ZH001",
        "alias_catedra": "0x500Dh",
        "title": "Punto y coma final espurio",
        "severity": "ERROR",
        "description": "Macro que finaliza con punto y coma (;), rompiendo sentencias if/else y bloques de control.",
        "suggestion": "Eliminá el ';' final de la definición de la macro.",
    },
    "ZH002": {
        "code": "ZH002",
        "alias_catedra": "0x500Ah",
        "title": "Evaluación múltiple de parámetros",
        "severity": "WARNING",
        "description": "Parámetro evaluado más de una vez en la macro, causando efectos colaterales si el argumento contiene expresiones como x++.",
        "suggestion": "Evaluá convertir la macro a función 'static inline' o almacená el parámetro en una variable temporal.",
    },
    "ZH003": {
        "code": "ZH003",
        "alias_catedra": "0x0013h",
        "title": "Parámetros sin paréntesis defensivos",
        "severity": "WARNING",
        "description": "Parámetro de macro no envuelto individualmente en paréntesis (x), generando precedencia de operadores errónea.",
        "suggestion": "Envolvé cada ocurrencia del parámetro entre paréntesis: (x).",
    },
    "ZH004": {
        "code": "ZH004",
        "alias_catedra": "0x0013h",
        "title": "Cuerpo de expresión sin paréntesis globales",
        "severity": "WARNING",
        "description": "Cuerpo global de expresión matemática o lógica no protegido con paréntesis externos.",
        "suggestion": "Envolvé toda la expresión de sustitución de la macro entre paréntesis: ((a) + (b)).",
    },
}


@app.command("rules")
@app.command("catalog")
def rules_cmd(
    json_output: bool = typer.Option(False, "--json", "-j", help="Emite el catálogo de reglas de macros en formato JSON versionado."),
) -> None:
    """Muestra el catálogo oficial de reglas de macros de ZHORA y su mapeo al namespace de cátedra."""
    if json_output:
        payload = {
            "schema_version": "1.0.0",
            "herramienta": "zhora",
            "namespace_prefijo": "ZH",
            "total_reglas": len(CATALOGO_REGLAS_ZHORA),
            "reglas": list(CATALOGO_REGLAS_ZHORA.values()),
        }
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return

    tabla = Table(title=f"Catálogo de Reglas de Macros — ZHORA ({len(CATALOGO_REGLAS_ZHORA)} reglas)")
    tabla.add_column("Código", style="bold cyan", justify="center")
    tabla.add_column("Alias Cátedra", style="bold yellow", justify="center")
    tabla.add_column("Severidad", justify="center")
    tabla.add_column("Título", style="bold")
    tabla.add_column("Descripción")

    for r in CATALOGO_REGLAS_ZHORA.values():
        sev_style = "bold red" if r["severity"] == "ERROR" else "bold yellow"
        tabla.add_row(r["code"], r["alias_catedra"], f"[{sev_style}]{r['severity']}[/{sev_style}]", r["title"], r["description"])

    console.print(tabla)


@app.command("doctor")
def doctor_cmd(
    json_output: bool = typer.Option(False, "--json", help="Emitir diagnóstico en formato JSON estructurado."),
) -> None:
    """Verifica el estado del entorno de auditoría de macros ZHORA (Tree-Sitter C, Python)."""
    import sys
    diagnostico = []

    py_ok = sys.version_info >= (3, 10)
    diagnostico.append({
        "componente": "Python Runtime",
        "estado": "OK" if py_ok else "ERROR",
        "requerido": True,
        "detalle": f"Python {sys.version.split()[0]}",
    })

    ts_ok = False
    try:
        from zhora.core.macro_linter import get_c_parser
        get_c_parser()
        ts_ok = True
        ts_det = "Gramática C AST cargada exitosamente"
    except Exception as e:
        ts_det = str(e)
    diagnostico.append({
        "componente": "Tree-Sitter C Parser",
        "estado": "OK" if ts_ok else "ERROR",
        "requerido": True,
        "detalle": ts_det,
    })

    todo_ok = py_ok and ts_ok

    if json_output:
        payload = {
            "schema_version": "1.0.0",
            "herramienta": "zhora",
            "ok": todo_ok,
            "componentes": diagnostico,
        }
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        raise typer.Exit(code=0 if todo_ok else 1)

    tabla = Table(title="🏥 Diagnóstico del Entorno ZHORA (doctor)", border_style="cyan")
    tabla.add_column("Componente", style="bold white")
    tabla.add_column("Estado", justify="center")
    tabla.add_column("Detalle")

    for c in diagnostico:
        color = "bold green" if c["estado"] == "OK" else "bold red"
        simbolo = "✓" if c["estado"] == "OK" else "✗"
        tabla.add_row(c["componente"], f"[{color}]{simbolo} {c['estado']}[/{color}]", c["detalle"])

    console.print(tabla)
    if not todo_ok:
        console.print("\n[bold red]Ejecutá `pip install tree-sitter tree-sitter-c` para reparar dependencias faltantes.[/bold red]")
        raise typer.Exit(code=1)


@app.command(hidden=True)
def version():
    """Muestra la versión de ZHORA."""
    from zhora import __version__
    console.print(f"[bold cyan]ZHORA[/bold cyan] versión [green]{__version__}[/green]")


if __name__ == "__main__":
    app()
