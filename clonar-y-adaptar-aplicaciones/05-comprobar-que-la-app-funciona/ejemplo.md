# Ejemplo conceptual: recuperar una corrección

Este documento propone comprobaciones para un editor hipotético. **No se ejecutaron**: no se ha construido ni elegido la aplicación del caso práctico. Los resultados permanecen pendientes y el formato concreto se decidiría al implementar el alcance.

## Trabajo elegido y compromisos

Una persona corrige una frase, guarda una copia local y necesita continuar después. En este ejemplo se acuerda que la copia conserva el contenido corregido y que el original no se modifica. Si no puede guardarse, el editor informa y mantiene la edición pendiente para reintentar.

El documento conocido tiene el título **Revisión** y dos párrafos, en este orden:

1. «Entrega mañana».
2. «Cerrar el pedido».

La persona cambia el primer párrafo por **«Entrega el viernes»**. Ese es el texto esperado de la copia; el segundo párrafo y el título conservan su contenido y orden. Comparar con el original sin tener en cuenta la edición esperada daría un criterio equivocado.

## Casos propuestos

| Caso | Condición y acciones | Resultado esperado | Evidencia propuesta | Estado |
|---|---|---|---|---|
| C1 · Recuperar la copia | Abrir el documento conocido, corregir, guardar copia, cerrar y reabrirla | Título con tilde, primer párrafo corregido y segundo párrafo en su orden | Comparación del contenido recuperado y registro del recorrido | Pendiente |
| C2 · Preservar el original | Ejecutar C1 y volver a abrir el original | Primer párrafo «Entrega mañana» y resto del original sin cambios | Comparación de las propiedades originales comprometidas | Pendiente |
| C3 · Deshacer y rehacer | Corregir el primer párrafo; deshacer; rehacer si se incluye en el alcance | Estados acordados de texto e indicador de edición pendiente | Observación del documento y del estado de edición después de cada acción | Pendiente |
| C4 · Guardado fallido y reintento | Usar un destino sin escritura; corregir la causa y reintentar | Mensaje comprensible, edición recuperable y copia posterior con el resultado esperado | Registro del error, estado conservado y comparación de la copia | Pendiente |
| C5 · Otros contenidos | Repetir el recorrido con vacío, texto largo y caracteres pertinentes | Propiedades definidas para cada entrada | Documento de entrada, resultado esperado y comparación obtenida | Pendiente |
| C6 · Recorrido con teclado | Completar la tarea sin ratón y observar foco y etiquetas | Pasos alcanzables y foco reconocible según el acuerdo | Registro de acciones y barreras observadas | Pendiente |

Las condiciones de aplicación, sistema y equipo todavía no están definidas. Antes de ejecutar habría que registrar versiones y preparar los archivos concretos. Los nombres C1…C6 identifican propuestas; no indican casos que hayan pasado.

## Intercambio con otras aplicaciones

Este ejemplo básico promete recuperar la copia en el editor hipotético. Si se añade intercambio, se especificarán **formato, otra aplicación y versión, propiedades conservadas y direcciones**. Abrir el resultado allí y devolverlo son comprobaciones distintas. No deducimos compatibilidad con otro programa a partir de C1.

Una imagen aplanada puede conservar el aspecto y perder la posibilidad de editar texto. La aceptación depende de lo que necesite el trabajo, no de exigir siempre los mismos bytes o todos los comportamientos de la referencia.

## Rendimiento y decisión

No se ha definido un presupuesto de apertura ni se han medido tiempos. Si ese riesgo importa, se acordará antes un límite con unidad y se registrarán tamaño del documento, equipo, versión, preparación y repeticiones.

**Decisión actual: pendiente.** No hay evidencia de ejecución que permita aceptar una implementación. Después se revisarán los fallos que impidan recuperar la corrección, conservar el original o utilizar la copia. Una revisión inicial con teclado no demuestra accesibilidad completa; los documentos conocidos tampoco demuestran compatibilidad universal.
