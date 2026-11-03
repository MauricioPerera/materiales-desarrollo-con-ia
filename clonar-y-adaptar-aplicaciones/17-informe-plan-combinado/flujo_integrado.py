"""Conecta referencias revisadas y un plan combinado sobre pistas prealineadas."""
import argparse
import importlib.util
import json
import wave
from pathlib import Path

ROOT=Path(__file__).resolve().parent.parent
def cargar(nombre, ruta):
    spec=importlib.util.spec_from_file_location(nombre,ruta)
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
    return mod
revision=cargar('revision',ROOT/'14-revision-y-corte'/'flujo_revision.py')
combinado=cargar('combinado',ROOT/'16-cortes-y-silencios'/'aplicar_plan_combinado.py')

def fuentes(informe,pantalla,audio,camara):
    roles={'informe':informe,'pantalla':pantalla,'audio':audio}
    if camara:roles['camara']=camara
    if len({Path(p).resolve() for p in roles.values()})!=len(roles):
        raise ValueError('Cada fuente debe ser un archivo diferente')
    return {k:revision.huella(p) for k,p in roles.items()}

def preparar(informe,pantalla,audio,camara,salida):
    report=revision.leer_informe(informe)
    draft={'version':2,'fuentes':fuentes(informe,pantalla,audio,camara),
           'referencias':report['referencias'],
           'decisiones':[{'indice':i,'resolucion':'pendiente','motivo':''} for i in range(len(report['referencias']))],
           'alineacion_comprobada':False,'revision_completada':False,
           'plan':{'fps':30,'duracion_fotogramas':None,'conservar':[],'silenciar':[]},
           'advertencia':'Declaraciones registradas; comprobar contenido, medios y sincronía.'}
    with Path(salida).open('x',encoding='utf8') as f:json.dump(draft,f,ensure_ascii=False,indent=2)
    return draft

def aplicar(borrador,informe,pantalla,audio,camara,salida):
    draft=json.loads(Path(borrador).read_text(encoding='utf8'));report=revision.leer_informe(informe)
    if draft.get('version')!=2:raise ValueError('Versión de borrador inválida')
    if draft.get('fuentes')!=fuentes(informe,pantalla,audio,camara):raise ValueError('Una fuente cambió o faltan pistas')
    if draft.get('referencias')!=report['referencias']:raise ValueError('Las referencias difieren del informe')
    if draft.get('revision_completada') is not True or draft.get('alineacion_comprobada') is not True:
        raise ValueError('Falta declarar revisión y alineación')
    decisions=draft.get('decisiones')
    if not isinstance(decisions,list) or len(decisions)!=len(report['referencias']):raise ValueError('Faltan decisiones')
    indices=[]
    for item in decisions:
        if not isinstance(item,dict) or type(item.get('indice')) is not int:raise ValueError('Índice inválido')
        if item.get('resolucion') not in ('incluida_en_plan','sin_cambio') or not isinstance(item.get('motivo'),str) or not item['motivo'].strip():
            raise ValueError('Hay referencias pendientes o sin motivo')
        indices.append(item['indice'])
    if sorted(indices)!=list(range(len(report['referencias']))):raise ValueError('Índices duplicados o ausentes')
    plan=draft.get('plan',{})
    combinado.cortes.validar(plan)
    with wave.open(str(audio),'rb') as src:combinado.silencios.validar(plan,src.getnframes())
    result=combinado.aplicar(plan,pantalla,audio,salida,camara)
    with (Path(salida)/'plan-revisado.json').open('x',encoding='utf8') as f:json.dump(draft,f,ensure_ascii=False,indent=2)
    return result

def main():
    p=argparse.ArgumentParser(description=__doc__);sub=p.add_subparsers(dest='accion',required=True)
    for name in ('preparar','aplicar'):
        q=sub.add_parser(name)
        if name=='aplicar':q.add_argument('borrador',type=Path)
        q.add_argument('informe',type=Path);q.add_argument('pantalla',type=Path);q.add_argument('audio',type=Path);q.add_argument('salida',type=Path);q.add_argument('--camara',type=Path)
    a=p.parse_args()
    result=preparar(a.informe,a.pantalla,a.audio,a.camara,a.salida) if a.accion=='preparar' else aplicar(a.borrador,a.informe,a.pantalla,a.audio,a.camara,a.salida)
    print(json.dumps(result,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
