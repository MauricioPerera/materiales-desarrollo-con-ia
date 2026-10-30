# Aplicar un corte revisado a pistas alineadas

Este experimento aplica un plan **escrito previamente** a pistas sintéticas con una línea de tiempo común. Genera archivos nuevos para pantalla, voz y, opcionalmente, cámara. No interpreta la transcripción ni decide dónde cortar.

## Requisitos y ejemplo

Necesitas Python y FFmpeg con `ffmpeg` y `ffprobe` disponibles en el PATH. Desde esta carpeta:

```sh
python aplicar_plan.py plan-ejemplo.json ejemplo/pantalla.mp4 ejemplo/microfono.wav salida-ejemplo --camara ejemplo/camara.mp4
```

Para probar sin cámara, usa otro nombre de salida y omite `--camara`:

```sh
python aplicar_plan.py plan-ejemplo.json ejemplo/pantalla.mp4 ejemplo/microfono.wav salida-sin-camara
```

La carpeta de salida debe ser nueva. El programa no sobrescribe entradas ni una salida existente. Si ocurre un error durante la codificación, puede quedar una carpeta parcial; revísala antes de volver a ejecutar con otro nombre.

## Qué significa el plan

Los intervalos son pares de fotogramas `[inicio, fin)` que se **conservan**. El final es exclusivo. En el ejemplo original hay 340 fotogramas a 30 fps; se conservan `[0,12)` y `[255,340)`, es decir, 97 fotogramas. El audio utiliza 48.000 muestras por segundo y se recorta con los mismos límites. Las tres entradas fueron generadas para compartir un origen temporal.

El programa comprueba frecuencia, duración y algunos datos del archivo, pero **eso no demuestra que las pistas reales estén sincronizadas ni detecta deriva**. Tampoco identifica automáticamente errores o instrucciones. El corte completo elimina tiempo de todas las pistas; silenciar solo el micrófono sería una operación diferente y no está implementada aquí.

Antes de aplicar un plan a una toma real, revisa el contenido y la sincronía de sus pistas y conserva los originales. Este ejemplo solo acepta sus condiciones concretas: video de 30 fps constantes, audio a 48 kHz y duraciones iguales a las del plan. Revisa la unión en imagen y sonido: las métricas y las pruebas sintéticas no sustituyen esa revisión.

## Evidencia y límites

En las pruebas con los medios sintéticos incluidos se comprobaron los dos modos, la duración de las salidas, la preservación de los originales y muestras de fotogramas y audio en los intervalos conservados. También se rechazaron planes vacíos, invertidos, solapados o fuera de rango. No se ha demostrado compatibilidad general con grabaciones reales ni sincronía en tomas largas.

## Fuentes

- [FFmpeg: recortar audio](https://ffmpeg.org/ffmpeg-filters.html#atrim)
- [FFmpeg: concatenar segmentos](https://ffmpeg.org/ffmpeg-filters.html#concat)
- [FFmpeg: recortar video](https://ffmpeg.org/ffmpeg-filters.html#trim)
