# Ejemplo conceptual: una copia que conserva el contenido

## Necesidad y alcance

Una persona necesita preparar una copia local de un documento conocido y volver a abrirla con el contenido acordado. Imprimir y colaborar en línea quedan fuera de este encargo. El formato, los datos y el entorno de comprobación deben identificarse.

## Criterios y escenarios propuestos

| ID | Estado inicial y acción | Resultado esperado | Comprobación propuesta | Estado |
|---|---|---|---|---|
| AC-1 | Documento conocido y destino disponible; crear la copia y volver a abrirla | Se conserva el contenido relevante acordado | Comparar el contenido al reabrir, bajo las condiciones identificadas | Pendiente de ejecución |
| AC-2 | Documento con edición pendiente y destino sin permiso de escritura; intentar crear la copia | Se informa del problema y se conserva la edición | Observar el mensaje y comprobar el contenido y el estado del documento | Pendiente de ejecución |

Son decisiones de este ejemplo. En otro producto hay que acordar el comportamiento correspondiente.

## Trabajo y decisiones

- Confirmar los datos de prueba y qué contenido debe conservarse.
- Resolver el mecanismo de escritura y apertura dentro del alcance acordado.
- Preparar comprobaciones que correspondan a AC-1 y AC-2.
- Revisar el resultado de cada ejecución y conservar su evidencia y condiciones.

Una decisión técnica explica cómo intentaremos satisfacer el criterio. Terminar una tarea no acredita por sí solo que ese criterio se haya cumplido.

## Una prueba intacta pero limitada

Una comprobación que solo pregunta si existe un archivo podría aceptar una copia vacía. Proteger esa comprobación frente a modificaciones conserva su identidad; no hace que compare contenido.

Para estudiar su fuerza, se puede proponer una pérdida deliberada de contenido en una copia aislada y comprobar si la prueba pertinente la rechaza. Si no se ha ejecutado ese experimento, sigue siendo una propuesta. Un fallo de conexión o entorno no acredita la detección de ese defecto.

## Referencia y revisión

Si el proceso del proyecto usa referencias aprobadas, registrar qué versión de criterios y pruebas se revisó, quién confirma la intención y qué perímetro se autorizó. Un cambio posterior de criterio o prueba requiere la revisión correspondiente y un motivo visible.

Los mecanismos documentados por KDD dependen de su configuración, los controles ejecutados y la confianza en el ejecutor. Este ejemplo no acredita una ejecución de KDD ni garantiza ausencia de defectos.
