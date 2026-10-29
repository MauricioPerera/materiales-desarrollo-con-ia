(() => {
  'use strict';
  const $ = id => document.getElementById(id);
  const ui = Object.fromEntries(['camera','microphone','start','pause','stop','cancel','status','message','results','downloads'].map(id=>[id,$(id)]));
  let phase='idle', streams=[], recorders=[], urls=[], events=[], origin=0, discarded=false;
  const stamp=(kind,detail={})=>events.push({kind,ms:Math.round((performance.now()-origin)*1000)/1000,...detail});
  function state(value) {
    phase=value;ui.status.textContent=({idle:'Listo para grabar',preparing:'Preparando',recording:'Grabando',paused:'En pausa',finishing:'Preparando archivos',ready:'Archivos listos'})[value];
    ui.start.disabled=value!=='idle';ui.pause.disabled=!['recording','paused'].includes(value);ui.stop.disabled=ui.cancel.disabled=!['recording','paused'].includes(value);
    ui.camera.disabled=ui.microphone.disabled=value!=='idle';ui.pause.textContent=value==='paused'?'Reanudar':'Pausar';
  }
  function release() {for(const stream of streams)for(const track of stream.getTracks())track.stop();streams=[];}
  function clearDownloads(){for(const url of urls)URL.revokeObjectURL(url);urls=[];ui.downloads.replaceChildren();ui.results.hidden=true;}
  function addDownload(name,blob){const a=document.createElement('a');a.className='download';a.textContent='Descargar '+name;a.download=name;a.href=URL.createObjectURL(blob);urls.push(a.href);ui.downloads.appendChild(a);}
  function format(kind){const choices=kind==='audio'?['audio/webm;codecs=opus','audio/webm','audio/mp4']:['video/webm;codecs=vp8','video/webm;codecs=vp9','video/webm','video/mp4'];return choices.find(MediaRecorder.isTypeSupported.bind(MediaRecorder))||'';}
  function makeRecorder(name,stream,kind){
    const mime=format(kind), recorder=new MediaRecorder(stream,mime?{mimeType:mime}:undefined), chunks=[];
    const result=new Promise((resolve,reject)=>{
      recorder.addEventListener('dataavailable',e=>{if(e.data?.size)chunks.push(e.data)});
      recorder.addEventListener('error',e=>reject(e.error||new Error('Error del grabador '+name)),{once:true});
      recorder.addEventListener('start',()=>stamp('start-event',{track:name}));
      recorder.addEventListener('stop',()=>{const type=recorder.mimeType||chunks[0]?.type||'application/octet-stream';resolve({name,type,blob:new Blob(chunks,{type})});},{once:true});
    });
    return {name,recorder,result};
  }
  async function start(){
    if(phase!=='idle')return;
    if(!navigator.mediaDevices?.getDisplayMedia||!window.MediaRecorder){ui.message.textContent='Este navegador no ofrece las funciones necesarias.';return;}
    clearDownloads();state('preparing');discarded=false;recorders=[];events=[];origin=performance.now();
    try{
      const screen=await navigator.mediaDevices.getDisplayMedia({video:true,audio:false});streams.push(screen);
      const camera=ui.camera.checked?await navigator.mediaDevices.getUserMedia({video:true,audio:false}):null;if(camera)streams.push(camera);
      const mic=ui.microphone.checked?await navigator.mediaDevices.getUserMedia({video:false,audio:true}):null;if(mic)streams.push(mic);
      const screenTrack=screen.getVideoTracks()[0];if(!screenTrack||screenTrack.readyState!=='live')throw new Error('La captura de pantalla no está disponible.');
      screenTrack.addEventListener('ended',()=>{if(['recording','paused'].includes(phase))finish(false,'La captura de pantalla terminó. Revisa los archivos disponibles.');},{once:true});
      recorders=[makeRecorder('pantalla',screen,'video'),...(camera?[makeRecorder('camara',camera,'video')]:[]),...(mic?[makeRecorder('microfono',mic,'audio')]:[])];
      for(const item of recorders){stamp('start-request',{track:item.name});item.recorder.start(1000)}
      state('recording');ui.message.textContent='Grabando pistas independientes.';
    }catch(error){
      for(const item of recorders)if(item.recorder.state!=='inactive')item.recorder.stop();release();recorders=[];state('idle');
      ui.message.textContent=(error.name==='NotAllowedError'?'Se canceló la selección o se rechazó un permiso.':error.message)+' Puedes volver a intentarlo.';
    }
  }
  async function finish(cancel=false,message=''){
    if(!['recording','paused'].includes(phase))return;
    discarded=cancel;state('finishing');stamp(cancel?'cancel-request':'stop-request');
    try{
      for(const item of recorders)if(item.recorder.state!=='inactive'){stamp('track-stop-request',{track:item.name});item.recorder.stop()}
      const done=await Promise.all(recorders.map(item=>item.result));release();recorders=[];
      if(discarded){state('idle');ui.message.textContent='Toma cancelada.';return;}
      const files=[];for(const item of done){if(!item.blob.size)throw new Error('Una pista no produjo datos.');const ext=item.type.startsWith('audio/mp4')?'m4a':item.type.startsWith('video/mp4')?'mp4':'webm';const name=item.name+'.'+ext;files.push({track:item.name,file:name,mime:item.type,bytes:item.blob.size});addDownload(name,item.blob)}
      const metadata={version:1,clock:'performance.now',description:'Tiempos de eventos medidos en la aplicación; no son marcas de tiempo verificadas del contenido.',events,files};
      addDownload('metadatos.json',new Blob([JSON.stringify(metadata,null,2)],{type:'application/json'}));ui.results.hidden=false;state('ready');ui.message.textContent=message||'Descarga y revisa cada pista.';
      const again=document.createElement('button');again.textContent='Nueva toma';again.addEventListener('click',()=>{clearDownloads();state('idle');ui.message.textContent='Selecciona los dispositivos que deseas usar.'});ui.downloads.appendChild(again);
    }catch(error){release();clearDownloads();recorders=[];state('idle');ui.message.textContent='No se pudo completar la toma: '+error.message;}
  }
  ui.start.addEventListener('click',start);
  ui.pause.addEventListener('click',()=>{try{if(phase==='recording'){stamp('pause-request');for(const x of recorders)x.recorder.pause();state('paused');ui.message.textContent='Pausa solicitada a todas las pistas.'}else if(phase==='paused'){stamp('resume-request');for(const x of recorders)x.recorder.resume();state('recording');ui.message.textContent='Reanudación solicitada a todas las pistas.'}}catch(error){ui.message.textContent='No se pudo cambiar el estado: '+error.message;finish(false)}});
  ui.stop.addEventListener('click',()=>finish());ui.cancel.addEventListener('click',()=>finish(true));
  window.addEventListener('beforeunload',()=>{release();clearDownloads()});state('idle');
})();
