# ZHORA — Linter y Auditor de Seguridad en Macros C (#define)

**ZHORA** audita macros del preprocesador C para detectar efectos de lado en evaluación múltiple de parámetros, falta de paréntesis defensivos en argumentos y cuerpos, y puntos y coma espurios.

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
