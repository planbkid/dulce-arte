# 🤖 Registro de uso de Inteligencia Artificial

**Proyecto:** Dulce Arte — Sistema de Trazabilidad y Pedidos (EVA 3 Backend)
**Alumno:** Cristóbal Barriga · Grupo 3
**Herramienta:** Claude (Anthropic) vía Claude Code

> Este archivo documenta las consultas realizadas a la IA como apoyo al desarrollo,
> según lo solicitado en el enunciado. El diseño final, la comprensión del código y
> la defensa son responsabilidad del estudiante.

---

## Prompt 1 — Entender el enunciado
**Consulta:** "Proyecto 3 EVA3 de backend, no sé qué tengo que hacer, te adjunto los
archivos para que me digas en forma de receta cómo tengo que hacerlo."
**Apoyo recibido:** Análisis del enunciado (docx), identificación de que me corresponde el
Proyecto 3 "Dulce Arte" (Grupo 3) y explicación de los 5 criterios de la rúbrica.

## Prompt 2 — Receta completa
**Consulta:** "Dame la receta completa para hacer todo lo que me piden."
**Apoyo recibido:** Guía paso a paso (fases 0 a 6) con comandos y código: estructura de apps,
modelos, Django Admin, lógica de negocio, frontend y despliegue en AWS.

## Prompt 3 — Generación del proyecto
**Consulta:** "Necesito que hagas todo tú y me lo pases, y lo despliego en AWS ya listo."
**Apoyo recibido:** Generación del proyecto Django/DRF completo:
- Modelos `Insumo`, `Producto`, `ProductoInsumo` (BOM), `Pedido`, `DetallePedido`, `Despacho`.
- Lógica de **descuento automático de inventario** según la Lista de Materiales al pasar un
  pedido a "En Preparación" (con validación de stock y transacción atómica).
- Django Admin personalizado (list_display, filtros, búsqueda, inlines).
- Endpoint DRF `mover_estado` para el tablero Kanban asíncrono.
- Templates responsivos y confirmación de despacho con firma digital.
- Comando `seed_demo` con datos de ejemplo y scripts/guía de despliegue en AWS EC2.

**Qué revisé / adapté yo:**
- *(Completa aquí lo que ajustaste: precios, insumos reales, textos, estilos, etc.)*

---

### Nota de honestidad académica
El código fue generado con apoyo de IA (permitido por el enunciado) y posteriormente
**revisado y comprendido** por el estudiante para la defensa individual.
