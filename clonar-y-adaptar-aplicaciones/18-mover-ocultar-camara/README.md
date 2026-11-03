# Mover u ocultar la cámara al componer una grabación

Este ejemplo genera una composición nueva a partir de pantalla, micrófono y una cámara opcional. Las pistas sintéticas se prepararon para compartir un origen temporal. El programa aplica posiciones y tramos escritos de antemano: no interpreta instrucciones ni se integra todavía en el grabador.

## Probarlo

Descarga el repositorio completo para disponer de los medios de ejemplo. Necesitas Python, FFmpeg y FFprobe en el PATH. Desde esta carpeta:

```sh
python componer_camara.py plan-ejemplo.json ../13-corte-revisado/ejemplo/pantalla.mp4 ../13-corte-revisado/ejemplo/microfono.wav salida-con-camara.mkv --camara ../13-corte-revisado/ejemplo/camara.mp4
```

Para probar sin cámara, omite `--camara` y usa un destino nuevo:

```sh
python componer_camara.py plan-ejemplo.json ../13-corte-revisado/ejemplo/pantalla.mp4 ../13-corte-revisado/ejemplo/microfono.wav salida-sin-camara.mkv
```

El destino debe ser un archivo MKV nuevo. La salida combina el video con audio PCM; la pantalla se vuelve a codificar. Los originales permanecen separados. Un fallo de codificación puede dejar un archivo parcial: revísalo y usa otro nombre para repetir.

## Leer el plan

Los intervalos `[inicio, fin)` usan fotogramas de la toma original; el final es exclusivo. El ejemplo tiene 340 fotogramas a 30 por segundo. La cámara aparece en `[0,100)` en la esquina superior izquierda, queda oculta en `[100,200)` y aparece en `[200,340)` en la esquina inferior derecha. Cambia de posición por corte; no hay movimiento suave ni cambios de tamaño durante el tramo.

La pantalla sintética mide 640 × 360 píxeles. La cámara se escala a 160 × 90; sus coordenadas `x` e `y` señalan la esquina superior izquierda. El tamaño y las posiciones deben ser enteros pares y la cámara debe caber dentro de la pantalla. La escala fija puede deformar una cámara con otra proporción. Los tramos deben estar ordenados y no solaparse; una lista vacía oculta toda la cámara. Sin `--camara`, se compone solo pantalla y voz aunque el plan contenga tramos.

El ejemplo requiere video con 340 fotogramas, inicio en cero y tasas declaradas de 30 fps, además de un WAV PCM de 16 bits, 48 kHz y uno o dos canales con duración equivalente. Las tasas declaradas no prueban cadencia constante, sincronía ni ausencia de deriva. Comprueba las condiciones de cada toma real y conserva sus originales.

## Revisar el resultado

Reproduce la composición y verifica que la cámara no tape información útil. Escucha la voz y revisa la sincronía en el inicio, las pausas y cerca del final. La comparación automática del ejemplo revisa fotogramas concretos, el audio y la conservación de entradas; no demuestra que todos los dispositivos ni grabaciones largas funcionen.

La cámara solo puede recolocarse independientemente cuando se dispone de su pista separada. Este experimento no recupera una cámara ya mezclada en la pantalla, no aplica acercamientos y no decide dónde colocarla por sí solo.

## Fuentes

- [FFmpeg: filtro overlay](https://ffmpeg.org/ffmpeg-filters.html#overlay)
- [FFmpeg: activación temporal de filtros](https://ffmpeg.org/ffmpeg-filters.html#Timeline-editing)
- [FFmpeg: escala de video](https://ffmpeg.org/ffmpeg-filters.html#scale)
