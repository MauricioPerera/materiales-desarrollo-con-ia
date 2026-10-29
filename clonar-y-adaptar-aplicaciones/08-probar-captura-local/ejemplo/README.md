# Grabador local: primera prueba

Prototipo educativo para grabar una pantalla o ventana con cámara y micrófono opcionales. La grabación se prepara en el navegador; la descarga es una acción local de la persona. La cámara, cuando está activa, se compone en el video final.

## Iniciar

Con Python instalado, ejecuta en esta carpeta:

```sh
python -m http.server 8787 --bind 127.0.0.1
```

Abre `http://localhost:8787/` en un navegador compatible, elige los dispositivos y pulsa **Iniciar grabación**. El navegador solicita la pantalla o ventana; concede los permisos adicionales si activaste cámara o micrófono. Al detener, revisa el resultado y usa **Descargar video**. El archivo suele ser WebM; el formato concreto depende del navegador.

El servidor solo entrega los archivos de la aplicación. Esta primera versión no sube la grabación a ningún servicio. Las pistas independientes, anotaciones y edición por agentes todavía no están implementadas.

## Límites

La captura depende de las capacidades y los permisos del navegador y del sistema. Se prueba el recorrido indicado en `SPEC.md`; los resultados reales y las limitaciones de las pruebas están documentados por separado. El usuario debe revisar lo que comparte antes de grabar.
