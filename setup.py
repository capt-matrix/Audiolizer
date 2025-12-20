import os
import urllib.request

from assets import ROOT,FONTS,INPUT,DEPS,make,set

def fetch_file(url,dir,dest):
     dest=os.path.join(dir,dest)
     os.makedirs(os.path.dirname(dest),exist_ok=True)
     if not os.path.exists(dest):
          urllib.request.urlretrieve(url,dest)
     

def check():
     check_=os.path.join(ROOT,'check')
     cc=''
     if not os.path.exists(check_):
          return False
     with open(check_) as r:
          cc=r.read()
     if '-.-. .- .--. - .- .. -. ..--.- -- .- - .-. .. -..-' in cc :
          return True
     return False
def assemble_file(path):
    ext=os.path.splitext(path)[1][1:]
    base = os.path.splitext(os.path.basename(path))[0]
    dir=os.path.dirname(path)
    idx = 0
    with open(path, 'wb') as out:
        while True:
            chunk_name = os.path.join(dir,f"R-{ext}.{base}-{idx}")
            if not os.path.exists(chunk_name):
                break
            with open(chunk_name, 'rb') as chunk:
                out.write(chunk.read())
            os.remove(chunk_name)
            idx += 1
def setup():
     make()
    
     deps=[
         ('https://raw.githubusercontent.com/capt-matrix/deps/main/ADLiz/dependencies/ffmpeg.exe',DEPS,'ffmpeg.exe'),
         ('https://raw.githubusercontent.com/capt-matrix/deps/main/ADLiz/dependencies/ffmpeg',DEPS,'ffmpeg'),
         ('https://raw.githubusercontent.com/capt-matrix/deps/main/ADLiz/dependencies/fluidsynth.exe',DEPS,'fluidsynth.exe'),
         ('https://raw.githubusercontent.com/capt-matrix/deps/main/ADLiz/dependencies/fluidsynth',DEPS,'fluidsynth'),
         ('https://raw.githubusercontent.com/capt-matrix/deps/main/ADLiz/dependencies/R-sf2.FluidR3-0',DEPS,'R-sf2.FluidR3-0'),
         ('https://raw.githubusercontent.com/capt-matrix/deps/main/ADLiz/dependencies/R-sf2.FluidR3-1',DEPS,'R-sf2.FluidR3-1'),
         ('https://raw.githubusercontent.com/capt-matrix/deps/main/ADLiz/dependencies/chords.json',DEPS,'chords.json'),

         ('https://raw.githubusercontent.com/capt-matrix/deps/main/ADLiz/Fonts/Arexa.otf',FONTS,'Arexa.otf'),
         ('https://raw.githubusercontent.com/capt-matrix/deps/main/ADLiz/Fonts/Exo.otf',FONTS,'Exo.otf'),
         ('https://raw.githubusercontent.com/capt-matrix/deps/main/ADLiz/Fonts/GConce.otf',FONTS,'GConce.otf'),
         ('https://raw.githubusercontent.com/capt-matrix/deps/main/ADLiz/Fonts/Pastone.otf',FONTS,'Pastone.otf'),
         
         ('https://raw.githubusercontent.com/capt-matrix/deps/main/ADLiz/page/index.html',INPUT,'index.html'),
         ('https://raw.githubusercontent.com/capt-matrix/deps/main/ADLiz/page/style.css',INPUT,'style.css'),
         ('https://raw.githubusercontent.com/capt-matrix/deps/main/ADLiz/page/script.js',INPUT,'script.js'),
    ]
    
     for url,dir,file in deps:
         fetch_file(url,dir,file)
     assemble_file(os.path.join(DEPS,'FluidR3.sf2'))
     with open(os.path.join(ROOT,'check'),'w') as check:
          check.write('Audiolizer dependencies fetched\n-.-. .- .--. - .- .. -. ..--.- -- .- - .-. .. -..-')
     set()
     
    