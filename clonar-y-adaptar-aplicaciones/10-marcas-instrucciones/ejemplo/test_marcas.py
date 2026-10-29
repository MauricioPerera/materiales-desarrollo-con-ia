"""Browser tests: synthetic media only; no screen, camera or microphone access."""
import http.server,json,os,socketserver,threading
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parent;OUT=ROOT/'evidencia-sintetica';OUT.mkdir(exist_ok=True)
class Server(socketserver.ThreadingMixIn,http.server.HTTPServer):daemon_threads=True
class Handler(http.server.SimpleHTTPRequestHandler):
 def __init__(self,*a,**kw):super().__init__(*a,directory=str(ROOT),**kw)
 def log_message(self,*a):pass
server=Server(('127.0.0.1',0),Handler);threading.Thread(target=server.serve_forever,daemon=True).start()
fake='''() => {
 const video=()=>{const c=document.createElement('canvas');c.width=640;c.height=360;const x=c.getContext('2d');function draw(){x.fillStyle='#23548d';x.fillRect(0,0,640,360);x.fillStyle='white';x.font='30px sans-serif';x.fillText('FUENTE SIMULADA',80,100);requestAnimationFrame(draw)}draw();return c.captureStream(15)};
 const audio=()=>{const ac=new AudioContext(),osc=ac.createOscillator(),dst=ac.createMediaStreamDestination();osc.connect(dst);osc.start();ac.resume();window.__audio=ac;return dst.stream};
 Object.defineProperty(navigator.mediaDevices,'getDisplayMedia',{configurable:true,value:async()=>video()});
 Object.defineProperty(navigator.mediaDevices,'getUserMedia',{configurable:true,value:async o=>o.video?video():audio()});
}'''
def download(page,name):
 with page.expect_download() as pending:page.locator(f'a[download="{name}"]').click()
 path=OUT/name;pending.value.save_as(str(path));return path
try:
 with sync_playwright() as p:
  browser=p.chromium.launch(executable_path=os.environ.get('PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH'),headless=True,args=['--autoplay-policy=no-user-gesture-required'])
  context=browser.new_context(viewport={'width':1280,'height':1100},accept_downloads=True);context.add_init_script(script='('+fake+')()')
  page=context.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
  page.goto(f'http://127.0.0.1:{server.server_port}/');page.click('#start');page.wait_for_function("document.querySelector('#status').textContent==='Grabando'")
  page.wait_for_timeout(300);page.fill('#marker-label','Revisar frase');page.click('#point');page.click('#interval');page.screenshot(path=str(OUT/'instruccion-abierta.png'));page.wait_for_timeout(300)
  page.click('#pause');page.wait_for_function("document.querySelector('#status').textContent==='En pausa'");assert page.locator('#point').is_disabled() and page.locator('#interval').is_disabled()
  page.wait_for_timeout(1300);page.click('#pause');page.wait_for_function("document.querySelector('#status').textContent==='Grabando'");page.wait_for_timeout(300);page.click('#interval');page.click('#point');page.wait_for_timeout(600);page.click('#stop')
  page.wait_for_function("document.querySelector('#status').textContent==='Archivos listos'");page.screenshot(path=str(OUT/'interfaz.png'))
  for name in ('pantalla.webm','camara.webm','microfono.webm'):assert download(page,name).stat().st_size>0
  metadata=json.loads(download(page,'metadatos.json').read_text(encoding='utf8'));marks=metadata['markers'];assert len(marks)==3
  (OUT/'metadatos-completo.json').write_text(json.dumps(metadata,ensure_ascii=False,indent=2),encoding='utf8')
  points=[m for m in marks if m['type']=='point'];interval=next(m for m in marks if m['type']=='instruction');assert len(points)==2 and interval['status']=='closed'
  assert points[0]['active_ms']<=interval['start_active_ms']<interval['end_active_ms']<=points[1]['active_ms']
  events={e['kind']:e['ms'] for e in metadata['events'] if e['kind'] in ('instruction-open','instruction-close','pause-request','resume-request')}
  wall=events['instruction-close']-events['instruction-open'];pause=events['resume-request']-events['pause-request'];active=interval['end_active_ms']-interval['start_active_ms']
  assert pause>1100 and abs(active-(wall-pause))<80,(wall,pause,active)
  page.get_by_text('Nueva toma').click();page.uncheck('#camera');page.uncheck('#microphone');page.click('#start');page.wait_for_function("document.querySelector('#status').textContent==='Grabando'");page.click('#interval');page.wait_for_timeout(500);page.click('#stop');page.wait_for_function("document.querySelector('#status').textContent==='Archivos listos'")
  incomplete=json.loads(download(page,'metadatos.json').read_text(encoding='utf8'));item=incomplete['markers'][0];assert item['status']=='incomplete' and item['end_active_ms'] is None
  (OUT/'metadatos-incompleto.json').write_text(json.dumps(incomplete,ensure_ascii=False,indent=2),encoding='utf8')
  page.get_by_text('Nueva toma').click();page.click('#start');page.wait_for_function("document.querySelector('#status').textContent==='Grabando'");page.click('#interval');page.click('#cancel');page.wait_for_function("document.querySelector('#status').textContent==='Listo para grabar'");assert page.locator('#results').is_hidden()
  assert not errors,errors
  result={'scope':'Chromium con fuentes sintéticas; no valida dispositivos reales ni comprensión de instrucciones.','punto_e_intervalo_cerrado':'ok','marcadores_ordenados':'ok','pause_wall_ms':round(pause),'interval_wall_ms':round(wall),'interval_active_ms':active,'diferencia_reloj_ms':round(abs(active-(wall-pause))), 'intervalo_incompleto':'ok','cancelacion':'ok','pistas_descargadas':3}
  (OUT/'resultados.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps(result,ensure_ascii=False,indent=2));context.close();browser.close()
finally:server.shutdown();server.server_close()
