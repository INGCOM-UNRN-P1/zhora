"""CLI principal de ZHORA."""

import json
from pathlib import Path
from typing import List, Optional
import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from zhora.core.models import MacroAuditReport
from zhora.core.macro_linter import lint_file_macros

app = typer.Typer(
    name="zhora",
    help="Linter y auditor de seguridad en macros del preprocesador C (#define)",
    add_completion=True
)
console = Console()


@app.command()
def audit(
    paths: List[Path] = typer.Argument(..., help="Archivos o directorios C a analizar"),
    json_output: bool = typer.Option(False, "--json", help="Emitir salida en formato JSON estructurado")
):
    """Audita macros #define en busca de efectos de lado, falta de paréntesis o puntos y coma."""
    files_to_check: List[Path] = []
    for p in paths:
        if p.is_file():
            files_to_check.append(p)
        elif p.is_dir():
            files_to_check.extend(list(p.glob("**/*.h")) + list(p.glob("**/*.c")))

    if not files_to_check:
        console.print("[yellow]No se encontraron archivos C/H para auditar macros.[/yellow]")
        raise typer.Exit(code=0)

    all_issues = []
    for f in files_to_check:
        all_issues.extend(lint_file_macros(f))

    has_errors = any(i.severity == "ERROR" for i in all_issues)
    report = MacroAuditReport(
        total_files_scanned=len(files_to_check),
        total_macros_scanned=len(all_issues),
        issues=all_issues,
        passed=not has_errors
    )

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


@app.command()
def version():
    """Muestra la versión de ZHORA."""
    from zhora import __version__
    console.print(f"[bold cyan]ZHORA[/bold cyan] versión [green]{__version__}[/green]")


if __name__ == "__main__":
    app()
