"""Measure separate recordings using synthetic sources only, never real devices."""
import http.server,json,os,socketserver,subprocess,threading,time
from pathlib import Path
from playwright.sync_api import sync_playwright
import numpy as np

ROOT=Path(__file__).resolve().parent;OUT=ROOT/'evidencia-sintetica';OUT.mkdir(exist_ok=True)
class Server(socketserver.ThreadingMixIn,http.server.HTTPServer):daemon_threads=True
class Handler(http.server.SimpleHTTPRequestHandler):
 def __init__(self,*a,**kw):super().__init__(*a,directory=str(ROOT),**kw)
 def log_message(self,*a):pass
server=Server(('127.0.0.1',0),Handler);threading.Thread(target=server.serve_forever,daemon=True).start()
fake='''() => {
 window.__beacon=false;window.__fakeStreams=[];
 const video=(w,h)=>{let c=document.createElement('canvas');c.width=w;c.height=h;let x=c.getContext('2d');function draw(){x.fillStyle=window.__beacon?'#e03823':'#14518d';x.fillRect(0,0,w,h);requestAnimationFrame(draw)}draw();let s=c.captureStream(30);window.__fakeStreams.push(s);return s};
 const audio=()=>{let ac=new AudioContext(),osc=ac.createOscillator(),gain=ac.createGain(),dst=ac.createMediaStreamDestination();gain.gain.value=0;osc.frequency.value=440;osc.connect(gain).connect(dst);osc.start();ac.resume();window.__audio=ac;window.__gain=gain;return dst.stream};
 Object.defineProperty(navigator.mediaDevices,'getDisplayMedia',{configurable:true,value:async()=>video(640,360)});
 Object.defineProperty(navigator.mediaDevices,'getUserMedia',{configurable:true,value:async o=>o.video?video(320,240):audio()});
 window.__signal=(on)=>{window.__beacon=on;window.__gain.gain.value=on?.35:0};
}'''
def media_info(path):return json.loads(subprocess.run(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(path)],capture_output=True,text=True,check=True).stdout)
def color_transition(path):
 raw=subprocess.run(['ffmpeg','-v','error','-i',str(path),'-vf','fps=30,scale=1:1','-f','rawvideo','-pix_fmt','rgb24','pipe:1'],capture_output=True,check=True).stdout
 colors=np.frombuffer(raw,dtype=np.uint8).reshape(-1,3).astype(np.int16);on=colors[:,0]>colors[:,2]+40
 indexes=np.where(np.diff(np.r_[False,on].astype(int))==1)[0]
 if len(indexes)!=2:raise AssertionError(f'Expected two video signals in {path.name}: {indexes}')
 return [round(int(i)/30,3) for i in indexes]
def audio_transition(path):
 raw=subprocess.run(['ffmpeg','-v','error','-i',str(path),'-f','s16le','-ar','16000','-ac','1','pipe:1'],capture_output=True,check=True).stdout
 samples=np.frombuffer(raw,dtype='<i2').astype(np.float64);window=160
 rms=np.array([np.sqrt(np.mean(samples[i:i+window]**2)) for i in range(0,len(samples)-window,window)])
 on=rms>500;indexes=np.where(np.diff(np.r_[False,on].astype(int))==1)[0]
 if len(indexes)!=2:raise AssertionError(f'Expected two audio signals: {indexes}')
 return [round(int(i)/100,3) for i in indexes]
try:
 with sync_playwright() as pw:
  chrome=os.environ.get('PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH')
  browser=pw.chromium.launch(executable_path=chrome,headless=True,args=['--autoplay-policy=no-user-gesture-required'])
  context=browser.new_context(viewport={'width':1280,'height':900},accept_downloads=True);context.add_init_script(script='('+fake+')()')
  page=context.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
  page.goto(f'http://127.0.0.1:{server.server_port}/');page.click('#start');page.wait_for_function("document.querySelector('#status').textContent==='Grabando'")
  page.wait_for_timeout(500);page.evaluate('window.__signal(true)');page.wait_for_timeout(350);page.evaluate('window.__signal(false)');page.wait_for_timeout(350)
  page.click('#pause');page.wait_for_function("document.querySelector('#status').textContent==='En pausa'");page.wait_for_timeout(1000)
  page.click('#pause');page.wait_for_function("document.querySelector('#status').textContent==='Grabando'");page.wait_for_timeout(400);page.evaluate('window.__signal(true)');page.wait_for_timeout(350);page.evaluate('window.__signal(false)');page.wait_for_timeout(800);page.click('#stop')
  page.wait_for_function("document.querySelector('#status').textContent==='Archivos listos'")
  for name in ('pantalla.webm','camara.webm','microfono.webm','metadatos.json'):
   with page.expect_download() as d:page.locator(f'a[download="{name}"]').click()
   d.value.save_as(str(OUT/name))
  page.screenshot(path=str(OUT/'resultado.png'));assert not errors,errors
  for file,kind in [('pantalla.webm','video'),('camara.webm','video'),('microfono.webm','audio')]:
   assert any(s['codec_type']==kind for s in media_info(OUT/file)['streams'])
  marker={'pantalla':color_transition(OUT/'pantalla.webm'),'camara':color_transition(OUT/'camara.webm'),'microfono':audio_transition(OUT/'microfono.webm')}
  spread=[round(max(values)-min(values),3) for values in zip(*marker.values())]
  metadata=json.loads((OUT/'metadatos.json').read_text(encoding='utf8'))
  assert {'pause-request','resume-request','stop-request'} <= {e['kind'] for e in metadata['events']}
  assert max(spread)<0.25,(marker,spread)
  page.get_by_text('Nueva toma').click();page.uncheck('#camera');page.uncheck('#microphone');page.click('#start');page.wait_for_function("document.querySelector('#status').textContent==='Grabando'");page.wait_for_timeout(900);page.click('#stop');page.wait_for_function("document.querySelector('#status').textContent==='Archivos listos'")
  assert page.locator('a[download="pantalla.webm"]').count()==1 and page.locator('a[download="camara.webm"]').count()==0 and page.locator('a[download="microfono.webm"]').count()==0
  page.get_by_text('Nueva toma').click();page.click('#start');page.wait_for_function("document.querySelector('#status').textContent==='Grabando'");page.wait_for_timeout(400);page.click('#cancel');page.wait_for_function("document.querySelector('#status').textContent==='Listo para grabar'");assert page.locator('#results').is_hidden()
  result={'scope':'Una ejecución corta en Chromium con señales sintéticas; no valida dispositivos, tomas largas ni precisión universal.','signal_seconds':marker,'difference_before_after_seconds':spread,'pause_resume_events_present':True,'files_checked':len(metadata['files']),'screen_only_and_cancel':'ok'}
  (OUT/'resultados.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps(result,ensure_ascii=False,indent=2))
  context.close();browser.close()
finally:server.shutdown();server.server_close()
