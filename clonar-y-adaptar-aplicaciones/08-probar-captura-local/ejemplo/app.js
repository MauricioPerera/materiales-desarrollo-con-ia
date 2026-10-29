(() => {
  'use strict';
  const $ = (id) => document.getElementById(id);
  const ui = Object.fromEntries(['status','status-dot','timer','empty','preview','result','stage-caption','camera','microphone','start','active-controls','pause','stop','cancel','download','new','message','screen-source','camera-source'].map((id) => [id, $(id)]));
  const ctx = ui.preview.getContext('2d', { alpha: false });
  let phase = 'idle', recorder = null, screen = null, camera = null, mic = null, canvasStream = null;
  let chunks = [], outputUrl = null, animation = 0, tick = 0, startedAt = 0, pauseAt = 0, pausedMs = 0, canceled = false, stopMessage = '', recorderFailure = '';
  const show = (element, visible) => element.classList.toggle('hidden', !visible);
  const setMessage = (text, error = false) => { ui.message.textContent = text; ui.message.classList.toggle('error', error); };
  function setPhase(next) {
    phase = next;
    const active = next === 'recording' || next === 'paused';
    const busy = active || next === 'preparing' || next === 'finalizing';
    ui.camera.disabled = busy; ui.microphone.disabled = busy; ui.start.disabled = next === 'preparing' || next === 'finalizing';
    show(ui.start, next === 'idle' || next === 'preparing' || next === 'finalizing');
    show(ui['active-controls'], active); show(ui.cancel, active);
    show(ui.download, next === 'ready'); show(ui.new, next === 'ready');
    show(ui.empty, next === 'idle' || next === 'preparing'); show(ui.preview, active); show(ui.result, next === 'ready');
    ui['status-dot'].classList.toggle('active', active);
    ui.status.textContent = ({idle:'Listo para grabar',preparing:'Solicitando permisos',recording:'Grabando',paused:'En pausa',finalizing:'Preparando el video',ready:'Grabación lista'})[next];
    ui.pause.textContent = next === 'paused' ? 'Reanudar' : 'Pausar';
    ui['stage-caption'].textContent = next === 'ready' ? 'Revisa el video antes de guardarlo.' : 'Tu grabación se guarda únicamente cuando la descargas.';
  }
  function resetClock() { startedAt = performance.now(); pausedMs = 0; pauseAt = 0; updateClock(); clearInterval(tick); tick = setInterval(updateClock, 250); }
  function updateClock() {
    const now = phase === 'paused' ? pauseAt : performance.now();
    const seconds = Math.max(0, Math.floor((now - startedAt - pausedMs) / 1000));
    ui.timer.textContent = String(Math.floor(seconds / 60)).padStart(2, '0') + ':' + String(seconds % 60).padStart(2, '0');
  }
  function cleanup() {
    cancelAnimationFrame(animation); clearInterval(tick);
    for (const stream of [screen, camera, mic, canvasStream]) if (stream) for (const track of stream.getTracks()) track.stop();
    screen = camera = mic = canvasStream = null;
    ui['screen-source'].srcObject = null; ui['camera-source'].srcObject = null;
  }
  function draw() {
    if (!screen || !['preparing','recording','paused'].includes(phase)) return;
    const w = ui.preview.width, h = ui.preview.height, screenVideo = ui['screen-source'];
    ctx.fillStyle = '#102c25'; ctx.fillRect(0, 0, w, h);
    if (screenVideo.readyState >= 2) ctx.drawImage(screenVideo, 0, 0, w, h);
    const cam = ui['camera-source'];
    if (camera && cam.readyState >= 2 && cam.videoWidth && cam.videoHeight) {
      const diameter = Math.max(80, Math.min(w, h) * 0.25), radius = diameter / 2;
      const margin = Math.max(18, Math.min(w, h) * 0.035), cx = w - margin - radius, cy = h - margin - radius;
      const size = Math.min(cam.videoWidth, cam.videoHeight), sx = (cam.videoWidth - size) / 2, sy = (cam.videoHeight - size) / 2;
      ctx.save(); ctx.beginPath(); ctx.arc(cx, cy, radius, 0, 2 * Math.PI); ctx.clip();
      ctx.drawImage(cam, sx, sy, size, size, cx - radius, cy - radius, diameter, diameter); ctx.restore();
      ctx.beginPath(); ctx.arc(cx, cy, radius, 0, 2 * Math.PI); ctx.strokeStyle = '#ffffff'; ctx.lineWidth = Math.max(3, diameter * .025); ctx.stroke();
    }
    animation = requestAnimationFrame(draw);
  }
  function chooseMime(withAudio) {
    const types = withAudio ? ['video/webm;codecs=vp8,opus','video/webm;codecs=vp9,opus','video/webm','video/mp4'] : ['video/webm;codecs=vp8','video/webm;codecs=vp9','video/webm','video/mp4'];
    return types.find((type) => MediaRecorder.isTypeSupported(type)) || '';
  }
  function finish(discard = false, message = '') {
    if (!['recording','paused'].includes(phase)) return;
    updateClock();
    if (phase === 'paused') { pausedMs += performance.now() - pauseAt; }
    canceled = discard; stopMessage = message; setPhase('finalizing'); clearInterval(tick);
    if (recorder && recorder.state !== 'inactive') recorder.stop(); else { cleanup(); setPhase('idle'); setMessage('No se pudo completar la grabación.', true); }
  }
  async function start() {
    if (phase !== 'idle') return;
    if (!navigator.mediaDevices?.getDisplayMedia || typeof MediaRecorder === 'undefined') { setMessage('Este navegador no ofrece las funciones de captura necesarias. Prueba con una versión compatible de Chrome o Edge en localhost.', true); return; }
    canceled = false; recorderFailure = ''; chunks = []; setPhase('preparing'); setMessage('Elige la pantalla o ventana que quieras grabar.');
    try {
      screen = await navigator.mediaDevices.getDisplayMedia({ video: true, audio: false });
      const screenTrack = screen.getVideoTracks()[0];
      if (!screenTrack || screenTrack.readyState !== 'live') throw new Error('La captura de pantalla terminó antes de comenzar.');
      screenTrack.addEventListener('ended', () => { if (['recording','paused'].includes(phase)) finish(false, 'La captura de pantalla terminó. Conservamos el video disponible.'); });
      if (ui.camera.checked) camera = await navigator.mediaDevices.getUserMedia({ video: true, audio: false });
      if (ui.microphone.checked) mic = await navigator.mediaDevices.getUserMedia({ video: false, audio: true });
      if (screenTrack.readyState !== 'live') throw new Error('La captura de pantalla terminó antes de comenzar.');
      ui['screen-source'].srcObject = screen; await ui['screen-source'].play();
      if (camera) { ui['camera-source'].srcObject = camera; await ui['camera-source'].play(); }
      const settings = screenTrack.getSettings();
      ui.preview.width = settings.width || ui['screen-source'].videoWidth || 1280;
      ui.preview.height = settings.height || ui['screen-source'].videoHeight || 720;
      if (!ui.preview.captureStream) throw new Error('Este navegador no permite grabar la composición de pantalla.');
      canvasStream = ui.preview.captureStream(30);
      const combined = new MediaStream([...canvasStream.getVideoTracks(), ...(mic ? mic.getAudioTracks() : [])]);
      const mimeType = chooseMime(Boolean(mic)); recorder = new MediaRecorder(combined, mimeType ? { mimeType } : undefined);
      recorder.addEventListener('dataavailable', (event) => { if (event.data?.size) chunks.push(event.data); });
      recorder.addEventListener('error', () => { recorderFailure = 'El navegador informó un error durante la grabación.'; });
      recorder.addEventListener('stop', () => {
        const type = recorder.mimeType || chunks[0]?.type || 'video/webm';
        const blob = new Blob(chunks, {type}); chunks = []; cleanup();
        if (canceled) { recorder = null; setPhase('idle'); ui.timer.textContent = '00:00'; setMessage('Grabación cancelada. Puedes empezar de nuevo.'); return; }
        if (!blob.size || recorderFailure) { recorder = null; setPhase('idle'); setMessage(recorderFailure || 'No se recibieron datos de video. Inténtalo de nuevo.', true); return; }
        if (outputUrl) URL.revokeObjectURL(outputUrl);
        outputUrl = URL.createObjectURL(blob); ui.result.src = outputUrl; ui.download.href = outputUrl;
        ui.download.download = 'grabacion-local.' + (type.startsWith('video/mp4') ? 'mp4' : 'webm');
        recorder = null; setPhase('ready'); setMessage(stopMessage || 'Tu video está listo para revisar y descargar.');
      }, {once:true});
      draw(); recorder.start(1000); setPhase('recording'); resetClock(); setMessage('Grabando. Puedes pausar, detener o cancelar la toma.');
    } catch (error) {
      cleanup(); recorder = null; setPhase('idle');
      const reason = error?.name === 'NotAllowedError' ? 'No se concedió un permiso o se canceló la selección.' : (error?.message || 'No fue posible iniciar la captura.');
      setMessage(reason + ' Revisa la configuración y vuelve a intentarlo.', true);
    }
  }
  ui.start.addEventListener('click', start);
  ui.pause.addEventListener('click', () => {
    if (!recorder) return;
    if (phase === 'recording' && recorder.state === 'recording') { recorder.pause(); pauseAt = performance.now(); setPhase('paused'); updateClock(); setMessage('Grabación pausada.'); }
    else if (phase === 'paused' && recorder.state === 'paused') { recorder.resume(); pausedMs += performance.now() - pauseAt; setPhase('recording'); setMessage('Grabación reanudada.'); }
  });
  ui.stop.addEventListener('click', () => finish(false));
  ui.cancel.addEventListener('click', () => finish(true));
  ui.new.addEventListener('click', () => { if (outputUrl) URL.revokeObjectURL(outputUrl); outputUrl = null; ui.result.removeAttribute('src'); ui.result.load(); ui.download.removeAttribute('href'); ui.timer.textContent = '00:00'; setPhase('idle'); setMessage('El navegador solicitará permiso solo para los dispositivos que selecciones.'); });
  window.addEventListener('beforeunload', () => { cleanup(); if (outputUrl) URL.revokeObjectURL(outputUrl); });
  setPhase('idle');
})();
