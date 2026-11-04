# Unir cortes y acercamiento con dos relojes

Este ejemplo combina un acercamiento fijo y cortes elegidos manualmente sobre medios sintéticos prealineados. El plan expresa todas las decisiones sobre la grabación original. El informe muestra qué partes del acercamiento sobreviven y dónde aparecen en el video de salida.

## Probar

Descarga el repositorio completo y ten disponibles Python 3, FFmpeg y FFprobe. Desde esta carpeta ejecuta:

```sh
python ../19-zoom-en-pantalla/crear_pantalla_sintetica.py pantalla.mp4
python aplicar_cortes_zoom.py plan-ejemplo.json pantalla.mp4 ../13-corte-revisado/ejemplo/microfono.wav salida --camara ../13-corte-revisado/ejemplo/camara.mp4
```

Omite `--camara` y elige otra carpeta de salida para probar sin cámara. La carpeta de salida debe ser nueva y su carpeta padre debe existir. Si una codificación falla, puede quedar una carpeta parcial: revísala y usa un destino nuevo. Las entradas no se sustituyen y la imagen se vuelve a codificar.

## Interpretar el ejemplo

Conservamos `[0,60)` y `[120,340)`: se eliminan 60 fotogramas del original y la salida contiene 280. El acercamiento original `[90,180)` cruza el tramo eliminado. Su porción conservada es `[120,180)` y aparece en `[60,120)` de la salida. Los límites iniciales están incluidos y los finales excluidos. Un intervalo que atraviesa varios cortes puede producir varias partes, o desaparecer si no se conserva ninguna.

La herramienta aplica el acercamiento a la pantalla original, superpone la cámara opcional y después recorta imagen y voz con los mismos intervalos. El informe traduce las intersecciones para facilitar la revisión; no identifica el objetivo ni interpreta instrucciones habladas.

## Límites y revisión

Se esperan 340 fotogramas a 30 fps, inicio en cero y WAV PCM de 16 bits y 48 kHz con duración coincidente. Las tasas declaradas no prueban cadencia constante ni que dispositivos reales estén sincronizados. Revisa las uniones, la voz, la legibilidad y la relación entre pistas, también al final de la toma. No hay fundidos ni seguimiento del cursor; el acercamiento usa cambios bruscos. Este experimento aún no es una aplicación integrada.

Fuentes: documentación de FFmpeg sobre [trim](https://ffmpeg.org/ffmpeg-filters.html#trim), [atrim](https://ffmpeg.org/ffmpeg-filters.html#atrim), [concat](https://ffmpeg.org/ffmpeg-filters.html#concat), [crop](https://ffmpeg.org/ffmpeg-filters.html#crop) y [overlay](https://ffmpeg.org/ffmpeg-filters.html#overlay).
