# Del informe a un corte revisado

Este experimento conecta el [informe de transcripción y marcas](../12-transcribir-y-buscar/) con el [cortador de pistas prealineadas](../13-corte-revisado/). Prepara un borrador vacío, registra decisiones explícitas y permite aplicar un plan a una carpeta nueva. No interpreta instrucciones ni decide qué cortar.

## Preparación

Descarga el repositorio completo para conservar las rutas relativas entre carpetas. Necesitas Python, FFmpeg y FFprobe en el PATH. Los ejemplos incluidos usan pistas sintéticas creadas juntas: pantalla, voz y cámara opcional. El informe proviene de la prueba sintética anterior y su audio se adaptó para el ejemplo del cortador.

Desde esta carpeta, genera un borrador nuevo:

```sh
python flujo_revision.py preparar ../12-transcribir-y-buscar/ejemplo/informe-sintetico.json ../13-corte-revisado/ejemplo/pantalla.mp4 ../13-corte-revisado/ejemplo/microfono.wav borrador.json --camara ../13-corte-revisado/ejemplo/camara.mp4
```

El borrador contiene las referencias originales y una decisión pendiente por cada una. Incluye huellas de las fuentes, una lista de intervalos vacía y dos campos en `false`. Revisa el informe y las pistas antes de editarlo; sigue la [guía de revisión](revision.md).

## Completar y aplicar

Después de examinar los medios, registra una resolución (`incluida_en_plan` o `sin_cambio`) y un motivo para **cada** referencia. Deja una referencia pendiente si aún no sabes cómo resolverla. Registra los intervalos de fotogramas que se conservan y su duración total. Solo tras comprobar la alineación y completar la revisión cambia los campos correspondientes a `true`.

El plan sintético del episodio anterior usa `duracion_fotogramas: 340` y `conservar: [[0, 12], [255, 340]]`. Los finales son exclusivos. Son valores para **ese ejemplo**, no una regla para otras grabaciones.

Con el borrador completado y una carpeta de salida que no exista:

```sh
python flujo_revision.py aplicar borrador.json ../12-transcribir-y-buscar/ejemplo/informe-sintetico.json ../13-corte-revisado/ejemplo/pantalla.mp4 ../13-corte-revisado/ejemplo/microfono.wav salida-revisada --camara ../13-corte-revisado/ejemplo/camara.mp4
```

Para trabajar sin cámara, omite `--camara` en **ambos** comandos y prepara un borrador nuevo. El programa comprueba las huellas y rechaza campos pendientes, referencias alteradas o un plan inválido antes de crear la salida. Si falla la codificación puede quedar una carpeta parcial; revísala y utiliza un destino nuevo para repetir la prueba. La salida incluye el plan empleado.

## Qué no comprueba

La huella detecta cambios de contenido entre las dos fases; no demuestra que el informe pertenezca a esas pistas, que estén sincronizadas o que sean auténticos. Los campos editables registran una declaración, no prueban que una persona haya escuchado la toma. Tampoco hay protección frente a cambios durante la ejecución. El cortador conserva sus restricciones de formato y no corrige desfases ni deriva. Las pruebas realizadas usan decisiones simuladas y medios sintéticos; no verifican calidad editorial ni dispositivos reales.

Conserva las entradas y escucha y mira el resultado completo antes de utilizarlo.

## Fuentes

- [faster-whisper: transcripción con tiempos](https://github.com/SYSTRAN/faster-whisper#word-level-timestamps)
- [FFmpeg: filtros de recorte y concatenación](https://ffmpeg.org/ffmpeg-filters.html#concat)
