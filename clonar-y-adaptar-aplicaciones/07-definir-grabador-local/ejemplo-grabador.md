# Ejemplo: grabador local para trabajar con agentes

Este ejemplo es una propuesta para explicar el proceso de definición. No demuestra que la aplicación ni las pruebas descritas ya existan.

## Necesidad y flujo actual

Una persona graba una demostración, da instrucciones habladas cuando comete un error y repite la frase corregida. Después trabaja con un agente para identificar los tramos y editar. Las pausas claras antes y después de las instrucciones son una práctica útil; su detección automática deberá comprobarse.

Queremos facilitar que el agente encuentre instrucciones y contexto sin perder los archivos originales. La grabación y el procesamiento inicial se plantean para un entorno local.

## Comparar y adaptar

| Necesidad | Referencia o práctica | Decisión propuesta |
|---|---|---|
| Grabar una demostración | Captura de pantalla y cámara de Loom | Dos modos: pantalla sin cámara y pantalla con cámara. |
| Cambiar la cámara después | Composición de video | Guardar pantalla y cámara por separado y comprobar su sincronización. |
| Indicar qué corregir | Instrucciones habladas en el flujo actual | Conservar audio y transcripción temporal; el agente propone cortes y señala dudas. |
| Señalar una región | Anotaciones de Loom para agentes | Explorar marcas con tiempo y región en una capa independiente. |
| Entregar contexto | Archivos locales y herramientas del agente | Explorar un manifiesto y una interfaz local; no exigir un servidor MCP propio. |
| Compartir por enlace | Servicio alojado | Fuera del primer recorrido local; puede evaluarse después. |

La documentación de Loom describe sus funcionalidades; la tabla no afirma que hayamos probado Loom ni que el proyecto replique su implementación.

## Escenario y resultado esperado

La persona elige pantalla y cámara opcional, graba una frase incorrecta, hace una pausa, indica qué quitar, hace otra pausa y repite la frase correcta. Se conservan las pistas originales. El agente prepara un plan de corte y, una vez resuelta cualquier ambigüedad, genera un video que conserva la frase correcta. Cuando se elimina un tramo completo, pantalla, cámara y audio deben permanecer sincronizados.

## Preguntas y experimentos pendientes

| Pregunta | Experimento propuesto | Evidencia esperada |
|---|---|---|
| ¿Funcionan los dos modos en la plataforma elegida? | Grabar y abrir localmente un ejemplo de cada modo. | Archivos reproducibles y registro de permisos y formatos. |
| ¿Se sincronizan las pistas después de una pausa? | Grabar una señal común al inicio, después de una pausa y cerca del final. | Comparar pantalla, cámara y voz durante la reproducción. |
| ¿Se identifica la instrucción de corte? | Transcribir una toma con un error, pausas e instrucción explícita. | Plan de cortes y revisión visual y auditiva de la exportación. |
| ¿Puede localizarse una marca? | Guardar tiempo y región de una anotación y consultar esos datos. | La marca coincide con el momento y la zona esperados. |
| ¿Qué URL y clics pueden capturarse? | Ensayar cada posibilidad en el entorno elegido. | Registro de capacidades, límites y permisos observados. |

Todas las pruebas de la tabla están pendientes. Si una falla, se revisa el alcance y se registra la decisión.
