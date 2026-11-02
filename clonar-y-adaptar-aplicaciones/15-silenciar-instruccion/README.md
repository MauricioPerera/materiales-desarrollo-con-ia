# Silenciar una instrucción sin quitar tiempo

Este experimento crea una copia de la pista de micrófono con intervalos explícitos en silencio. La duración y las muestras fuera de esos intervalos se conservan. El programa no abre la pantalla ni la cámara, no decide qué silenciar y no modifica las entradas.

## Probar el ejemplo

Descarga el repositorio completo para conservar las rutas relativas. Necesitas Python 3.12 o posterior. Desde esta carpeta:

```sh
python silenciar_intervalos.py plan-ejemplo.json ../13-corte-revisado/ejemplo/microfono.wav microfono-silenciado.wav
```

La salida debe tener un nombre nuevo. Puedes comparar el resultado con el micrófono original y colocar ambos junto a las [pistas sintéticas de pantalla y cámara](../13-corte-revisado/ejemplo/). Esos medios fueron preparados para compartir un reloj; una toma real requiere una comprobación propia de sincronía. Si ocurre un error durante la escritura puede quedar una salida parcial: revísala y utiliza otro nombre al repetir.

## El plan

Los intervalos `[inicio, fin)` se indican en fotogramas: el inicio se incluye y el final se excluye. El ejemplo declara 340 fotogramas a 30 fps y silencia `[115, 225)`, aproximadamente de 3,83 a 7,50 segundos. A 48.000 muestras por segundo, cada fotograma equivale a 1.600 muestras por canal. Estos límites se definieron para **este audio sintético** y no sirven automáticamente para otra grabación.

La herramienta acepta WAV PCM sin comprimir de 16 bits, 48 kHz y uno o dos canales, con una duración igual a la declarada en el plan. El archivo de salida puede no conservar metadatos auxiliares del original. Los intervalos deben estar ordenados, sin solaparse y dentro de la duración. Una ruta de salida existente se rechaza.

## Qué revisar

- Una marca o una transcripción ayuda a buscar; escucha el audio para decidir los límites reales.
- El silencio sustituye **todo** el sonido del micrófono en ese intervalo, incluido el ambiente. No silencia una pista de audio del sistema ni modifica otros archivos.
- Un cambio brusco puede producir clics o sonar artificial. El ejemplo no aplica fundidos ni restaura ambiente; escucha los bordes antes de usarlo.
- La operación no elimina una frase equivocada que esté fuera del intervalo y no corrige desfases entre pistas.
- Si también hay cortes, revisa cómo cambian los tiempos y el orden de las operaciones.

Las pruebas comparan muestras antes, dentro y después del intervalo, duración, conservación de originales, rechazo de planes inválidos y un caso estéreo sintético. No sustituyen la escucha ni prueban dispositivos reales. Esta herramienta es independiente del [flujo de revisión anterior](../14-revision-y-corte/).

## Fuentes

- [Python: lectura y escritura de WAV](https://docs.python.org/3/library/wave.html)
- [Manual de Audacity: fundidos y clics en los bordes](https://manual.audacityteam.org/man/fade_and_crossfade.html)
