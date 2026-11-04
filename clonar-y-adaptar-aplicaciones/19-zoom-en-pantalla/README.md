# Acercar una región de la pantalla

Este ejemplo educativo aplica un acercamiento fijo a una pantalla sintética durante un intervalo elegido a mano. Una cámara opcional se superpone después, por lo que mantiene su tamaño y posición durante el acercamiento. El audio se conserva como PCM en la salida MKV. Las entradas permanecen intactas y el video de salida se vuelve a codificar.

## Requisitos y uso

Necesitas Python 3, FFmpeg y FFprobe disponibles en la línea de comandos. Desde esta carpeta, crea una pantalla de prueba y usa la cámara y el micrófono sintéticos del ejemplo anterior:

```sh
python crear_pantalla_sintetica.py pantalla-sintetica.mp4
python acercar_pantalla.py plan-ejemplo.json pantalla-sintetica.mp4 ../13-corte-revisado/ejemplo/microfono.wav resultado.mkv --camara ../13-corte-revisado/ejemplo/camara.mp4
```

Para probar el modo sin cámara, omite `--camara` y utiliza otro nombre de salida. Cada salida debe ser nueva. Si falla una codificación, comprueba si quedó un archivo parcial antes de volver a intentarlo.

El plan describe el rectángulo como `[x, y, ancho, alto]` en la pantalla original. Sus dimensiones deben tener la misma proporción que la pantalla y sus valores deben ser pares. Los intervalos usan fotogramas del original: incluyen el inicio y excluyen el final. Esta muestra espera 340 fotogramas a 30 fps y audio PCM de 48 kHz con duración coincidente.

## Límites

El cambio es brusco; no hay transición animada ni seguimiento del cursor. El programa no interpreta instrucciones ni selecciona regiones por sí mismo. Los tiempos se refieren al original sin cortes; para usar un video recortado hay que traducir el plan al nuevo reloj. Igual duración y frecuencia declarada no prueban sincronía real ni ausencia de deriva. Ampliar no recupera detalle perdido; revisa imagen, voz y sincronía en cada grabación.

Fuentes: [filtros de FFmpeg](https://ffmpeg.org/ffmpeg-filters.html), en particular crop, scale, overlay y edición temporal.
