"""Transcripción local y búsqueda aproximada de contexto. No edita los medios."""
import argparse
import json
import math
import subprocess
from pathlib import Path

def references(markers, segments, offset, duration, context=4):
    if offset is not None and not math.isfinite(offset):
        raise ValueError('El desplazamiento debe ser finito')
    if not math.isfinite(context) or context < 0:
        raise ValueError('El contexto debe ser finito y no negativo')
    out = []
    for marker in markers:
        item = {'marca': marker, 'estado': 'pendiente', 'segmentos': []}
        if marker.get('type') == 'instruction':
            start, end = marker.get('start_active_ms'), marker.get('end_active_ms')
            if marker.get('status') != 'closed' or end is None:
                item['estado'] = 'instrucción incompleta: revisar'; out.append(item); continue
        elif marker.get('type') == 'point':
            start = end = marker.get('active_ms')
        else:
            item['estado'] = 'tipo desconocido: revisar'; out.append(item); continue
        if not all(isinstance(x, (int, float)) and not isinstance(x, bool) and math.isfinite(x) and x >= 0 for x in (start, end)) or end < start:
            item['estado'] = 'tiempos inválidos: revisar'; out.append(item); continue
        if offset is None:
            item['estado'] = 'sin alineación de relojes: revisar'; out.append(item); continue
        a, b = start / 1000 + offset, end / 1000 + offset
        if a < 0 or b > duration:
            item['estado'] = 'referencia fuera del audio: revisar'; out.append(item); continue
        item['estado'] = 'contexto aproximado: revisar audio original'
        item['ventana_audio_s'] = [max(0, a-context), min(duration, b+context)]
        item['segmentos'] = [s for s in segments if s['fin'] >= item['ventana_audio_s'][0] and s['inicio'] <= item['ventana_audio_s'][1]]
        out.append(item)
    return out

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('audio', type=Path);p.add_argument('marcas', type=Path);p.add_argument('salida', type=Path)
    p.add_argument('--offset-audio', type=float, default=None, help='Segundos: tiempo de audio = tiempo activo + desplazamiento comprobado')
    p.add_argument('--contexto', type=float, default=4);p.add_argument('--modelo', default='small')
    args = p.parse_args()
    if args.salida.resolve() in (args.audio.resolve(), args.marcas.resolve()):
        p.error('La salida debe ser distinta de los archivos de entrada')
    if args.salida.exists():p.error('La salida ya existe; elige otro nombre')
    if args.offset_audio is not None and not math.isfinite(args.offset_audio):p.error('El desplazamiento debe ser finito')
    if not math.isfinite(args.contexto) or args.contexto < 0:p.error('El contexto debe ser finito y no negativo')
    metadata=json.loads(args.marcas.read_text(encoding='utf8'))
    if not isinstance(metadata.get('markers'), list):p.error('Se esperaba una lista markers en los metadatos')
    from faster_whisper import WhisperModel
    import numpy as np
    decoded=subprocess.run(['ffmpeg','-v','error','-i',str(args.audio),'-f','f32le','-ac','1','-ar','16000','pipe:1'],check=True,stdout=subprocess.PIPE)
    audio=np.frombuffer(decoded.stdout,dtype='<f4').copy()
    if not len(audio):p.error('El archivo no contiene audio decodificable')
    model=WhisperModel(args.modelo,device='cpu',compute_type='int8')
    segments,info=model.transcribe(audio,language='es',beam_size=5,word_timestamps=True,condition_on_previous_text=False)
    rows=[{'inicio':s.start,'fin':s.end,'texto':s.text.strip(),'palabras':[{'inicio':w.start,'fin':w.end,'texto':w.word.strip()} for w in (s.words or [])]} for s in segments]
    report={'duracion_audio_s':info.duration,'idioma':'es','modelo':args.modelo,'offset_audio_s':args.offset_audio,'advertencia':'Tiempos aproximados. Revisar audio y sincronización; no se aplicaron ediciones.', 'transcripcion':rows,'referencias':references(metadata['markers'],rows,args.offset_audio,info.duration,args.contexto)}
    with args.salida.open('x',encoding='utf8') as f:json.dump(report,f,ensure_ascii=False,indent=2)
    print(f'Informe creado: {args.salida}. Revisa el audio original y los relojes.')

if __name__=='__main__':main()
