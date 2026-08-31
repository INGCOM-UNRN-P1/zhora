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


def generar_seccion_markdown(report: MacroAuditReport) -> str:
    """Genera sección de auditoría de seguridad en macros para Dredd."""
    lines = ["## Seguridad en Macros del Preprocesador (Zhora)\n"]
    lines.append(f"- **Archivos escaneados:** {report.total_files_scanned}")
    lines.append(f"- **Problemas en macros:** {len(report.issues)}\n")
    if report.passed:
        lines.append("> [!TIP]\n> **Macros Seguras:** Todas las directivas `#define` están debidamente parentizadas y libres de efectos de lado o punto y coma espurios.\n")
    else:
        lines.append("> [!WARNING]\n> **Riesgo en Macros del Preprocesador:**\n")
        lines.append("| Macro | Ubicación | Código | Severidad | Diagnóstico | Sugerencia |")
        lines.append("| :--- | :--- | :---: | :---: | :--- | :--- |")
        for iss in report.issues:
            lines.append(f"| `{iss.macro_name}` | `{Path(iss.file_path).name}:{iss.line_number}` | `{iss.code}` | **{iss.severity}** | {iss.message} | {iss.suggestion} |")
        lines.append("")
    return "\n".join(lines)


@app.command("audit")
@app.command("check")
def audit(
    paths: List[Path] = typer.Argument(..., help="Archivos o directorios C a analizar"),
    json_output: bool = typer.Option(False, "--json", help="Emitir salida en formato JSON estructurado"),
    output_md: Optional[Path] = typer.Option(None, "--md", "--output-md", help="Generar sección de reporte en formato Markdown para fusión en Dredd."),
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
    md_content = generar_seccion_markdown(report)
    if output:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(md_content, encoding="utf-8")
        console.print(f"[bold green]✓ Reporte Markdown generado en:[/bold green] {output}")
    else:
        print(md_content)


@app.command()
def version():
    """Muestra la versión de ZHORA."""
    from zhora import __version__
    console.print(f"[bold cyan]ZHORA[/bold cyan] versión [green]{__version__}[/green]")


if __name__ == "__main__":
    app()
