"""Aplica a pistas prealineadas un plan explícito de tramos a conservar."""
import argparse
import json
import subprocess
from pathlib import Path

FPS=30
RATE=48000

def validar(plan):
    if plan.get('fps') != FPS or isinstance(plan.get('fps'), bool):
        raise ValueError('El ejemplo requiere 30 fps')
    total=plan.get('duracion_fotogramas'); parts=plan.get('conservar')
    if type(total) is not int or total <= 0 or not isinstance(parts,list) or not parts:
        raise ValueError('Duración o lista de intervalos inválida')
    last=0
    for part in parts:
        if not isinstance(part,list) or len(part)!=2 or any(type(x) is not int for x in part):
            raise ValueError('Cada intervalo debe contener dos fotogramas enteros')
        a,b=part
        if not (last <= a < b <= total):raise ValueError('Intervalos invertidos, solapados o fuera de duración')
        last=b
    return total,parts

def info(path, kind):
    data=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-of','json',str(path)]))
    matches=[s for s in data['streams'] if s['codec_type']==kind]
    if len(matches)!=1:raise ValueError(f'Se esperaba una pista de {kind}: {path.name}')
    s=matches[0]
    if abs(float(s.get('start_time',0)))>0.001:raise ValueError('La pista no comienza en cero; revisa la alineación')
    return s

def aplicar(plan, pantalla, audio, salida, camara=None):
    total,parts=validar(plan)
    paths=[Path(pantalla),Path(audio)]+([Path(camara)] if camara else [])
    if len({p.resolve() for p in paths})!=len(paths):raise ValueError('Las pistas deben ser archivos diferentes')
    screen=info(paths[0],'video'); sound=info(paths[1],'audio'); camera=info(paths[2],'video') if camara else None
    for v in [screen]+([camera] if camera else []):
        if v.get('r_frame_rate')!='30/1' or v.get('avg_frame_rate')!='30/1' or int(v.get('nb_frames',0))!=total:
            raise ValueError('El video debe tener 30 fps constantes y la duración exacta del plan')
    if int(sound.get('sample_rate',0))!=RATE or abs(float(sound.get('duration',0))-total/FPS)>1/RATE:
        raise ValueError('El audio debe ser de 48 kHz y tener la duración exacta del plan')
    dest=Path(salida)
    dest.mkdir(parents=False,exist_ok=False)
    def edit(src, name, audio_mode=False):
        prefix='a' if audio_mode else 'v'; count=len(parts)
        splitter='asplit' if audio_mode else 'split'
        labels=''.join(f'[{prefix}{i}]' for i in range(count))
        graph=[f'[0:{prefix}:0]{splitter}={count}{labels}'] if count>1 else [f'[0:{prefix}:0]{"anull" if audio_mode else "null"}[{prefix}0]']
        for i,(start,end) in enumerate(parts):
            trim=(f'atrim=start_sample={start*1600}:end_sample={end*1600},asetpts=PTS-STARTPTS' if audio_mode else f'trim=start_frame={start}:end_frame={end},setpts=PTS-STARTPTS')
            graph.append(f'[{prefix}{i}]{trim}[t{i}]')
        inputs=''.join(f'[t{i}]' for i in range(count));graph.append(f'{inputs}concat=n={count}:v={0 if audio_mode else 1}:a={1 if audio_mode else 0}[out]')
        codec=['-c:a','pcm_s16le','-ar',str(RATE)] if audio_mode else ['-c:v','libx264','-preset','veryfast','-crf','18','-pix_fmt','yuv420p','-r','30']
        subprocess.run(['ffmpeg','-v','error','-n','-i',str(src),'-filter_complex',';'.join(graph),'-map','[out]',*codec,str(dest/name)],check=True)
    edit(paths[0],'pantalla.mp4')
    if camara:edit(paths[2],'camara.mp4')
    edit(paths[1],'microfono.wav',True)
    report={'fps':FPS,'muestras_por_segundo':RATE,'conservar':parts,'fotogramas_salida':sum(b-a for a,b in parts),'camara':bool(camara),'nota':'Pistas prealineadas; verificar las uniones y conservar los originales.'}
    (dest/'resultado.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    return report

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('plan',type=Path);p.add_argument('pantalla',type=Path);p.add_argument('audio',type=Path);p.add_argument('salida',type=Path);p.add_argument('--camara',type=Path)
    args=p.parse_args(); report=aplicar(json.loads(args.plan.read_text(encoding='utf8')),args.pantalla,args.audio,args.salida,args.camara); print(json.dumps(report,ensure_ascii=False,indent=2))

if __name__=='__main__':main()
