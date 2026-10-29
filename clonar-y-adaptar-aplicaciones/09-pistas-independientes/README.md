# Pantalla, cámara y voz en pistas independientes

Este experimento guarda por separado los medios de una toma para poder editar la cámara sin modificar el archivo de pantalla. Los metadatos identifican archivos y eventos registrados por la aplicación; no garantizan que el contenido esté sincronizado.

## Probar el ejemplo

1. En la carpeta `ejemplo`, ejecuta `python -m http.server 8788 --bind 127.0.0.1`.
2. Abre `http://localhost:8788` con un navegador compatible. Decide si activar cámara y micrófono.
3. Inicia, elige una ventana o pantalla de prueba sin información privada, pausa, reanuda y detén.
4. Descarga cada pista y los metadatos. Examina los archivos en tu editor y compara señales visibles y audibles. Consulta el [ejemplo de composición](ejemplo-edicion.md).

La captura y los formatos dependen del navegador, el sistema y los permisos. La aplicación prepara los archivos en el navegador y no los sube a ningún servicio. Esta versión es experimental; no incorpora edición por agentes ni sincronización automática.

## Repetir la prueba sintética

El script crea una pantalla, una cámara y un tono sintéticos: no solicita pantalla ni dispositivos reales. Necesita Python, Playwright, NumPy, FFmpeg y ffprobe. Instala las librerías con `python -m pip install playwright numpy` y el navegador con `python -m playwright install chromium`. Desde `ejemplo`, ejecuta `python test_sintetico.py`.

La prueba descarga tres pistas, mide dos señales antes y después de una pausa y ensaya el modo sin cámara y la cancelación. El resultado solo describe esa ejecución corta. Usa la [plantilla de medición](plantilla-medicion.md) y las [fuentes](fuentes.md) para repetir el experimento en tu entorno.
