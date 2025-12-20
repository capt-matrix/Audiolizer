from AC_encoder import Song
from MIDI_encoder import Audio
from VIDI_encoder import Lizer
import server as m
from assets import WIDTH,HEIGHT
import setup as r
import threading


if not r.check():
     r.setup()

server=threading.Thread(target=m.run)
server.daemon=True
server.start()



runner=True

m.log('def',f'Screen dimensions: {WIDTH}x{HEIGHT}')

while runner:
     command,options=m.get_command()
     config=None
     song=None
     music=None
     visual=None
     
     saver=[0,0,0] #AC,WAV,MP4
     
     if not command:
          continue
     else:
          print(command,options)
          output=options.get('o',None)
          if output:
               saver[0] = 1 if 'c' in output.split('|') else 0
               saver[1] = 1 if 'a' in output.split('|') else 0
               saver[2] = 1 if 'v' in output.split('|') else 0
     if command == 'run':
          config=m.get_config()
          if not config:
               continue
          try:
               song=Song()
               song.write_ACode(saver=saver[0])
               path=song.path
               audio=Audio(song)
               audio.output(saver=saver[1])
               m.put_acode(path+'.AC',song.TPB,song.measure[0])
               visual=Lizer(song)
               visual.run(saver=saver[2])
          except Exception as e:
               m.log('err',str(e))

# S=Song()
# S.write_ACode()
# path=S.path
# A=Audio(S)
# A.output()
# L=Lizer(S)
# L.run()
