# Ejemplo de decisiones para los medios sintéticos

El informe incluido tiene una marca cerrada y otra incompleta. En la prueba automatizada las dos resoluciones siguientes son **simuladas**: sirven para ejercitar el recorrido y no certifican que una persona haya revisado el audio ni que una marca incompleta pueda ignorarse en una grabación real.

| Referencia | Resolución de prueba | Motivo de prueba |
|---|---|---|
| Marca cerrada | `incluida_en_plan` | Se propone retirar la frase anterior y silenciar la instrucción, conservando la imagen durante ella. |
| Marca incompleta | `sin_cambio` | Se simula que no requiere una operación adicional. En una toma real hay que examinarla antes de decidir. |

El plan de ejemplo conserva `[0,12)` y `[90,340)` y silencia `[115,225)` del micrófono original. La prueba solo declara la alineación porque las pistas fueron creadas para compartir un origen; esa declaración no prueba por sí misma la sincronía. Registra tus propias decisiones tras revisar tus propios medios, sin sustituir las referencias o huellas generadas por el borrador.
