"""Plugin de ZHORA para el microkernel RIPLEY."""

from pathlib import Path
from typing import Dict, Any
from zhora import __version__
from zhora.core.macro_linter import lint_file_macros


class ZhoraPlugin:
    """Plugin de auditoría de macros para Ripley."""

    name = "macro_security"
    description = "Auditor de seguridad en macros del preprocesador (#define, efectos de lado, paréntesis)"

    version = __version__

    def is_available(self) -> bool:
        return True

    def execute(self, workspace: Path, manifest_config: Dict[str, Any]) -> Dict[str, Any]:
        """Firma común de los satélites de ripley (igual que kaneda/spunkmeyer)."""
        return self.run({"source_dir": str(workspace)})

    def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        source_dir = Path(context.get("source_dir", "."))
        files = list(source_dir.glob("**/*.h")) + list(source_dir.glob("**/*.c"))

        all_issues = []
        has_critical = False

        for f in files:
            issues = lint_file_macros(f)
            for iss in issues:
                if iss.severity == "ERROR":
                    has_critical = True
                all_issues.append({
                    "code": iss.code,
                    "severity": iss.severity,
                    "macro": iss.macro_name,
                    "file": f.name,
                    "line": iss.line_number,
                    "message": iss.message,
                    "suggestion": iss.suggestion
                })

        return {
            "passed": not has_critical,
            "issues_count": len(all_issues),
            "issues": all_issues
        }
