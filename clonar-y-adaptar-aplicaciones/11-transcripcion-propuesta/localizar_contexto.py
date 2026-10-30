"""Agrupa texto ilustrativo cerca de marcas; no aplica ni calcula cortes."""
import json
import sys
from pathlib import Path

def informe(datos, margen=4.0):
    resultado = []
    for marca in datos['marcas']:
        inicio = float(marca['inicio'])
        fin = marca.get('fin')
        if marca.get('estado') != 'cerrada' or fin is None:
            resultado.append({'marca': marca, 'estado': 'revisar: intervalo incompleto', 'contexto': []})
            continue
        fin = float(fin)
        if fin < inicio:
            raise ValueError('El final precede al inicio')
        contexto = [s for s in datos['transcripcion'] if s['fin'] >= inicio-margen and s['inicio'] <= fin+margen]
        resultado.append({'marca': marca, 'estado': 'revisar: tiempos aproximados; sin decisión de corte', 'contexto': contexto})
    return {'reloj': datos['reloj'], 'advertencia': 'No se ha editado ningún medio. Verifica el reloj, el audio y la imagen.', 'referencias': resultado}

if __name__ == '__main__':
    if len(sys.argv) != 2:
        raise SystemExit('Uso: python localizar_contexto.py ejemplo.json')
    datos = json.loads(Path(sys.argv[1]).read_text(encoding='utf8'))
    print(json.dumps(informe(datos), ensure_ascii=False, indent=2))
