from AC_encoder import Song
from assets import FS,TPQN,STRINGS,env,readb,save
from server import log
from midiutil import MIDIFile

import os
import subprocess
import random





class Audio():
     def __init__(self,AC:Song):
          self.AC=AC
          
          MIDI=MIDIFile(1,ticks_per_quarternote=TPQN,eventtime_is_ticks=True)
          MIDI.addTrackName(0,0,self.name)
          MIDI.addTempo(0,0,(self.tempo*4)/self.measure[1])
          
          for string in range(6):
               MIDI.addProgramChange(0,string,0,self.instrument)
               
          self.MIDI=MIDI
          log('inf',f'Using SoundFont {os.path.basename(self.soundfont)} with instrument {self.instrument}')
     def __getattr__(self, name):
          return getattr(self.AC,name)
     def parse_ACode2midi(self):
          prev=None
          prev_vol=100
          
          def jitter_vol(volume):
               if self.humanize_velocity>0:
                    volume+=random.randint(-self.humanize_velocity,self.humanize_velocity)
               return max(0,min(127,volume))
          
          def add_pick(timept, frame,dur, volume):
               for ind in range(6):
                    i = frame[ind]
                    pitch = list(STRINGS.values())[ind][1]
                    if i != 'X':
                         pitch += int(i)
                         vol=jitter_vol(volume)
                         self.MIDI.addNote(0, ind, pitch, timept,dur, vol)
          
          def add_strum(timept,frame,func,dur,volume):
               if (6-frame.count('X'))==0:
                    return
               
               delay_factor=self.strum_spread_down if func=='D' else self.strum_spread_up
               delay_factor*=1+random.uniform(-0.2,0.2)
               
               delay_per_string = (delay_factor * dur) / (6-frame.count('X'))
               delay = 0
               
               for ind in range(6):
                    if func=='D':   
                         string_idx = ind
                    elif func == 'U':
                         string_idx = 5 - ind
                    else:
                         string_idx = ind
                         delay_per_string = 0
                    
                    i=frame[string_idx]
                    if i!='X':
                         pitch=list(STRINGS.values())[string_idx][1]+int(i)
                         note=list(STRINGS.keys())[ind]+i
                         timept_= timept + round(delay)
                         vol=jitter_vol(volume)
                         self.MIDI.addNote(0,ind,pitch,timept_,dur,vol,note)    
                         delay+=delay_per_string
                         
          def add_hit(timept,frame,dur,basevol,fader=12):
               if frame is None or dur<=0:
                    return
               fade = max(1, round(dur / fader))
               for step in range(fader):
                    volume = int(basevol*(1.0 - (step / fader) * (1-0.25)))
                    timept_= round(timept + step * fade)
                    for ind in range(6):
                         i = frame[ind]
                         if i != 'X':
                              pitch = list(STRINGS.values())[ind][1] + int(i)
                              self.MIDI.addNote(0, ind, pitch, timept_ , fade , volume)                   
                    
          frames=readb(self.path+'.AC')
               
          ind=0
          i = frames[ind]
          len_=len(frames)
          timept=0
          dur=0
          while True:
               if ind==len_:
                    break
               
               i = frames[ind]
               if not i:
                    continue
               
               frame,func,timept=i
               dur=self.TPB
               if not ind+1==len_:
                    dur = frames[ind+1][2]-timept
               
               if func=='P':
                    add_pick(timept,frame,dur,100)
                    prev=frame
                    prev_vol=100
               elif func=='H':
                    add_hit(timept,prev,dur,prev_vol)
                    prev_vol=int(prev_vol*0.5)
               elif func in ['D','U']:
                    add_strum(timept,frame,func,dur,100)
                    prev=frame
                    prev_vol=100
               ind+=1
     def write_MIDI(self):
          self.parse_ACode2midi()
          log('def','Parsed ACode to MIDI')
          with open(self.path+'.mid','wb') as MID_file:
               self.MIDI.writeFile(MID_file)
          log('pas','MIDI written')
               
     def output(self,saver=0):
          self.write_MIDI()
          try:
               subprocess.run([
                   FS,
                    '-ni',
                    '-q',
                    '-F', self.path+'.wav', 
                    '-r', '44100',          
                    self.soundfont,     
                    self.path+'.mid'    
               ],check=True,env=env)
          except Exception as e:
               print(FS,e)
          
          if saver:
               save(self.path+'.wav')
               log('pas','WAV file written to Downloads/Audiolizer')
         