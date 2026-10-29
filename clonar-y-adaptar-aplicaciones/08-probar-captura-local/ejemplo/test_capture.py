"""Browser integration tests with explicitly synthetic screen/camera/audio sources."""
import contextlib,http.server,json,os,socketserver,subprocess,threading,time
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'evidencia';OUT.mkdir(exist_ok=True)
CHROME=os.environ.get('PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH')
class Server(socketserver.ThreadingMixIn,http.server.HTTPServer):daemon_threads=True
class Handler(http.server.SimpleHTTPRequestHandler):
 def __init__(self,*args,**kwargs):super().__init__(*args,directory=str(ROOT),**kwargs)
 def log_message(self,*args):pass
server=Server(('127.0.0.1',0),Handler);threading.Thread(target=server.serve_forever,daemon=True).start()
url=f'http://127.0.0.1:{server.server_port}/'
fake='''() => {
 window.__sourceMode='ok';window.__streams=[];
 const screen=()=>{const c=document.createElement('canvas');c.width=1280;c.height=720;const x=c.getContext('2d');x.fillStyle='#23548d';x.fillRect(0,0,1280,720);x.fillStyle='white';x.font='bold 55px sans-serif';x.fillText('PANTALLA SIMULADA',100,180);const s=c.captureStream(15);window.__streams.push(s);return s;};
 const cam=()=>{const c=document.createElement('canvas');c.width=320;c.height=240;const x=c.getContext('2d');x.fillStyle='#df542b';x.fillRect(0,0,320,240);x.fillStyle='white';x.font='bold 28px sans-serif';x.fillText('CÁMARA',92,115);const s=c.captureStream(15);window.__streams.push(s);return s;};
 const audio=()=>{const ac=new AudioContext();const dst=ac.createMediaStreamDestination(),osc=ac.createOscillator();osc.frequency.value=440;osc.connect(dst);osc.start();ac.resume();window.__audio=ac;return dst.stream;};
 Object.defineProperty(navigator.mediaDevices,'getDisplayMedia',{configurable:true,value:async()=>{if(window.__sourceMode==='deny')throw new DOMException('denied','NotAllowedError');return screen();}});
 Object.defineProperty(navigator.mediaDevices,'getUserMedia',{configurable:true,value:async opts=>opts.video?cam():audio()});
 window.__endCapture=()=>window.__streams[0].getVideoTracks()[0].dispatchEvent(new Event('ended'));
}'''
def meta(path):return json.loads(subprocess.run(['ffprobe','-v','error','-show_streams','-of','json',str(path)],capture_output=True,text=True,check=True).stdout)
def frame(path,name):
 out=OUT/name
 subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-ss','0.5','-i',str(path),'-frames:v','1',str(out)],check=True)
 return out
results=[]
try:
 with sync_playwright() as pw:
  browser=pw.chromium.launch(executable_path=CHROME,headless=True,args=['--autoplay-policy=no-user-gesture-required'])
  context=browser.new_context(viewport={'width':1440,'height':1000},accept_downloads=True)
  context.add_init_script(script='('+fake+')()')
  page=context.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)));page.goto(url);page.screenshot(path=str(OUT/'interfaz-inicial.png'))
  page.click('#start');page.wait_for_function("document.querySelector('#status').textContent==='Grabando'")
  page.wait_for_timeout(1300);page.click('#pause');page.wait_for_function("document.querySelector('#status').textContent==='En pausa'");page.wait_for_timeout(400);page.click('#pause');page.wait_for_timeout(1200);page.click('#stop');page.wait_for_function("document.querySelector('#status').textContent==='Grabación lista'")
  with page.expect_download() as d:page.click('#download')
  screen_only=OUT/'sin-camara.webm';d.value.save_as(str(screen_only));probe=meta(screen_only);assert any(s['codec_type']=='video' for s in probe['streams']);assert not any(s['codec_type']=='audio' for s in probe['streams']);frame(screen_only,'sin-camara-frame.png')
  assert page.locator('#result').is_visible();results.append({'test':'pantalla sin cámara; pausa y reanudación','result':'ok','source':'pantalla sintética','streams':[s['codec_type'] for s in probe['streams']]})
  page.click('#new');page.check('#camera');page.check('#microphone');page.click('#start');page.wait_for_function("document.querySelector('#status').textContent==='Grabando'");page.wait_for_timeout(1400);page.screenshot(path=str(OUT/'interfaz-grabando-fuentes-simuladas.png'));page.wait_for_timeout(1000);page.click('#stop');page.wait_for_function("document.querySelector('#status').textContent==='Grabación lista'")
  with page.expect_download() as d:page.click('#download')
  both=OUT/'con-camara-y-voz-simulada.webm';d.value.save_as(str(both));probe=meta(both);assert {'video','audio'} <= {s['codec_type'] for s in probe['streams']};img=frame(both,'con-camara-frame.png')
  from PIL import Image
  im=Image.open(img).convert('RGB');w,h=im.size;base=im.getpixel((int(w*.2),int(h*.5)));bubble=im.getpixel((int(w*.92),int(h*.90)));assert base[2]>base[0] and bubble[0]>bubble[2],(base,bubble)
  results.append({'test':'pantalla, cámara y micrófono en archivo descargado','result':'ok','source':'pantalla, cámara y tono sintéticos','pixel_pantalla':base,'pixel_camara':bubble,'streams':[s['codec_type'] for s in probe['streams']]})
  page.click('#new');page.uncheck('#camera');page.uncheck('#microphone');page.evaluate("window.__sourceMode='deny'");page.click('#start');page.wait_for_function("document.querySelector('#status').textContent==='Listo para grabar'");assert 'permiso' in page.locator('#message').inner_text().lower();results.append({'test':'permiso rechazado','result':'ok','source':'excepción simulada'})
  page.evaluate("window.__sourceMode='ok'");page.click('#start');page.wait_for_function("document.querySelector('#status').textContent==='Grabando'");page.wait_for_timeout(1300);page.evaluate('window.__endCapture()');page.wait_for_function("document.querySelector('#status').textContent==='Grabación lista'");assert 'terminó' in page.locator('#message').inner_text().lower();results.append({'test':'fin externo de pantalla','result':'ok','source':'evento de fin simulado'})
  page.click('#new');page.click('#start');page.wait_for_function("document.querySelector('#status').textContent==='Grabando'");page.wait_for_timeout(2100);page.click('#pause');frozen=page.locator('#timer').inner_text();page.wait_for_timeout(1300);assert page.locator('#timer').inner_text()==frozen;page.click('#stop');page.wait_for_function("document.querySelector('#status').textContent==='Grabación lista'");assert page.locator('#timer').inner_text()==frozen;results.append({'test':'detener en pausa conserva el tiempo','result':'ok','source':'fuente sintética','timer':frozen})
  page.click('#new');page.click('#start');page.wait_for_function("document.querySelector('#status').textContent==='Grabando'");page.wait_for_timeout(800);page.click('#cancel');page.wait_for_function("document.querySelector('#status').textContent==='Listo para grabar'");assert page.locator('#download').is_hidden();results.append({'test':'cancelar toma','result':'ok','source':'fuente sintética'})
  assert not errors,errors
  context.close();browser.close()
finally:server.shutdown();server.server_close()
(OUT/'resultados.json').write_text(json.dumps({'scope':'Pruebas automáticas en Chromium con fuentes y eventos sintéticos; no validan permisos ni hardware real.','results':results},ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(results,ensure_ascii=False,indent=2))
