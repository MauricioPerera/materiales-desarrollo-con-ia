"""Compone pantalla y voz con cámara opcional en tramos y posiciones explícitos."""
import argparse
import json
import subprocess
import wave
from pathlib import Path

def info_video(p,total):
    streams=json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_entries','stream=width,height,nb_frames,r_frame_rate,avg_frame_rate,start_time','-of','json',str(p)]))['streams']
    if len(streams)!=1:raise ValueError('Se requiere una pista de video')
    s=streams[0]
    if s.get('r_frame_rate')!='30/1' or s.get('avg_frame_rate')!='30/1' or int(s.get('nb_frames',0))!=total or abs(float(s.get('start_time',0)))>.001:
        raise ValueError('El video debe declarar 30 fps, iniciar en cero y coincidir con el plan')
    return s

def validar(plan,width,height):
    if type(plan.get('fps')) is not int or plan['fps']!=30:raise ValueError('El ejemplo requiere 30 fps')
    total=plan.get('duracion_fotogramas');size=plan.get('tamano_camara');segments=plan.get('tramos_camara')
    if type(total) is not int or total<=0:raise ValueError('Duración inválida')
    if not isinstance(size,list) or len(size)!=2 or any(type(v) is not int or v<=0 or v%2 for v in size):raise ValueError('El tamaño de cámara requiere dos enteros positivos pares')
    if not isinstance(segments,list):raise ValueError('La lista de tramos es obligatoria')
    last=0
    for s in segments:
        if not isinstance(s,dict) or any(type(s.get(k)) is not int for k in ('inicio','fin','x','y')):raise ValueError('Tramo inválido')
        a,b,x,y=(s[k] for k in ('inicio','fin','x','y'))
        if not (last<=a<b<=total):raise ValueError('Tramos invertidos, solapados o fuera de duración')
        if x<0 or y<0 or x%2 or y%2 or x+size[0]>width or y+size[1]>height:raise ValueError('La cámara debe caber dentro de la pantalla y usar coordenadas pares')
        last=b
    return total,size,segments

def componer(plan,pantalla,audio,salida,camara=None):
    total=plan.get('duracion_fotogramas')
    if type(total) is not int or total<=0:raise ValueError('Duración inválida')
    screen=info_video(pantalla,total);width,height=int(screen['width']),int(screen['height'])
    if width%2 or height%2:raise ValueError('La pantalla requiere dimensiones pares')
    total,size,parts=validar(plan,width,height)
    paths=[Path(pantalla),Path(audio)]+([Path(camara)] if camara else [])
    if len({p.resolve() for p in paths})!=len(paths):raise ValueError('Las entradas deben ser archivos distintos')
    if camara:info_video(camara,total)
    with wave.open(str(audio),'rb') as w:
        if w.getcomptype()!='NONE' or w.getsampwidth()!=2 or w.getframerate()!=48000 or w.getnchannels() not in (1,2) or w.getnframes()!=total*1600:
            raise ValueError('Se requiere WAV PCM de 16 bits y 48 kHz con duración coincidente')
    dest=Path(salida)
    if dest.suffix.lower()!='.mkv':raise ValueError('Este ejemplo genera un archivo MKV')
    if dest.exists():raise FileExistsError('La salida debe ser nueva')
    cmd=['ffmpeg','-v','error','-n','-i',str(pantalla),'-i',str(audio)]
    if camara and parts:
        cmd+=['-i',str(camara)]
        labels=''.join(f'[c{i}]' for i in range(len(parts)))
        graph=[f'[2:v]scale={size[0]}:{size[1]},format=yuva420p'+(f',split={len(parts)}{labels}' if len(parts)>1 else '[c0]')]
        previous='0:v'
        for i,s in enumerate(parts):
            output=f'v{i}';enable=f"gte(n,{s['inicio']})*lt(n,{s['fin']})"
            graph.append(f"[{previous}][c{i}]overlay=x={s['x']}:y={s['y']}:eof_action=pass:repeatlast=0:enable='{enable}'[{output}]")
            previous=output
        cmd+=['-filter_complex',';'.join(graph),'-map',f'[{previous}]']
    else:cmd+=['-map','0:v:0']
    cmd+=['-map','1:a:0','-frames:v',str(total),'-c:v','libx264','-preset','veryfast','-crf','18','-pix_fmt','yuv420p','-r','30','-c:a','pcm_s16le',str(dest)]
    subprocess.run(cmd,check=True)
    return {'fotogramas':total,'fps':30,'camara_incluida':bool(camara and parts),'tramos_camara':parts if camara else [],'nota':'Revisar imagen, sonido y sincronía; conservar las entradas.'}

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('plan',type=Path);p.add_argument('pantalla',type=Path);p.add_argument('audio',type=Path);p.add_argument('salida',type=Path);p.add_argument('--camara',type=Path)
    a=p.parse_args();result=componer(json.loads(a.plan.read_text(encoding='utf8')),a.pantalla,a.audio,a.salida,a.camara);print(json.dumps(result,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
