# ZHORA — Linter y Auditor de Seguridad en Macros C (#define)

**ZHORA** audita macros del preprocesador C para detectar efectos de lado en evaluación múltiple de parámetros, falta de paréntesis defensivos en argumentos y cuerpos, y puntos y coma espurios.

---

## 🎯 Alcance

### Qué cubre
- Linter pedagógico y auditor de seguridad de macros del preprocesador en C (`#define`, reglas `ZH001` a `ZH004`).
- Verificación defensiva de paréntesis en parámetros y cuerpo de macros (`ZH003`, `ZH004`).
- Detección de puntos y coma espurios al final de definiciones de macros (`ZH001`).
- Detección de efectos colaterales indeseados por evaluación múltiple de argumentos en llamadas a macros (`ZH002`).

### Qué no cubre (Límites y Delegación)
- Auditoría de inclusión de cabeceras o dependencias circulares (delegado a `wierzbowski`).
- Traducción de errores del compilador tras la fase de preprocesamiento (delegado a `daedalus` / `esper`).
- Ejecución de código (delegado a `nostromo`).

---

## 📋 Requisitos

### Requisitos de Sistema y Entorno
- Multiplataforma. Python >= 3.10.

### Dependencias Externas y Binarios
- Ninguno obligatorio (análisis estático con Tree-Sitter AST).

### Integración en el Ecosistema
- CLI `zhora`. Plugin registrado en `ripley.plugins` (`macro_security`).

---

## 🚀 Uso Rápido

```bash
# Auditar macros en archivos y carpetas
zhora audit src/
zhora check src/

# Generar informe en formato Markdown
zhora report src/

# Salida estructurada JSON
zhora audit src/ --json
```

---

## 🔍 Reglas Auditadas

- **`ZH001`**: Macros que finalizan con punto y coma (`;`), rompiendo sentencias `if/else`.
- **`ZH002`**: Parámetros evaluados más de una vez (riesgo de side effects con `x++`).
- **`ZH003`**: Parámetros de macro no envueltos individualmente en paréntesis `(x)`.
- **`ZH004`**: Cuerpo de expresión matemática no protegido con paréntesis externos.
