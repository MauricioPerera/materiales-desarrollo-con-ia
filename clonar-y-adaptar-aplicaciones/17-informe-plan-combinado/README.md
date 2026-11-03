# Del informe a un plan combinado revisado

Este experimento conecta un informe existente con decisiones explícitas y el [plan de cortes y silencios](../16-cortes-y-silencios/). Trabaja con archivos sintéticos preparados para compartir un reloj. No graba, no transcribe ni interpreta instrucciones: el informe se obtiene antes y las decisiones se escriben manualmente.

## Preparar el borrador

Descarga el repositorio completo para conservar las dependencias. Necesitas Python, FFmpeg y FFprobe. Desde esta carpeta:

```sh
python flujo_integrado.py preparar ../12-transcribir-y-buscar/ejemplo/informe-sintetico.json ../13-corte-revisado/ejemplo/pantalla.mp4 ../13-corte-revisado/ejemplo/microfono.wav borrador.json --camara ../13-corte-revisado/ejemplo/camara.mp4
```

El borrador debe tener nombre nuevo. Contiene las referencias, las huellas de las fuentes, una decisión pendiente por referencia y un plan vacío. Las declaraciones de revisión y alineación empiezan en `false`.

## Revisar y aplicar

Revisa cada referencia y la toma completa. Registra una resolución `incluida_en_plan` o `sin_cambio` y un motivo no vacío para cada referencia. Una marca incompleta o ambigua requiere atención: si no sabes resolverla, mantenla pendiente. Define los intervalos de `conservar` y `silenciar` en el reloj original, con final exclusivo. Solo tras revisar la toma y comprobar la alineación declara ambas condiciones en el borrador.

El plan del ejemplo sintético utiliza `fps: 30`, `duracion_fotogramas: 340`, `conservar: [[0,12],[90,340]]` y `silenciar: [[115,225]]`. Son límites de este ejemplo, no una regla para otras tomas. Consulta el [ejemplo de decisiones simuladas](ejemplo-decisiones.md). Para probar específicamente el rechazo de una referencia pendiente, usa una copia del borrador sintético con el plan válido, las declaraciones y las demás decisiones completadas, pero deja una resolución en `pendiente`: el comando debe rechazarla sin crear la salida. Las declaraciones de esa prueba son simuladas; no las extrapoles a una toma real.

```sh
python flujo_integrado.py aplicar borrador.json ../12-transcribir-y-buscar/ejemplo/informe-sintetico.json ../13-corte-revisado/ejemplo/pantalla.mp4 ../13-corte-revisado/ejemplo/microfono.wav salida --camara ../13-corte-revisado/ejemplo/camara.mp4
```

Para probar sin cámara, omite `--camara` en ambos comandos y prepara otro borrador. La carpeta de salida debe ser nueva. Si falla la codificación puede quedar una salida parcial; revísala y usa un destino nuevo al repetir. El plan revisado acompaña a las pistas editadas. Las herramientas del ejemplo exigen video declarado a 30 fps, WAV PCM de 16 bits a 48 kHz y duraciones coincidentes; consulta sus restricciones antes de usarlas.

## Qué comprueba y qué no

Se comparan huellas y referencias antes de aplicar el plan y se exigen decisiones, motivos y declaraciones completas. Se rechazan intervalos inválidos y salidas existentes. La huella no demuestra que el informe pertenezca a las pistas, que estén sincronizadas ni que alguien haya escuchado. Las decisiones declaradas no prueban por sí mismas que el plan las implemente; las fuentes podrían cambiar entre la comprobación y el uso. Las tasas declaradas no prueban cadencia constante ni ausencia de deriva. El silencio no aplica fundidos y solo afecta al micrófono.

Las pruebas del episodio usan decisiones simuladas y entradas sintéticas. Reproduce y revisa juntas las salidas antes de usarlas; conserva los originales. La captura real, la interfaz de revisión y la integración en el grabador siguen pendientes.

## Fuentes

- [Python: huellas SHA-256](https://docs.python.org/3/library/hashlib.html)
- [faster-whisper: tiempos por palabra](https://github.com/SYSTRAN/faster-whisper#word-level-timestamps)
- [FFmpeg: filtros de recorte y concatenación](https://ffmpeg.org/ffmpeg-filters.html#concat)
