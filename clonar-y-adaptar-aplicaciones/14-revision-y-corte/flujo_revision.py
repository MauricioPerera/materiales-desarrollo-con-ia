"""Prepara un borrador y aplica un plan explícito a pistas sintéticas prealineadas."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path

CORTE=Path(__file__).resolve().parent.parent/'13-corte-revisado'/'aplicar_plan.py'
spec=importlib.util.spec_from_file_location('corte_revisado',CORTE)
corte=importlib.util.module_from_spec(spec);spec.loader.exec_module(corte)

def huella(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
    return h.hexdigest()

def leer_informe(path):
    data=json.loads(Path(path).read_text(encoding='utf8'))
    if not isinstance(data.get('referencias'),list) or not data['referencias']:
        raise ValueError('El informe debe contener referencias')
    if any(not isinstance(item,dict) for item in data['referencias']):raise ValueError('Referencia inválida')
    return data

def preparar(informe,pantalla,audio,camara,salida):
    report=leer_informe(informe)
    roles={'informe':informe,'pantalla':pantalla,'audio':audio}
    if camara:roles['camara']=camara
    if len({Path(p).resolve() for p in roles.values()})!=len(roles):raise ValueError('Los archivos deben ser distintos')
    draft={'version':1,'fuentes':{k:huella(p) for k,p in roles.items()},'referencias':report['referencias'],
           'decisiones':[{'indice':i,'resolucion':'pendiente','motivo':''} for i in range(len(report['referencias']))],
           'alineacion_comprobada':False,'revision_completada':False,'plan':{'fps':30,'duracion_fotogramas':None,'conservar':[]},
           'advertencia':'Comprobar medios y alineación; la herramienta no interpreta instrucciones ni verifica la revisión humana.'}
    with Path(salida).open('x',encoding='utf8') as f:json.dump(draft,f,ensure_ascii=False,indent=2)
    return draft

def aplicar(borrador,informe,pantalla,audio,camara,salida):
    draft=json.loads(Path(borrador).read_text(encoding='utf8'));report=leer_informe(informe)
    if draft.get('version')!=1:raise ValueError('Versión de borrador inválida')
    roles={'informe':informe,'pantalla':pantalla,'audio':audio}
    if camara:roles['camara']=camara
    if draft.get('fuentes')!={k:huella(p) for k,p in roles.items()}:raise ValueError('Una fuente cambió o faltan pistas; prepara y revisa otro borrador')
    if draft.get('referencias')!=report['referencias']:raise ValueError('Las referencias difieren del informe')
    if draft.get('revision_completada') is not True or draft.get('alineacion_comprobada') is not True:
        raise ValueError('Falta registrar la revisión y la alineación')
    decisions=draft.get('decisiones')
    if not isinstance(decisions,list) or len(decisions)!=len(report['referencias']):raise ValueError('Faltan decisiones')
    indices=[]
    for decision in decisions:
        if not isinstance(decision,dict) or type(decision.get('indice')) is not int:raise ValueError('Índice inválido')
        if decision.get('resolucion') not in ('incluida_en_plan','sin_cambio') or not isinstance(decision.get('motivo'),str) or not decision['motivo'].strip():
            raise ValueError('Hay referencias pendientes o sin motivo')
        indices.append(decision['indice'])
    if sorted(indices)!=list(range(len(report['referencias']))):raise ValueError('Índices duplicados o ausentes')
    corte.validar(draft.get('plan',{}))
    result=corte.aplicar(draft['plan'],pantalla,audio,salida,camara)
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
