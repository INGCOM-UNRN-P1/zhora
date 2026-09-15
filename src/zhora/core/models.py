"""Modelos de datos para el análisis de macros en ZHORA."""

from typing import List, Optional
from pydantic import BaseModel, Field


class MacroIssue(BaseModel):
    code: str
    severity: str  # "ERROR", "WARNING", "INFO"
    macro_name: str
    file_path: str
    line_number: int
    raw_macro: str
    message: str
    suggestion: str
    suggested_inline: Optional[str] = None


class MacroAuditReport(BaseModel):
    schema_version: str = "1.0.0"
    total_files_scanned: int = 0
    total_macros_scanned: int = 0
    issues: List[MacroIssue] = Field(default_factory=list)
    passed: bool = True
