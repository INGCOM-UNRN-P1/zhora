# ZHORA — Linter y Auditor de Seguridad en Macros C (#define)

**ZHORA** audita macros del preprocesador C para detectar efectos de lado en evaluación múltiple de parámetros, falta de paréntesis defensivos en argumentos y cuerpos, y puntos y coma espurios.

---

## 🎯 Alcance

### Qué cubre
- Linter pedagógico y auditor de seguridad de macros del preprocesador en C (`#define`, reglas `0x40XXh`).
- Verificación obligatoria de paréntesis defensivos en parámetros y cuerpo de macros (`0x4001h`).
- Exigencia de nomenclatura en mayúsculas (`UPPER_SNAKE_CASE`) para identificadores de macros (`0x4002h`).
- Exigencia de encapsulamiento en bloques `do { ... } while(0)` para macros multisentencia (`0x4003h`).
- Detección de efectos colaterales indeseados por evaluación múltiple de argumentos en llamadas a macros.

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

# Salida estructurada JSON
zhora audit src/ --json
```

---

## 🔍 Reglas Auditadas

- **`ZH001`**: Macros que finalizan con punto y coma (`;`), rompiendo sentencias `if/else`.
- **`ZH002`**: Parámetros evaluados más de una vez (riesgo de side effects con `x++`).
- **`ZH003`**: Parámetros de macro no envueltos individualmente en paréntesis `(x)`.
- **`ZH004`**: Cuerpo de expresión matemática no protegido con paréntesis externos.
