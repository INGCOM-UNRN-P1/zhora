# Manual de Uso y Referencia Técnica: zhora

> **ZHORA** — Linter y auditor de seguridad en macros del preprocesador C (#define)
> **Versión:** `0.1.0` · **CLI principal:** `zhora` · **Plugin Ripley:** `macro_security`

---

## 1. Arquitectura y Propósito Pedagógico

`zhora` forma parte del ecosistema de herramientas de la cátedra de Programación 1 (UNRN). Su objetivo central es resolver de forma modular, determinista y automatizada las tareas asociadas a su dominio específico dentro del ciclo de desarrollo, evaluación y aprendizaje de software en C.

### Alcance Funcional (Qué cubre)
- Linter pedagógico y auditor de seguridad de macros del preprocesador en C (`#define`, reglas `ZH001` a `ZH004`).
- Verificación defensiva de paréntesis en parámetros y cuerpo de macros (`ZH003`, `ZH004`).
- Detección de puntos y coma espurios al final de definiciones de macros (`ZH001`).
- Detección de efectos colaterales indeseados por evaluación múltiple de argumentos en llamadas a macros (`ZH002`).

### Límites de Responsabilidad y Delegación (Qué no cubre)
- Auditoría de inclusión de cabeceras o dependencias circulares (delegado a `wierzbowski`).
- Traducción de errores del compilador tras la fase de preprocesamiento (delegado a `daedalus` / `esper`).
- Ejecución de código (delegado a `nostromo`).

### Principios de Diseño
- **Enfoque Pedagógico:** Diagnósticos y mensajes en español rioplatense orientados a facilitar la comprensión de errores conceptuales.
- **Salida Estructurada Dual:** Soporte nativo para visualización enriquecida en terminal (Rich) y salida parseable para orquestadores (`--json`).
- **Integración Contractual:** Capacidad de emitir secciones de reporte para `dredd` (`dredd-section`) y actuar como satélite orquestado por `ripley`.
- **Idempotencia y Robustez:** Validación de precondiciones y comandos de autodiagnóstico (`doctor`) para verificación del entorno.

---

## 2. Instalación y Requisitos

### Requisitos del Sistema
- **Python:** `>= 3.10` (recomendado Python 3.11 o 3.12).
- **Gestor de paquetes:** [`uv`](https://github.com/astral-sh/uv) (entorno estándar de cátedra).
- **Toolchain C (si aplica):** GCC / Clang, Make, GDB y bibliotecas estándar de desarrollo.

### Instalación en el Entorno de Usuario
Para instalar la herramienta de forma global y aislada en el sistema mediante `uv tool`:
```bash
uv tool install --editable /home/mrtin/dev/tools/zhora
```

### Verificación de Instalación
Ejecutá el comando `doctor` para constatar que todas las dependencias y binarios requeridos estén presentes y operativos:
```bash
zhora doctor
```

---

## 3. Guía Integral de Comandos (CLI)

| Comando | Descripción Breve |
| :--- | :--- |
| [`zhora check`](#check) | Audita macros #define en busca de efectos de lado, falta de paréntesis o puntos y coma. |
| [`zhora audit`](#audit) | Audita macros #define en busca de efectos de lado, falta de paréntesis o puntos y coma. |
| [`zhora report`](#report) | Genera directamente la sección de reporte Markdown de ZHORA para Dredd. |
| [`zhora catalog`](#catalog) | Muestra el catálogo oficial de reglas de macros de ZHORA y su mapeo al namespace de cátedra. |
| [`zhora rules`](#rules) | Muestra el catálogo oficial de reglas de macros de ZHORA y su mapeo al namespace de cátedra. |
| [`zhora doctor`](#doctor) | Verifica el estado del entorno de auditoría de macros ZHORA (Tree-Sitter C, Python). |
| [`zhora version`](#version) | Muestra la versión de ZHORA. |

### `zhora check`

Audita macros #define en busca de efectos de lado, falta de paréntesis o puntos y coma.

Exit code: 1 solo si hay hallazgos de severidad ERROR (ZH001, ZH003); los WARNING
(ZH002, ZH004) se informan pero salen con 0.

#### Argumentos
| Argumento | Tipo | Descripción |
| :--- | :--- | :--- |
| `paths` | `List[pathlib._local.Path]` | Archivos o directorios C a analizar |

#### Opciones y Banderas
| Opción / Banderas | Tipo | Por Defecto | Descripción |
| :--- | :--- | :--- | :--- |
| `--json` | `<class 'bool'>` | `False` | Emitir salida en formato JSON estructurado |
| `--md`, `--output-md` | `Optional[pathlib._local.Path]` | `None` | Generar sección de reporte en formato Markdown para fusión en Dredd. |

#### Ejemplo de Invocación
```bash
zhora check <paths>
```

### `zhora audit`

Audita macros #define en busca de efectos de lado, falta de paréntesis o puntos y coma.

Exit code: 1 solo si hay hallazgos de severidad ERROR (ZH001, ZH003); los WARNING
(ZH002, ZH004) se informan pero salen con 0.

#### Argumentos
| Argumento | Tipo | Descripción |
| :--- | :--- | :--- |
| `paths` | `List[pathlib._local.Path]` | Archivos o directorios C a analizar |

#### Opciones y Banderas
| Opción / Banderas | Tipo | Por Defecto | Descripción |
| :--- | :--- | :--- | :--- |
| `--json` | `<class 'bool'>` | `False` | Emitir salida en formato JSON estructurado |
| `--md`, `--output-md` | `Optional[pathlib._local.Path]` | `None` | Generar sección de reporte en formato Markdown para fusión en Dredd. |

#### Ejemplo de Invocación
```bash
zhora audit <paths>
```

### `zhora report`

Genera directamente la sección de reporte Markdown de ZHORA para Dredd.

#### Argumentos
| Argumento | Tipo | Descripción |
| :--- | :--- | :--- |
| `paths` | `List[pathlib._local.Path]` | Archivos o directorios C a analizar |

#### Opciones y Banderas
| Opción / Banderas | Tipo | Por Defecto | Descripción |
| :--- | :--- | :--- | :--- |
| `--output`, `-o` | `Optional[pathlib._local.Path]` | `None` | Ruta de destino del archivo Markdown. |

#### Ejemplo de Invocación
```bash
zhora report <paths>
```

### `zhora catalog`

Muestra el catálogo oficial de reglas de macros de ZHORA y su mapeo al namespace de cátedra.

#### Opciones y Banderas
| Opción / Banderas | Tipo | Por Defecto | Descripción |
| :--- | :--- | :--- | :--- |
| `--json`, `-j` | `<class 'bool'>` | `False` | Emite el catálogo de reglas de macros en formato JSON versionado. |

#### Ejemplo de Invocación
```bash
zhora catalog
```

### `zhora rules`

Muestra el catálogo oficial de reglas de macros de ZHORA y su mapeo al namespace de cátedra.

#### Opciones y Banderas
| Opción / Banderas | Tipo | Por Defecto | Descripción |
| :--- | :--- | :--- | :--- |
| `--json`, `-j` | `<class 'bool'>` | `False` | Emite el catálogo de reglas de macros en formato JSON versionado. |

#### Ejemplo de Invocación
```bash
zhora rules
```

### `zhora doctor`

Verifica el estado del entorno de auditoría de macros ZHORA (Tree-Sitter C, Python).

#### Opciones y Banderas
| Opción / Banderas | Tipo | Por Defecto | Descripción |
| :--- | :--- | :--- | :--- |
| `--json` | `<class 'bool'>` | `False` | Emitir diagnóstico en formato JSON estructurado. |

#### Ejemplo de Invocación
```bash
zhora doctor
```

### `zhora version`

Muestra la versión de ZHORA.

#### Ejemplo de Invocación
```bash
zhora version
```

---

## 4. Formatos de Salida e Integración con el Ecosistema

### Modo Interactivo / Terminal (Rich)
Por defecto, la herramienta renderiza paneles, árboles y tablas estilizadas para facilitar la lectura del estudiante y docente en terminales modernas con soporte ANSI.

### Modo Estructurado JSON (`--json`)
Para integración con pipelines de CI/CD, scripts de automatización u orquestadores externos, la opción `--json` emite un documento JSON estricto por la salida estándar (`stdout`), dirigiendo cualquier mensaje de logging a `stderr`:
```bash
zhora check --json
```

### Integración con Dredd (`dredd-section`)
Cuando la herramienta genera reportes de evaluación para entregas de alumnos, produce una sección Markdown estandarizada conforme al contrato de integración de Dredd (v1.0.0):
```markdown
<!-- dredd-section: zhora, tool=zhora, version=0.1.0, status=ok -->
```
Este encabezado garantiza la agregación determinista de los hallazgos en la rúbrica docente.

### Integración con Ripley
`zhora` está registrada en el catálogo de plugins satélites de Ripley (`SATELLITE_CATALOG`). Puede invocarse directamente a través del motor de evaluación de Ripley configurando el análisis en `ripley.toml`.

---

## 5. Diagnóstico y Códigos de Salida

### Códigos de Retorno (`exit code`)
| Código | Significado |
| :---: | :--- |
| `0` | Ejecución exitosa sin hallazgos críticos ni errores de sintaxis. |
| `1` | Hallazgos pedagógicos detectados, infracción de reglas o advertencias activas. |
| `2` | Error de sintaxis en argumentos CLI o archivo fuente no encontrado. |
| `>2` | Error no recuperable del sistema, fallo de memoria o excepción interna. |

### Diagnóstico del Entorno (`doctor`)
Ante comportamientos inesperados, verificá el estado operativo con:
```bash
zhora doctor
```
Comprueba la presencia de las dependencias requeridas y la integridad de los componentes del paquete.