# Probar un grabador local

Este ejemplo parte de la definición del grabador inspirado en Loom y explora una pregunta concreta: ¿podemos capturar una pantalla y descargar un video, con cámara y micrófono opcionales?

El prototipo compone las imágenes de pantalla y cámara en un único video. Todavía no guarda pistas independientes ni incluye edición por agentes o marcas. Es un experimento para aprender y ajustar la definición, no una aplicación terminada.

## Cómo probarlo

1. Abre una terminal en la carpeta `ejemplo` y ejecuta `python -m http.server 8787 --bind 127.0.0.1`.
2. Abre `http://localhost:8787` en un navegador compatible con captura de pantalla y grabación de medios.
3. Decide si usar cámara y micrófono; inicia la grabación y elige qué compartir en el selector del navegador.
4. Detén la toma, descárgala y revisa el archivo. Consulta la [lista de comprobación](lista-comprobacion.md).

La captura y los permisos dependen del navegador, el sistema y los dispositivos. Usa una ventana o pantalla de prueba sin información privada y comprueba qué seleccionaste antes de grabar. El archivo se prepara en el navegador y se descarga cuando lo solicitas; el servidor de ejemplo entrega los archivos de la aplicación.

## Qué evidencia tenemos

La ejecución automatizada utilizó una pantalla y una cámara sintéticas y un tono de audio. Se verificó el archivo descargado, así como pausa, cancelación y algunos errores simulados. Esto no valida los permisos del sistema ni una cámara o micrófono físicos. Esos casos deben probarse en el equipo de cada persona. El formato disponible depende del navegador.

Consulta las [fuentes](fuentes.md) y la [definición del experimento](ejemplo/SPEC.md).
