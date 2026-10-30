# De marcas y transcripción a una propuesta

Estos materiales ayudan a revisar una grabación con una instrucción hablada. El ejemplo usa datos ficticios y muestra cómo localizar contexto; no edita medios ni decide qué debe eliminarse.

1. Consulta [la plantilla de revisión](plantilla-propuesta.md) para registrar lo que se conservará, la operación sugerida y las dudas.
2. Ejecuta `python localizar_contexto.py ejemplo.json` para agrupar segmentos de transcripción cercanos a las marcas de ejemplo. Necesitas Python 3. No se instala ni ejecuta un transcriptor con este ejemplo.
3. Compara el informe con [la revisión comentada](ejemplo-revision.md). Los tiempos son ilustrativos y comparten un reloj únicamente en este ejemplo.

Para una toma real, comprueba el desplazamiento de cada pista y escucha el audio original. El tiempo activo de los metadatos de la aplicación no garantiza coincidencia exacta con los tiempos de los archivos. Una marca incompleta no debe interpretarse como una orden de corte. Conserva los originales.

## Fuentes

- [faster-whisper: transcripción y tiempos por palabra](https://github.com/SYSTRAN/faster-whisper#word-level-timestamps)
- [FFmpeg: detección de silencio](https://ffmpeg.org/ffmpeg-filters.html#silencedetect)
- [MediaRecorder](https://developer.mozilla.org/en-US/docs/Web/API/MediaRecorder)
