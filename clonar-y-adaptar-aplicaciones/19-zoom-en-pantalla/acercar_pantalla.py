"""Aplica un acercamiento fijo a pantalla y superpone una cámara opcional."""
import argparse, json, subprocess, wave
from pathlib import Path

def video_info(path, total):
    data=json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_entries','stream=width,height,nb_frames,r_frame_rate,avg_frame_rate,start_time','-of','json',str(path)]))['streams']
    if len(data)!=1: raise ValueError('Se requiere una pista de video')
    v=data[0]
    if v.get('r_frame_rate')!='30/1' or v.get('avg_frame_rate')!='30/1' or int(v.get('nb_frames',0))!=total or abs(float(v.get('start_time',0)))>.001: raise ValueError('El video debe declarar 30 fps, iniciar en cero y coincidir con el plan')
    return v

def validar(plan,w,h):
    total=plan.get('duracion_fotogramas'); region=plan.get('region'); parts=plan.get('tramos_zoom'); cam=plan.get('camara')
    if plan.get('fps')!=30 or type(total) is not int or total<=0: raise ValueError('Duración o frecuencia inválida')
    if not isinstance(region,list) or len(region)!=4 or any(type(v) is not int or v%2 for v in region): raise ValueError('La región requiere cuatro enteros pares')
    x,y,rw,rh=region
    if x<0 or y<0 or rw<=0 or rh<=0 or x+rw>w or y+rh>h or rw*h!=rh*w: raise ValueError('Región fuera de pantalla o con proporción distinta')
    if not isinstance(parts,list) or not parts: raise ValueError('Se requiere al menos un intervalo')
    last=0
    for t in parts:
        if not isinstance(t,list) or len(t)!=2 or any(type(v) is not int for v in t) or not last<=t[0]<t[1]<=total: raise ValueError('Intervalos inválidos o solapados')
        last=t[1]
    if not isinstance(cam,list) or len(cam)!=4 or any(type(v) is not int or v%2 for v in cam): raise ValueError('Cámara inválida')
    cx,cy,cw,ch=cam
    if cx<0 or cy<0 or cw<=0 or ch<=0 or cx+cw>w or cy+ch>h: raise ValueError('La cámara debe caber en la pantalla')
    return total,region,parts,cam

def componer(plan,pantalla,audio,salida,camara=None):
    total=plan.get('duracion_fotogramas')
    if type(total) is not int or total<=0: raise ValueError('Duración inválida')
    v=video_info(pantalla,total); w,h=int(v['width']),int(v['height'])
    total,region,parts,cam=validar(plan,w,h)
    inputs=[Path(pantalla),Path(audio)]+([Path(camara)] if camara else [])
    if len({p.resolve() for p in inputs})!=len(inputs): raise ValueError('Las entradas deben ser distintas')
    if camara: video_info(camara,total)
    with wave.open(str(audio),'rb') as wav:
        if wav.getcomptype()!='NONE' or wav.getsampwidth()!=2 or wav.getframerate()!=48000 or wav.getnchannels() not in (1,2) or wav.getnframes()!=total*1600: raise ValueError('Se requiere WAV PCM de 16 bits y 48 kHz con duración coincidente')
    dest=Path(salida)
    if dest.suffix.lower()!='.mkv': raise ValueError('La salida debe ser MKV')
    if dest.exists(): raise FileExistsError('La salida debe ser nueva')
    x,y,rw,rh=region; cx,cy,cw,ch=cam
    enabled='+'.join(f'gte(n,{a})*lt(n,{b})' for a,b in parts)
    graph=f"[0:v]split=2[base][source];[source]crop={rw}:{rh}:{x}:{y},scale={w}:{h}[zoom];[base][zoom]overlay=0:0:enable='{enabled}':eof_action=pass:repeatlast=0[screen]"
    cmd=['ffmpeg','-v','error','-n','-i',str(pantalla),'-i',str(audio)]
    if camara:
        cmd+=['-i',str(camara)]
        graph+=f';[2:v]scale={cw}:{ch}[cam];[screen][cam]overlay={cx}:{cy}:eof_action=pass:repeatlast=0[out]'
    else: graph+=';[screen]null[out]'
    cmd+=['-filter_complex',graph,'-map','[out]','-map','1:a:0','-frames:v',str(total),'-c:v','libx264','-preset','veryfast','-crf','18','-pix_fmt','yuv420p','-r','30','-c:a','pcm_s16le',str(dest)]
    subprocess.run(cmd,check=True)
    return {'fotogramas':total,'fps':30,'region':region,'tramos_zoom':parts,'camara_incluida':bool(camara)}

def main():
    p=argparse.ArgumentParser(description=__doc__); p.add_argument('plan',type=Path);p.add_argument('pantalla',type=Path);p.add_argument('audio',type=Path);p.add_argument('salida',type=Path);p.add_argument('--camara',type=Path)
    a=p.parse_args(); print(json.dumps(componer(json.loads(a.plan.read_text(encoding='utf8')),a.pantalla,a.audio,a.salida,a.camara),ensure_ascii=False,indent=2))
if __name__=='__main__': main()
