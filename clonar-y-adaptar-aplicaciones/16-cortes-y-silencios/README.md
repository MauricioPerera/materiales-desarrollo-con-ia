# Un plan para cortes y silencios

Este experimento combina dos operaciones sobre pistas sintéticas prealineadas: silencia intervalos del micrófono en el **reloj original** y después aplica los mismos cortes a pantalla, voz y, opcionalmente, cámara. El plan se escribe y revisa antes de ejecutarlo; el programa no interpreta instrucciones ni demuestra que las pistas reales estén sincronizadas.

## Probar el ejemplo

Descarga el repositorio completo para conservar las dependencias y los medios sintéticos. Necesitas Python, FFmpeg y FFprobe. Desde esta carpeta ejecuta:

```sh
python aplicar_plan_combinado.py plan-ejemplo.json ../13-corte-revisado/ejemplo/pantalla.mp4 ../13-corte-revisado/ejemplo/microfono.wav salida --camara ../13-corte-revisado/ejemplo/camara.mp4
```

Para repetir sin cámara, omite `--camara` y usa otro nombre de salida. La carpeta de salida debe ser nueva y su carpeta padre debe existir. Si falla la codificación puede quedar una carpeta parcial; revísala y usa un destino nuevo. Se crea un audio intermedio temporal. La salida contiene las pistas editadas y un informe con los intervalos trasladados al reloj de salida.

## Qué representa el plan

Los intervalos se expresan en fotogramas originales `[inicio, fin)`, con final exclusivo. La toma tiene 340 fotogramas a 30 por segundo. Conserva `[0,12)` y `[90,340)`: elimina 78 fotogramas y deja 262. Silencia el micrófono en `[115,225)` del original; tras el corte, esa zona aparece en `[37,147)` de la salida. Si un silencio se cruza con un corte, solo sobrevive su intersección con el material conservado; puede quedar dividido en varios tramos o desaparecer.

El experimento requiere video con tasas declaradas de 30 fps, 340 fotogramas, inicio en cero y WAV PCM de 16 bits, 48 kHz y uno o dos canales, con duración coincidente. Las tasas declaradas no prueban que cada fotograma tenga cadencia constante; tampoco garantizan alineación ni ausencia de deriva. El WAV de salida puede perder metadatos auxiliares. Los silencios no incluyen fundidos ni conservan ambiente. El audio de otras pistas requiere decisiones separadas.

## Revisar juntas las pistas

Coloca las salidas en un editor desde el mismo origen temporal y reproduce la toma. Comprueba el contenido de cada unión, escucha antes y después del silencio y revisa que la acción de pantalla siga siendo comprensible. Si hay cámara, comprueba su relación con la pantalla y la voz, también cerca del final. Conserva los originales y revisa los límites con la toma real antes de aplicar cualquier plan.

Las comprobaciones del ejemplo no sustituyen la escucha, no identifican intención y no garantizan compatibilidad con dispositivos reales. Este experimento combina dos herramientas educativas; todavía no integra el grabador ni el flujo de revisión previo.

## Fuentes

- [FFmpeg: trim](https://ffmpeg.org/ffmpeg-filters.html#trim), [atrim](https://ffmpeg.org/ffmpeg-filters.html#atrim) y [concat](https://ffmpeg.org/ffmpeg-filters.html#concat).
- [Python: formato WAV](https://docs.python.org/3/library/wave.html).
- [Audacity: fundidos y transiciones](https://manual.audacityteam.org/man/fade_and_crossfade.html).
