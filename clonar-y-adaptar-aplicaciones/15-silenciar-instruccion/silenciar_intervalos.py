"""Silencia intervalos explícitos en PCM de 16 bits sin cambiar su duración."""
import argparse
import json
import wave
from pathlib import Path

FPS=30
RATE=48000
SAMPLES_PER_FRAME=RATE//FPS

def validar(plan, muestras):
    total=plan.get('duracion_fotogramas'); ranges=plan.get('silenciar')
    if type(plan.get('fps')) is not int or plan['fps']!=FPS:raise ValueError('El plan requiere 30 fotogramas por segundo')
    if type(total) is not int or total<=0 or total*SAMPLES_PER_FRAME!=muestras:raise ValueError('La duración declarada no coincide con el audio')
    if not isinstance(ranges,list) or not ranges:raise ValueError('Indica al menos un intervalo')
    end_prev=0
    for pair in ranges:
        if not isinstance(pair,list) or len(pair)!=2 or any(type(n) is not int for n in pair):raise ValueError('Cada intervalo requiere dos enteros')
        start,end=pair
        if not (end_prev<=start<end<=total):raise ValueError('Intervalos invertidos, solapados o fuera de rango')
        end_prev=end
    return [(a*SAMPLES_PER_FRAME,b*SAMPLES_PER_FRAME) for a,b in ranges]

def silenciar(plan,entrada,salida):
    entrada=Path(entrada);salida=Path(salida)
    if entrada.resolve()==salida.resolve():raise ValueError('La salida debe ser distinta de la entrada')
    with wave.open(str(entrada),'rb') as src:
        if src.getcomptype()!='NONE' or src.getsampwidth()!=2 or src.getframerate()!=RATE or src.getnchannels() not in (1,2):
            raise ValueError('Se requiere WAV PCM de 16 bits, 48 kHz y uno o dos canales')
        ranges=validar(plan,src.getnframes());channels=src.getnchannels();total=src.getnframes()
        # Exclusive creation refuses an existing file, including the input.
        with salida.open('xb') as raw:
            with wave.open(raw,'wb') as dst:
                dst.setnchannels(channels);dst.setsampwidth(2);dst.setframerate(RATE)
                at=0;frame_bytes=channels*2
                while at<total:
                    count=min(8192,total-at);chunk=bytearray(src.readframes(count))
                    if len(chunk)!=count*frame_bytes:raise ValueError('Audio truncado')
                    for a,b in ranges:
                        lo=max(a,at);hi=min(b,at+count)
                        if lo<hi:chunk[(lo-at)*frame_bytes:(hi-at)*frame_bytes]=bytes((hi-lo)*frame_bytes)
                    dst.writeframesraw(chunk);at+=count
    return {'muestras':total,'frecuencia':RATE,'canales':channels,'intervalos_fotogramas':plan['silenciar'],'nota':'Escucha los bordes; no se aplicaron fundidos ni se modificaron otras pistas.'}

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('plan',type=Path);parser.add_argument('entrada',type=Path);parser.add_argument('salida',type=Path)
    a=parser.parse_args();plan=json.loads(a.plan.read_text(encoding='utf8'));print(json.dumps(silenciar(plan,a.entrada,a.salida),ensure_ascii=False,indent=2))
if __name__=='__main__':main()
