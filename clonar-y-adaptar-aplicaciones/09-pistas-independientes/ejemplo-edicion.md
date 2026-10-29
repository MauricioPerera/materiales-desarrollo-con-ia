# Ejemplo de composición

Con FFmpeg instalado y las tres pistas WebM en el directorio actual, este ejemplo coloca la cámara en la esquina inferior derecha. Usa una copia: conserva los originales.

```sh
ffmpeg -i pantalla.webm -i camara.webm -i microfono.webm -filter_complex "[1:v]scale=320:-2[cam];[0:v][cam]overlay=main_w-overlay_w-20:main_h-overlay_h-20:shortest=1[v]" -map "[v]" -map 2:a -c:v libx264 -pix_fmt yuv420p -c:a aac -shortest resultado.mp4
```

Para colocarla arriba a la izquierda, sustituye la posición de `overlay` por `20:20`. Para ocultarla, compón solo pantalla y audio. Este ejemplo no corrige desplazamientos: compara primero las señales y ajusta la alineación si es necesario. Los nombres y códecs reales pueden cambiar según el navegador; adapta las entradas y medidas a tus archivos.
