"""Compone zoom manual en el reloj original y corta imagen y voz juntas."""
import argparse, importlib.util, json, subprocess, tempfile
from pathlib import Path
HERE=Path(__file__).resolve().parent
def cargar(nombre,archivo):
 spec=importlib.util.spec_from_file_location(nombre,archivo);mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);return mod
cortes=cargar('cortes',HERE.parent/'13-corte-revisado'/'aplicar_plan.py')
zoom=cargar('zoom',HERE.parent/'19-zoom-en-pantalla'/'acercar_pantalla.py')

def trasladar(conservar,intervalos):
 """Conserva las intersecciones, con referencia original y de salida."""
 partes=[]; posicion=0
 for a,b in conservar:
  for c,d in intervalos:
   lo=max(a,c);hi=min(b,d)
   if lo<hi:partes.append({'original':[lo,hi],'salida':[posicion+lo-a,posicion+hi-a]})
  posicion+=b-a
 return partes

def aplicar(plan,pantalla,audio,destino,camara=None):
 total,partes=cortes.validar(plan)
 screen=zoom.video_info(pantalla,total); zoom.validar(plan,int(screen['width']),int(screen['height']))
 dest=Path(destino)
 if dest.exists():raise FileExistsError('La salida debe ser una carpeta nueva')
 # La composición y la carpeta final son nuevas; las entradas no se reemplazan.
 with tempfile.TemporaryDirectory(prefix='cortes-zoom-') as tmp:
  base=Path(tmp)/'composicion.mkv'
  zoom.componer(plan,pantalla,audio,base,camara)
  dest.mkdir(parents=False,exist_ok=False)
  count=len(partes); graph=[]
  for stream,prefix in [('v','v'),('a','a')]:
   splitter='split' if stream=='v' else 'asplit'
   graph.append(f'[0:{stream}:0]{splitter}={count}'+''.join(f'[{prefix}{i}]' for i in range(count)) if count>1 else f'[0:{stream}:0]{"null" if stream=="v" else "anull"}[{prefix}0]')
   for i,(a,b) in enumerate(partes):
    cut=f'trim=start_frame={a}:end_frame={b},setpts=PTS-STARTPTS' if stream=='v' else f'atrim=start_sample={a*1600}:end_sample={b*1600},asetpts=PTS-STARTPTS'
    graph.append(f'[{prefix}{i}]{cut}[{prefix}t{i}]')
   graph.append(''.join(f'[{prefix}t{i}]' for i in range(count))+f'concat=n={count}:v={1 if stream=="v" else 0}:a={0 if stream=="v" else 1}[{prefix}out]')
  output=dest/'resultado.mkv'
  subprocess.run(['ffmpeg','-v','error','-n','-i',str(base),'-filter_complex',';'.join(graph),'-map','[vout]','-map','[aout]','-c:v','libx264','-preset','veryfast','-crf','18','-pix_fmt','yuv420p','-r','30','-c:a','pcm_s16le',str(output)],check=True)
 report={'fps':30,'fotogramas_original':total,'conservar':partes,'zoom_original':plan['tramos_zoom'],'zoom_conservado':trasladar(partes,plan['tramos_zoom']),'fotogramas_salida':sum(b-a for a,b in partes),'camara':bool(camara),'nota':'Pistas prealineadas: revisar imagen, sonido y sincronía.'}
 (dest/'resultado.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8');return report

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('plan',type=Path);p.add_argument('pantalla',type=Path);p.add_argument('audio',type=Path);p.add_argument('salida',type=Path);p.add_argument('--camara',type=Path)
 a=p.parse_args();print(json.dumps(aplicar(json.loads(a.plan.read_text(encoding='utf8')),a.pantalla,a.audio,a.salida,a.camara),ensure_ascii=False,indent=2))
if __name__=='__main__':main()
