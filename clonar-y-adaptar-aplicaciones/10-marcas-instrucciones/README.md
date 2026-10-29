# Marcas e instrucciones para revisar una grabación

Este experimento permite guardar las pistas de una toma y registrar marcas puntuales o intervalos de instrucciones. Las marcas ayudan a encontrar contexto; no interpretan la voz ni ejecutan cortes.

## Probar el ejemplo

1. En `ejemplo`, ejecuta `python -m http.server 8789 --bind 127.0.0.1` y abre `http://localhost:8789` en un navegador compatible.
2. Elige una pantalla o ventana de prueba sin información privada y activa cámara o micrófono si los necesitas.
3. Mientras grabas, pulsa **Marcar punto** para señalar un instante. Para una instrucción hablada, pulsa **Iniciar instrucción**, habla y pulsa **Cerrar instrucción**.
4. Detén y descarga las pistas y los metadatos. Compara las marcas con el audio y la imagen antes de proponer cambios. Si detienes con una instrucción abierta, se registra como incompleta.

Las marcas se calculan con el reloj activo de la aplicación, que excluye las pausas. Son referencias aproximadas y no garantizan el mismo fotograma o instante en cada pista. Los archivos se preparan en el navegador y solo se guardan cuando los descargas.

La instrucción hablada permanece en la pista de micrófono. Esta versión no tiene audio exclusivo para instrucciones, transcripción, identificación automática de errores ni edición por agentes. El comportamiento con hardware real y tomas largas requiere pruebas en tu entorno.

## Repetir la prueba sintética

La prueba usa pantalla, cámara y audio generados; no solicita acceso a dispositivos reales. Necesita Python y Playwright: instala con `python -m pip install playwright` y `python -m playwright install chromium`. Desde `ejemplo`, ejecuta `python test_marcas.py`.

El script verifica puntos, intervalos, el tiempo activo durante una pausa, un intervalo incompleto, cancelación y descarga de pistas simuladas. Esto no demuestra comprensión de instrucciones ni edición automática.

Completa la [plantilla de propuesta](plantilla-propuesta.md), consulta el [ejemplo](ejemplo-propuesta.md) y revisa las [fuentes](fuentes.md).
