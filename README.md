# ZHORA — Linter y Auditor de Seguridad en Macros C (#define)

> 📖 **Manual de Usuario:** Para una guía exhaustiva de comandos, banderas, arquitectura y ejemplos, consultá el [Manual de Uso](MANUAL.md).

**ZHORA** audita macros del preprocesador C para detectar efectos de lado en evaluación múltiple de parámetros, falta de paréntesis defensivos en argumentos y cuerpos, y puntos y coma espurios.

---

## 🎯 Alcance

### Qué cubre
- Linter pedagógico y auditor de seguridad de macros del preprocesador en C (`#define`, reglas `ZH001` a `ZH005`).
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
- **`ZH005`**: Macros de varias sentencias (o con un bloque `{ }` suelto) sin `do { ... } while (0)`: dentro de un `if` sin llaves solo la primera sentencia queda condicionada.

En `ZH002`, `ZH003` y `ZH004` el hallazgo trae además la función `static inline` equivalente
(`suggested_inline` en el JSON), con `int` como tipo provisorio para ajustar.

<!-- p1:referencia:inicio — generado por p1-tools/scripts/readme_generado.py: no editar a mano -->

## Referencia rápida

### Requisitos

- Python ≥ 3.11 y [uv](https://docs.astral.sh/uv/getting-started/installation/).

### Comandos

| Comando | Descripción |
|:--|:--|
| `zhora check`, `zhora audit` | Audita macros #define en busca de efectos de lado, falta de paréntesis o puntos y coma. |
| `zhora report` | Genera directamente la sección de reporte Markdown de ZHORA para Dredd. |
| `zhora catalog`, `zhora rules` | Muestra el catálogo oficial de reglas de macros de ZHORA y su mapeo al namespace de cátedra. |
| `zhora doctor` | Verifica el estado del entorno de auditoría de macros ZHORA (Tree-Sitter C, Python). |

Ayuda de cada comando: `zhora <comando> -h`.

### Salida JSON

Con `--json`, estos comandos emiten el resultado como JSON por la salida estándar, para usarlo desde scripts, ripley o dredd: `zhora check`, `zhora audit`, `zhora catalog`, `zhora rules`, `zhora doctor`. El de `doctor --json` lleva `schema_version` y `ok`.

### Códigos de salida

| Código | Significado |
|:--|:--|
| `0` | Terminó bien (en `doctor`: está todo lo requerido). |
| `1` | El comando encontró problemas (hallazgos, pruebas que fallan, un umbral que no se alcanza) o un dato no se pudo usar (un archivo ilegible, un formato inválido). |
| `2` | Error de uso: comando, opción o argumento inválido. |

<!-- p1:referencia:fin -->
