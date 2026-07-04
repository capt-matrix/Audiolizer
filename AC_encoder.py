import re
import json
import os
import random
from assets import ROOT,CONFIG,CHORDS,TPQN,HEX,STRINGS,SF,save
from server import log
# X-3-2-0-1-0.F ; this is an acode line [frame]. the 6 numbers separated by - represents states of 6 strings [E-e] at that frame, and F is function going on at that frame
# kinds of F: 
# D=down strum, U=up strum, H=slap all strings, P=pluck one string, S=rest (leave everything as it is) 


def clean(content:str|list,chars=''):
     if isinstance(content,list):
          result=[]
          for i in range(len(content)):
               content[i]=content[i].strip()
               content[i]=content[i].strip(chars)
               content[i]=content[i].strip()
               if not content[i]:
                    continue
               result.append(content[i])
          return result
     return content.strip().strip(chars).strip()


          
class Song:
     def __init__(self):
          self.name="My_song"
          self.path=ROOT
          
          self.u_chords=[]
          self.picks=[]
          self.strums=[]
          self.progressions=[]
          
          self.capo_fret=0
          self.tempo=120
          self.instrument=24
          self.measure=[4,4]
          
          self.soundfont=SF
          self.song=[]
          
          self.humanize_timing=0.0
          self.humanize_velocity=0
          self.strum_spread_down=0.12
          self.strum_spread_up=0.10
          
          self.chords={}
          self.sequence={
               'Chords':{},
               'Strums':{},
               'Picks':{},
          }
          
          self.TPB=0
          self.TPBr=0
          self.TPS=0
          
          
          self.read_config()
          self.path=os.path.join(ROOT,self.name)
          
     def _getChord(self,chordlib,fingering):
          for name,frets in chordlib.items():
               if frets == fingering:
                    return name
          return None
     def parse_song(self, song):
          def tokenize(s):
               tokens = []
               i = 0
               while i < len(s):
                    if s[i] in '()+*x':
                         tokens.append(s[i])
                         i += 1
                    elif s[i].isspace():
                         i += 1
                    else:
                         j = i
                         while j < len(s) and s[j] not in '()+*x' and not s[j].isspace():
                              j += 1
                         tokens.append(s[i:j])
                         i = j
               return tokens

          def parse(tokens):
               stack = [[]]
               i = 0
               while i < len(tokens):
                    token = tokens[i]
                    if token == '(':
                         stack.append([])
                         i += 1
                    elif token == ')':
                         group = stack.pop()
                         stack[-1].append(group)
                         i += 1
                    elif token == '+':
                         i += 1
                    elif token == '*':
                         count = int(tokens[i+1])
                         group = stack[-1].pop()
                         expanded = []
                         for _ in range(count):
                              expanded.extend(group if isinstance(group, list) else [group])
                         stack[-1].extend(expanded)
                         i += 2
                    elif token == 'x':
                         # Cross product: pop last item, next token should be a group or item
                         left = stack[-1].pop()
                         i += 1
                         
                         # Get right operand
                         if i < len(tokens) and tokens[i] == '(':
                              # Parse the group
                              depth = 1
                              j = i + 1
                              while j < len(tokens) and depth > 0:
                                   if tokens[j] == '(':
                                        depth += 1
                                   elif tokens[j] == ')':
                                        depth -= 1
                                   j += 1
                              # Recursively parse this subexpression
                              sub_tokens = tokens[i:j]
                              right = parse(sub_tokens)[0]
                              i = j
                         else:
                              # Single token
                              right = tokens[i]
                              i += 1
                         
                         # Perform cross product
                         left_list = left if isinstance(left, list) else [left]
                         right_list = right if isinstance(right, list) else [right]
                         
                         result = []
                         for l in left_list:
                              for r in right_list:
                                   result.append(f"{l}x{r}")
                         
                         stack[-1].extend(result)
                    else:
                         stack[-1].append(token)
                         i += 1
               return stack[0]

          def flatten(lst):
               result = []
               for item in lst:
                    if isinstance(item, list):
                         result.extend(flatten(item))
                    else:
                         result.append(item)
               return result
          
          tokens = tokenize(song)
          parsed = parse(tokens)
          return flatten(parsed)
     def read_config(self,content=None):
          config=[]
          if not content:
               with open(CONFIG,'r') as song_file:
                    config=song_file.readlines()
          else:
               config=content.splitlines()
          
          for line in config:
               I=None
               I=re.split(r';+',line)[0]
               I=re.split(r'::',I)
               I=clean(I)
               
               if len(I)<=1:
                    continue
               
               if I[0] == 'FILE_NAME':
                    self.name=clean(I[1])
                    log('def',f"FILE_NAME rcvd {self.name}")
               elif I[0] == 'CUSTOM_CHORDS':
                    self.u_chords=clean(I[1].split(','))
               elif I[0] == 'PICK_PATTERN':
                    self.picks=clean(I[1].split(','))
               elif I[0] == 'STRUM_PATTERN':
                    self.strums=clean(I[1].split(','))
               elif I[0] == 'CHORD_PATTERN':
                    self.progressions=clean(I[1].split(','))
                    
                    for i,pattern in enumerate(self.progressions):
                         pattern=pattern.split('>>')
                         pattern=clean(pattern)
                         with open(CHORDS,'r') as chord_lib:
                              chord_lib= json.load(chord_lib)
                         for ind,chord in enumerate(pattern):
                              chord=clean(chord)
                              if 'U' in chord:
                                   u_chords=self.u_chords
                                   u_chords=clean(u_chords)
                                   u_chord =u_chords[int(chord.replace('U',''))-1].split('.')
                                   if  self._getChord(chord_lib,u_chord):
                                        chord =  self._getChord(chord_lib,u_chord)
                                        log('wrn',f"Chord {u_chord} is {chord} .. using {chord} instead of {u_chord}")
                                        pattern[ind]=chord
                                   else:
                                        self.chords[chord]=u_chord
                              if not chord in self.chords.keys():
                                   self.chords[chord]=chord_lib[chord]
                         self.progressions[i]='>>'.join(pattern)
                                
               elif I[0] == 'CAPO':
                    self.capo_fret=int(I[1])
               elif I[0] == 'TEMPO':
                    self.tempo=int(I[1])
                    log('inf',f"Tempo set to {self.tempo}")
               elif I[0] == 'MEASURE':
                    self.measure=(int(I[1].split('/')[0]),int(I[1].split('/')[1]))
               elif I[0] == 'INSTRUMENT':
                    self.instrument=int(I[1])
               elif I[0] == 'SF':
                    self.soundfont=clean(I[1])
               elif I[0] == 'HUMANIZE':
                    parts=I[1].split(',')
                    for part in parts:
                         kv=part.split(':')
                         k=clean(kv[0])
                         if k=='timing':
                              self.humanize_timing=float(clean(kv[1]))
                         elif k=='velocity':
                              self.humanize_velocity=int(clean(kv[1]))
               elif I[0] == 'STRUM_SPREAD':
                    parts=I[1].split(',')
                    for part in parts:
                         kv=part.split(':')
                         k=clean(kv[0])
                         if k=='down':
                              self.strum_spread_down=float(clean(kv[1]))
                         elif k=='up':
                              self.strum_spread_up=float(clean(kv[1]))
               elif I[0] == 'SONG':
                    I[1]=clean(I[1],'|#')
                    for segment in self.parse_song(I[1]):
                         segment=clean(segment,'+*')
                         self.song.append(segment)
          self.TPB =( TPQN * 4 )/ self.measure[1]  
          self.TPS= (self.TPB * self.tempo)/60
          self.TPBr = self.TPB * self.measure[0]     
          log('inf',f"Params. TPS:{self.TPS}, TPB:{self.TPB}")
     # def process_durs   
     def write_ACode(self,saver=0):
          def to_bytes(n):
               if n==0:
                    return b'\x00'
               b=bytearray()
               while n:
                    b.insert(0,n & 0xff)
                    n>>=8
               return b
          def writeb(frame,func,timept):
               b=bytearray()
               for i in frame:
                    b.append(HEX['frets'][i])
               b.append(HEX['seps']['del'])
               b.append(HEX['funcs'][func])
               b.append(HEX['seps']['del'])
               tbyt=to_bytes(timept)
               b.append(len(tbyt))
               b.extend(tbyt)
               AC_file.write(b)
               
          def next(frame,func,dur,default=(('X','X','X','X','X','X'),'S')): # dur in beat fractions
               nonlocal line
               nonlocal timept
               
               func = default[1] if func=='F' else func
               
               for ind in range(len(default[0])):
                    i=frame[ind]
                    if i.isdigit() or i=='X':
                         continue
                    else:
                         frame[ind]=default[0][ind]
                         
               writeb(frame,func,timept)
               line+=1
               if self.humanize_timing>0:
                    dur*=1+random.uniform(-self.humanize_timing,self.humanize_timing)
               timept+=round(float(dur)*self.TPB)
               return ['E','A','D','G','B','e'],'F'
          
          def apply_capo(chord:str|list):
               result=chord
               if isinstance(result,list):
                    result=[]
                    for ind in range(6):
                         i = chord[ind]
                         if i.isdigit():
                              i = str(int(i)+self.capo_fret)
                         result.append(i)
               else:
                    if result.isdigit():
                         result = str(int(result)+self.capo_fret)
               return result
          
          def get_durb(line:str):
               if not '|' in line:
                    return 1
               dur=clean(line.split('|')[0])
               try:
                    dur=float(dur)
               except:
                    dur=1
               return dur
          
          def process_strum(strumseq, barlen):
               if strumseq.count(' ')+1 == barlen:
                    return strumseq.split(' ')
               strumseq=strumseq.replace(' ','')
               n = len(strumseq)
               
               result = []
               current_idx = 0
               
               for i in range(barlen):
                    start = int(round(i * n / barlen))
                    end = int(round((i + 1) * n / barlen))
                    
                    chunk = strumseq[current_idx : current_idx + (end - start)]
                    result.append(chunk)
                    current_idx += len(chunk)
                    
               return result
                                   
          with open(self.path+'.AC','wb') as AC_file:
               line=0
               timept=0
               frame=['0','0','0','0','0','0']
               for segment in self.song:
                    frame=['E','A','D','G','B','e']
                    func='F'
                    segment=clean(segment)
                    dur=0
                    
                    if 'p' in segment.lower():
                         
                         pick_sequence=self.picks[int(segment.replace('P',''))-1]
                         pick_sequence=clean(pick_sequence)
                         
                         dur=get_durb(pick_sequence)
                         
                         pick_sequence=pick_sequence.split('|')[1]
                         pick_sequence=pick_sequence.replace('-','.S0.')
                         if not line in self.sequence['Picks'].keys():
                              self.sequence['Picks'][line]=[dur*self.TPB,pick_sequence]
                         pick_sequence=pick_sequence.split('.')
                         pick_sequence=clean(pick_sequence,'.')

                         for pick in pick_sequence:
                              parts= re.findall(r'[a-zA-Z]+|\d+', pick)
                              if parts[0]=='S':
                                   frame=['0','0','0','0','0','0']
                                   func='S'
                              else:
                                   parts[1]=apply_capo(parts[1])
                                   frame[STRINGS[parts[0]][0]]=parts[1]
                                   func='P'
                              frame,func=next(frame,func,dur)
                              
                    elif 'x' in segment.lower():
                         strum,chord=segment.split('x')
                         strum_sequence=self.strums[int(strum.replace('S',''))-1]
                         strum_sequence=clean(strum_sequence).replace('-','S')
                         
                         dur=get_durb(strum_sequence)
                         
                         strum_sequence=strum_sequence.split('|')[1]
                         
                         strum_sequence=process_strum(strum_sequence,self.measure[0])
                         
                         strum_sequence=clean(strum_sequence)
                         
                         if not line in self.sequence['Strums'].keys():
                              try:
                                   if not [dur*self.TPB,strum_sequence] == self.sequence['Strums'][len(self.sequence['Strums'].keys())-1]:
                                        self.sequence['Strums'][line]=[dur*self.TPB,strum_sequence]
                              except KeyError:
                                   self.sequence['Strums'][line]=[dur*self.TPB,strum_sequence]
                         
                         chord_sequence=self.progressions[int(chord.replace('C',''))-1]
                         chord_sequence=clean(chord_sequence)
                         chord_sequence=chord_sequence.split('>>')
                         chord_sequence=clean(chord_sequence,'>>')
                         if not line in self.sequence['Chords'].keys():
                              dur_=dur*self.TPB*len(chord_sequence)
                              try:
                                   if not [dur_,chord_sequence] == self.sequence['Chords'][len(self.sequence['Chords'].keys())-1]:
                                        self.sequence['Chords'][line]=[dur_,chord_sequence]
                              except KeyError:
                                   self.sequence['Chords'][line]=[dur_,chord_sequence]
                         
                         for chord in chord_sequence:
                              chord=self.chords.get(chord)
                              chord_=apply_capo(chord)
                              for strum in strum_sequence:
                                   len_=len(strum)
                                   frame=chord_
                                   if len_>1:
                                        for i in strum:
                                             func=i
                                             next(frame,func,dur/len_)
                                        continue
                                   func=strum
                                   next(frame,func,dur)
               
               log('pas',f"ACode written duration: {round(timept/self.TPB,2)} beats, {round(timept/self.TPBr,2)} bars, {round(timept/self.TPS,2)} s, {line} frames")
               next(frame,'S',1)
               next(frame,'S',1)
               next(frame,'S',1)
               
               if saver:
                    save(self.path+'.AC')
                    log('pas',f"AC saved as {self.name}.AC in Downloads")
               
               


