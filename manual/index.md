---
title: "Manual de Referencia: zhora"
subtitle: "Zhora — Linter y Auditor de Seguridad en Macros del Preprocesador #define"
author: "Cátedra de Algoritmos y Programación"
date: "2026-08-31"
---

(manual-zhora)=
# Zhora — Linter y Auditor de Seguridad en Macros del Preprocesador #define

````{abstract}
**Rol en el ecosistema:** Auditoría de seguridad y buenas prácticas en macros de C: detección de parámetros sin paréntesis defensivos `(x)`, efectos colaterales en argumentos (`MACRO(i++)`), macros con sentencias múltiples sin bloque `do { ... } while(0)` y sugerencia de funciones `inline` / `enum`.
````

---

(manual-zhora-proposito)=
## 1. Propósito y Filosofía Pedagógica

La herramienta **`zhora`** forma parte del ecosistema oficial de software de la cátedra. Su diseño sigue principios pedagógicos rigurosos:

1. **Evidencia Técnica Directa**: Todo diagnóstico se fundamenta en la norma ISO C (C11/C23), en el modelo de memoria del sistema o en convenciones arquitectónicas formales.
2. **Acción Correctiva Concreta**: Cada advertencia incluye la prescripción técnica inmediata para resolver el defecto sin recurrir a conjeturas.
3. **Autonomía del Estudiante**: Facilita la autoevaluación local antes de la entrega final del trabajo práctico.
4. **Objetividad Docente**: Estandariza la corrección automática eliminando discrepancias subjetivas en la evaluación.

---

(manual-zhora-instalacion)=
## 2. Instalación y Diagnóstico del Entorno

````{important}
Asegurate de contar con el compilador GCC/Clang y las librerías del sistema instaladas antes de ejecutar `zhora`.
````

Para comprobar el estado de salud de tu entorno de trabajo y las dependencias auxiliares:

````{code-block} bash
# Comprobación de dependencias del sistema
zhora doctor
````

Si se detecta la falta de alguna utilidad (como `gdb`, `valgrind`, `clang-format` o `typst`), el comando indicará el paquete exacto a instalar según tu distribución GNU/Linux o entorno MSYS2.

---

(manual-zhora-comandos)=
## 3. Referencia Completa de Comandos CLI

A continuación se detallan los subcomandos principales disponibles en `zhora`:

| Sintaxis del Comando | Descripción y Efecto |
| :--- | :--- |
| `zhora audit include/ src/` | Audita todas las macros `#define` buscando vulnerabilidades de precedencia. |
| `zhora fix include/macros.h` | Agrega automáticamente paréntesis defensivos a los parámetros de macros. |
| `zhora to-inline include/macros.h` | Convierte macros complejas en funciones estáticas inline tipadas. |
| `zhora doctor` | Verifica analizadores de preprocesador C. |

````{tip}
Podés agregar el flag `--json` a la mayoría de los comandos para exportar resultados en formato estructurado o `--md` para generar reportes Markdown para el informe de entrega.
````

---

(manual-zhora-tutorial)=
## 4. Tutorial Paso a Paso con Ejemplos Reales

### Caso de Estudio

Considerá el siguiente fragmento de código representativo:

````{code-block} c
:linenos:
// Macro insegura: falta de paréntesis y doble evaluación de argumentos
#define CUADRADO_MAL(x) x * x
#define MAX_MAL(a, b) ((a) > (b) ? (a) : (b))

// Invocaciones problemáticas:
// CUADRADO_MAL(1 + 2) expande a: 1 + 2 * 1 + 2 = 5 (esperado: 9)
// MAX_MAL(i++, j) evalúa 'i++' dos veces si 'a > b'

// Macro segura auditada por Zhora:
#define CUADRADO_BIEN(x) ((x) * (x))
// O preferiblemente función inline:
static inline int cuadrado(int x) { return x * x; }
````

### Ejecución de la Herramienta

Ejecutá el análisis desde tu terminal:

````{code-block} bash
zhora audit include/ src/
````

### Salida Obtenida en Consola

````{code-block} text
⚠️ ZHORA PREPROCESSOR SECURITY REPORT:
┌─────────────────┬────────────────────────────────────────────────────────┐
│ Ubicación       │ Diagnóstico de Seguridad y Sugerencia                  │
├─────────────────┼────────────────────────────────────────────────────────┤
│ macros.h:2:9    │ Macro 'CUADRADO_MAL': Parámetro 'x' sin paréntesis.    │
│                 │ 'x * x' fallará ante expresiones compuestas (1 + 2).   │
│ macros.h:3:9    │ Macro 'MAX_MAL': Doble evaluación de 'a'. Riesgo grave │
│                 │ ante argumentos con efectos colaterales (i++).         │
└─────────────────┴────────────────────────────────────────────────────────┘
💡 Ejecutá 'zhora fix include/macros.h' para agregar paréntesis protectores.
````

````{note}
Prestá atención a la explicación pedagógica generada: la herramienta no solo señala la línea del problema, sino que explica la causa raíz y el impacto en memoria o arquitectura.
````

---

(manual-zhora-ejercicios)=
## 5. Ejercicios Prácticos y Desafíos

Practicá el uso avanzado de **`zhora`** resolviendo los siguientes ejercicios:

````{exercise} Desafío 1: Auditoría de Macros en Headers de Utilidad
Escanear `include/util.h` y encontrar macros propensas a errores de precedencia.

**Instrucción de ejecución:**
```bash
zhora audit include/util.h
```
````

````{solution} Desafío 1
```bash
zhora audit include/util.h
# Verificá que la operación concluya exitosamente con código de salida 0.
```
````

````{exercise} Desafío 2: Auto-Protección de Parámetros con Paréntesis
Corregir automáticamente `#define MULT(a, b) a * b` por `((a) * (b))`.

**Instrucción de ejecución:**
```bash
zhora fix include/util.h
```
````

````{solution} Desafío 2
```bash
zhora fix include/util.h
# Revisá el archivo generado o el informe en terminal para confirmar la resolución del problema.
```
````

````{exercise} Desafío 3: Migración de Macros a Funciones `inline`
Reemplazar macros con efectos colaterales por funciones `static inline` con chequeo de tipos.

**Instrucción de ejecución:**
```bash
zhora to-inline include/matematica.h
```
````

````{solution} Desafío 3
```bash
zhora to-inline include/matematica.h
# Comprobá que la salida confirme la ausencia de advertencias o errores pendientes.
```
````

---

(manual-zhora-makefile)=
## 6. Integración en el Flujo de Trabajo y Makefile

Para incorporar `zhora` de forma automática a tu flujo de desarrollo, agregá la siguiente regla en el `Makefile` de tu proyecto:

````{code-block} makefile
check-zhora:
	@echo "=== Ejecutando verificación con zhora ==="
	zhora check src/ include/

.PHONY: check-zhora
````

Ejecutá `make check-zhora` antes de cada commit para asegurar que tu código conserve el estado de aprobación.
