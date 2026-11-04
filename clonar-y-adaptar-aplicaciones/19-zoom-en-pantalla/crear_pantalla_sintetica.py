"""Crea una pantalla de formas geométricas, sin capturar el escritorio."""
import subprocess,sys
from pathlib import Path
out=Path(sys.argv[1])
if out.exists(): raise FileExistsError('La salida debe ser nueva')
vf='drawbox=x=30:y=30:w=580:h=300:color=0x174d40:t=fill,drawbox=x=45:y=45:w=550:h=270:color=0xe1eee4:t=fill,drawbox=x=180:y=110:w=280:h=140:color=0xc45335:t=fill,drawbox=x=205:y=135:w=100:h=60:color=0xfad67e:t=fill,drawbox=x=335:y=135:w=100:h=60:color=0x68ad8c:t=fill,drawbox=x=205:y=215:w=230:h=20:color=0xffffff:t=fill'
subprocess.run(['ffmpeg','-v','error','-n','-f','lavfi','-i','color=c=0x94c6a9:s=640x360:r=30','-vf',vf,'-frames:v','340','-c:v','libx264','-pix_fmt','yuv420p',str(out)],check=True)
