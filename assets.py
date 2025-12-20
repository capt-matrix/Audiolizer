import platform
from platformdirs import user_downloads_dir,user_data_dir
import os
import shutil
import ctypes
import subprocess

Appname='Audiolizer'
Author='captain_matrix'
ROOT=user_data_dir(appname=Appname,appauthor=Author)
SAVE=os.path.join(user_downloads_dir(),Appname)
def make():
     os.makedirs(ROOT,exist_ok=True)
     os.makedirs(SAVE,exist_ok=True)

def set():
     if platform.system()=='Darwin':
          os.chmod(os.path.join(DEPS,'fluidsynth'),0o755)
          os.chmod(os.path.join(DEPS,'ffmpeg'),0o755)

aspect=[16,9]
WIDTH,HEIGHT=(1440,810)

def _scaleWH(w,h):
     w_,h_=w,h
     if h==min(w,h):
          w_=round((aspect[0]/aspect[1])*h)
     else:
          h_=round((aspect[1]/aspect[0])*w)
     return [w_,h_]
     

if platform.system()=='Darwin':
    result=subprocess.run(['system_profiler','SPDisplaysDataType'],capture_output=True,text=True)
    width=WIDTH
    height=HEIGHT
    for line in result.stdout.splitlines():
        if "Resolution" in line:
            parts = line.strip().split()
            # Example: "Resolution: 2560 x 1600 Retina"
            if len(parts) >= 4 and parts[1] == ":":
                try:
                    width = int(parts[2])
                    height = int(parts[4])
                except Exception:
                    pass
            elif len(parts) >= 3:
                try:
                    width = int(parts[1])
                    height = int(parts[3])
                except Exception:
                    pass
            break
    WIDTH=min(width,WIDTH)
    HEIGHT=min(height,HEIGHT)
    WIDTH,HEIGHT=_scaleWH(WIDTH,HEIGHT)
elif platform.system()=='Windows':
    user32=ctypes.windll.user32
    width=user32.GetSystemMetrics(0)
    height=user32.GetSystemMetrics(1)
    WIDTH=min(width,WIDTH)
    HEIGHT=min(height,HEIGHT)
    WIDTH,HEIGHT=_scaleWH(WIDTH,HEIGHT)


INPUT=os.path.join(ROOT,'page')
FONTS=os.path.join(ROOT,'Fonts')
DEPS=os.path.join(ROOT,'dependencies')

CONFIG=os.path.join(ROOT,'config.txt')
SF=os.path.join(ROOT,'dependencies','FluidR3.sf2')
CHORDS=os.path.join(ROOT,'dependencies','chords.json')

if platform.system()=='Windows':
    FS=os.path.join(DEPS,'fluidsynth.exe')
    FM=os.path.join(DEPS,'ffmpeg.exe')
else:
    FS=os.path.join(DEPS,'fluidsynth')
    FM=os.path.join(DEPS,'ffmpeg')
    
env=os.environ.copy()
env['PATH']=env.get('PATH','')+os.pathsep+FS

FPS=60
TPQN=480
PORT=8000

HEX={
     'frets':{
          '0':0x0,
          '1':0x1,
          '2':0x2,
          '3':0x3,
          '4':0x4,
          '5':0x5,
          '6':0x6,
          '7':0x7,
          '8':0x8,
          '9':0x9,
          '10':0xa,
          '11':0xb,
          '12':0xc,
          'X':0xf,
     },
     'funcs':{
          'S':0x0,
          'P':0x1,
          'D':0x2,
          'U':0x3,
          'H':0x4,
     },
     'seps':{
          'del':0xee,
     }
}
HEX_={
     'frets':{
         0x0:'0',
         0x1:'1',
         0x2:'2',
         0x3:'3',
         0x4:'4',
         0x5:'5',
         0x6:'6',
         0x7:'7',
         0x8:'8',
         0x9:'9',
         0xa:'10',
         0xb:'11',
         0xc:'12',
         0xf:'X',
     },
     'funcs':{
          0x0:'S',
          0x1:'P',
          0x2:'D',
          0x3:'U',
          0x4:'H',
     },
     'seps':{
          0xee:'del',
     }
}
STRINGS={
     'E':[0,40],
     'A':[1,45],
     'D':[2,50],
     'G':[3,55],
     'B':[4,59],
     'e':[5,64],
}

def readb(path):
     with open(path, 'rb') as f:
          data = f.read()
     lines=[]
     i = 0
     while i < len(data):
          
          frame = [data[i+j] for j in range(6)]
          t=[HEX_['frets'][frame[j]] for j in range(6)]
          frame=t
          i += 6
          
          if data[i] != HEX['seps']['del']:
          #   print("Frame separator missing!")
               break
          i += 1
          func = data[i]
          t=func
          func=HEX_['funcs'][t]
          i += 1
          if data[i] != HEX['seps']['del']:
          #   print("Func separator missing!")
               break
          i += 1
          tlen=data[i]
          i+=1
          
          timept=int.from_bytes(data[i:i+tlen],'big')
          i += tlen
          lines.append([frame,func,timept])
     return lines

def save(path):
     file=os.path.basename(path)
     dest=os.path.join(SAVE,file)
     shutil.copy(path,dest)
