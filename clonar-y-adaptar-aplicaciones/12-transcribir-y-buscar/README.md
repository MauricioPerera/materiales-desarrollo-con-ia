# Transcribir una toma y buscar contexto

Este experimento procesa localmente un archivo de audio con [faster-whisper](https://github.com/SYSTRAN/faster-whisper), lee las marcas del [grabador experimental anterior](../10-marcas-instrucciones/) y genera un informe con texto y referencias aproximadas. No corta ni altera ninguna pista y no interpreta las instrucciones de edición.

## Preparación

Necesitas Python, FFmpeg disponible en el PATH y el paquete `faster-whisper`:

```sh
python -m pip install faster-whisper
```

El programa usa por defecto el modelo `small` en CPU. La primera vez puede descargar el modelo; consulta las instrucciones y requisitos de [faster-whisper](https://github.com/SYSTRAN/faster-whisper) y [FFmpeg](https://ffmpeg.org/download.html). El procesamiento del audio se hace en el equipo una vez disponibles el modelo y las dependencias. El ejemplo carga el audio decodificado en memoria y está pensado para tomas cortas. Usa una copia y conserva los originales.

## Uso

```sh
python transcribir_y_buscar.py audio.webm metadatos.json informe.json
```

Sin desplazamiento, el informe incluye la transcripción pero deja las marcas sin alinear. El grabador registra tiempo activo; la transcripción cuenta desde el inicio del archivo de audio. Tras **comprobar** su relación sobre la grabación, puedes indicarla en segundos:

```sh
python transcribir_y_buscar.py audio.webm metadatos.json informe.json --offset-audio 0.2
```

La convención es `tiempo de audio = tiempo activo + desplazamiento`. Un valor de cero no se debe suponer. El valor puede ser negativo; una referencia convertida fuera del audio queda pendiente. El desplazamiento constante no corrige posibles cambios de sincronía a lo largo de la toma. La salida no sobrescribe un archivo existente ni modifica las entradas.

El informe busca segmentos dentro de una ventana de cuatro segundos alrededor de cada marca cerrada o puntual; `--contexto` ajusta el margen. Las instrucciones incompletas y las referencias fuera del audio quedan pendientes. Lee [la guía de revisión](revision.md) antes de usar los resultados.

## Ejemplo comprobado

La carpeta [ejemplo](ejemplo/) contiene voz sintética de tres frases, metadatos generados para esa misma línea de tiempo y el informe obtenido en una ejecución local. Al haber construido el audio y las marcas juntos, para **ese ejemplo** se conoce el desplazamiento cero. Puedes generar tu propio informe con otro nombre:

```sh
python transcribir_y_buscar.py ejemplo/audio-sintetico.wav ejemplo/metadatos-sinteticos.json resultado.json --offset-audio 0
```

Este caso corto no demuestra precisión con otras voces, ruido ni pistas reales.

## Fuentes

- [faster-whisper: tiempos por palabra](https://github.com/SYSTRAN/faster-whisper#word-level-timestamps)
- [MediaRecorder: eventos y precisión temporal](https://developer.mozilla.org/en-US/docs/Web/API/MediaRecorder/dataavailable_event)
