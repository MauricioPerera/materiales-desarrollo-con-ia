"""Aplica silencio en el reloj original y después cortes a pistas prealineadas."""
import argparse
import importlib.util
import json
import tempfile
import wave
from pathlib import Path

HERE = Path(__file__).resolve().parent

def cargar(nombre, archivo):
    spec = importlib.util.spec_from_file_location(nombre, archivo)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

cortes = cargar('cortes', HERE.parent/'13-corte-revisado'/'aplicar_plan.py')
silencios = cargar('silencios', HERE.parent/'15-silenciar-instruccion'/'silenciar_intervalos.py')

def trasladar(conservar, silenciar):
    """Intersecciones de silencio trasladadas a la salida; final exclusivo."""
    salida=[]
    posicion=0
    for a,b in conservar:
        for c,d in silenciar:
            lo=max(a,c); hi=min(b,d)
            if lo<hi: salida.append([posicion+lo-a,posicion+hi-a])
        posicion+=b-a
    return salida

def aplicar(plan, pantalla, audio, destino, camara=None):
    total, partes = cortes.validar(plan)
    with wave.open(str(audio), 'rb') as src:
        silencios.validar(plan, src.getnframes())
    destino=Path(destino)
    if destino.exists(): raise FileExistsError('La salida debe ser una carpeta nueva')
    # La carpeta temporal es creada y eliminada por tempfile; las entradas nunca se alteran.
    with tempfile.TemporaryDirectory(prefix='plan-combinado-') as temporal:
        copia=Path(temporal)/'microfono-silenciado.wav'
        silencios.silenciar(plan,audio,copia)
        informe=cortes.aplicar(plan,pantalla,copia,destino,camara)
    informe['silenciar_original']=plan['silenciar']
    informe['silenciar_salida']=trasladar(partes,plan['silenciar'])
    informe['orden']='silenciar micrófono en el reloj original; cortar todas las pistas'
    (destino/'resultado.json').write_text(json.dumps(informe,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    return informe

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('plan',type=Path);p.add_argument('pantalla',type=Path);p.add_argument('audio',type=Path);p.add_argument('salida',type=Path);p.add_argument('--camara',type=Path)
    a=p.parse_args()
    print(json.dumps(aplicar(json.loads(a.plan.read_text(encoding='utf8')),a.pantalla,a.audio,a.salida,a.camara),ensure_ascii=False,indent=2))
if __name__=='__main__':main()
