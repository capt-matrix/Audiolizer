from AC_encoder import Song
from assets import FM,HEIGHT,WIDTH,FONTS,FPS,readb,env,save
from server import log
import pygame
import math
import re
import subprocess
import cv2
import os
import numpy as np



Colors={
    'BackGround':'#919191',
    'Capo':"#5D5E63",
    'Port':"#A6A3A3",
    'Text':'#000000',
    'Primary':"#5E17EB",
    'Arrow':"#7D62B3",
    'Hit':"#C1584D",
    
    'Body':"#B7B48B",
    'Title':'#7A857A',
    'LabelRect':"#8C9F8C",
    'Fret':"#E0E4D2",
    'Hole':"#C1C3BA",
    
}
Fonts=['Arexa.70','Exo.20','GConce.65','Pastone.40']




class Lizer():
    def __init__(self,AC:Song):
        self.AC=AC
        self.frames=[]
        
        self.controls=[100]
        
        self.bar_width=round((5/16)*WIDTH) - 4
        self.PDot_start=(WIDTH//2) - round((5/32)*WIDTH) + 2
        
        self.structure={
            'ScaleLength':2000,
            'StringLength':WIDTH-25,
            'StringThickness':4,
            'StringOfft':30,
            
            'TitleBar':['rect',
                        [0,0,WIDTH,round(HEIGHT*0.15)],
                        Colors['Title'],
                        0,
                        [-1,-1,15,15]],
            'Author':['Made with love by captain_matrix',
                      ['mr',round(WIDTH*0.995),round(HEIGHT*0.075)],
                      Fonts[1],
                      (Colors['Text'],None)],
            'Title':['Audiolizer I',
                     ['c',WIDTH//2,round(HEIGHT*0.075)],
                     Fonts[0],
                     (Colors['Text'],None)],
            'LabelRect':['rect',
                         [WIDTH*0.015,HEIGHT*0.020,170,90],
                         Colors['LabelRect'],
                         0,
                         [2,2,2,2]],
            'Label1':[f'Volume: {self.controls[0]}',
                      ['ml',WIDTH*0.015+10,HEIGHT*0.020+20],
                      Fonts[1],
                      (Colors['Text'],None)],
            'Label2':[f'Tempo: {self.tempo} bpm',
                      ['ml',WIDTH*0.015+10,HEIGHT*0.020+45],
                      Fonts[1],
                      (Colors['Text'],None)],
            'Label3':[f'Measure: {self.measure[0]}/{self.measure[1]}',
                      ['ml',WIDTH*0.015+10,HEIGHT*0.020+70],
                      Fonts[1],
                      (Colors['Text'],None)],
            
            'ViewPortL':['rect',
                         [(WIDTH//2)-round((5/18)*WIDTH)-round(HEIGHT*0.25),round(WIDTH*0.1),round((5/18)*WIDTH),round(HEIGHT*0.1)],
                         Colors['Port'],
                         0,
                         [5,5,5,5]],
            'ViewPortR':['rect',
                         [(WIDTH//2)+round((5/18)*WIDTH)-round(HEIGHT*0.25),round(WIDTH*0.1),round((5/18)*WIDTH),round(HEIGHT*0.1)],
                         Colors['Port'],
                         0,
                         [5,5,5,5]],
            'ChordP':['Chords',
                      ['ml',(WIDTH//2)+round((5/18)*WIDTH)-round(HEIGHT*0.25)+10,round(WIDTH*0.1)+round(HEIGHT*0.05)],
                      Fonts[3],
                      (Colors['Text'],None)],
            'StrumP':['Strums',
                      ['ml',(WIDTH//2)-round((5/18)*WIDTH)-round(HEIGHT*0.25)+10,round(WIDTH*0.1)+round(HEIGHT*0.05)],
                      Fonts[3],
                      (Colors['Text'],None)],
            
            'Name':[f'{self.name}.AC',
                    ['c',(WIDTH//2),round(WIDTH*0.1)+round(HEIGHT*0.1)-20],
                    Fonts[2],
                    (Colors['Fret'],None)],
            
            'ProgressBarBase':['rect',
                               [(WIDTH//2)-round((5/32)*WIDTH),round(0.295*HEIGHT),round((5/16)*WIDTH),10],
                               Colors['Hole'],
                               0,
                               [2,2,2,2]],
            'ProgressBar':['rect',
                           [(WIDTH//2)-round((5/32)*WIDTH)+1,round(0.295*HEIGHT)+1,self.bar_width,10-2],
                           Colors['Primary'],
                           0,
                           [2,2,2,2]],
            'ProgressDot':['circ',
                           [self.PDot_start,round(0.295*HEIGHT)+5,8],
                           Colors['Primary'],
                           0],
            'Time':['00:00||00:00',
                    ['c',(WIDTH//2),round(WIDTH*0.1)+round(HEIGHT*0.1)+40],
                    Fonts[1],
                    (Colors['Text'],None)],
            
            'Body':['rect',
                    [5,round(0.45*HEIGHT),WIDTH-10,round(0.45*HEIGHT)],
                    Colors['Body'],
                    0,
                    [50,5,50,5]],
            'SoundHole':['circ',
                         [round(0.08*HEIGHT),round(0.675*HEIGHT),round(0.225*HEIGHT)-5],
                         Colors['Hole'],
                         0],
        }
        self.fonts={}
        
        self.frets={
            0:['rect',
               [WIDTH-25,self.structure['Body'][1][1]-3,20,self.structure['Body'][1][3]+6],
               Colors['Fret'],
               0,
               [2,2,2,2]],
        }
        self.stringsp=[[self.structure['Body'][1][1]+30,4]]
        self.fretsp=[[self.frets[0][1][0],self.frets[0][1][2]]]
        self.strings={
            
        }
        self.dots={
            
        }
        self.vidi_dur=0.0
        
        self.recording=False
        self.recorder=None

        pygame.init()
        self.screen=pygame.display.set_mode((WIDTH,HEIGHT),vsync=1)
        for i in Fonts:
            try:
                self.fonts[i]=pygame.font.Font(os.path.join(FONTS,i.split('.')[0]+'.otf'),int(i.split('.')[1]))
            except:
                self.fonts[i]=pygame.font.Font(size=int(i.split('.')[1]))
    
        for i in range(1,13):
           self.fretsp.append([
               self.fretsp[0][0] - int(self.structure['ScaleLength'] - (1*(self.structure['ScaleLength']/2**(i/12)))),
               16-i if i<10 else 5])
        for i in range(13):
            self.frets[i]=['rect',
                           [self.fretsp[i][0],self.frets[0][1][1],self.fretsp[i][1],self.frets[0][1][3]],
                           Colors['Fret'],
                           0,
                           [2,2,2,2]]
        self.capo=[-1,self.frets[0][1][1]-10,round(2.4*self.fretsp[0][1]),self.frets[0][1][3]+20]
        for i in range(1,6):
            self.stringsp.append([
                min(self.structure['Body'][1][1]+self.structure['Body'][1][3],self.stringsp[0][0]+i*round(self.structure['Body'][1][1]/6)),
                max(2, self.stringsp[0][1] - round(i * 0.4))
            ])
        for i in range(6):
            self.strings[5-i]=String(self.screen,5-i,[2,self.structure['StringLength']],frequency=min(64*round((i+1)/3),50),stringsp=self.stringsp,fretsp=self.fretsp)
            self.dots[5-i]=Dot(self.screen,5-i,fretsp=self.fretsp,stringsp=self.stringsp)
        self.arrow=Arrow(self.screen,[
            self.structure['SoundHole'][1][0]-self.structure['SoundHole'][1][2]//2,  
            round(0.45*HEIGHT-30),                  
            round(0.45*HEIGHT),                 
            round(0.45*HEIGHT+60),              
        ])
        self.parse_ACode2vidi()
        log('def','Parsed ACode to VIDI')
        pygame.display.set_caption("Audiolizer","ADLiz")
    def __getattr__(self, name):
          return getattr(self.AC,name)
    def setup(self):
        self._renderShape('TitleBar')
        self._renderText('Author')
        self._renderText('Title')
        self._renderShape('LabelRect')
        self._renderText('Label1')
        self._renderText('Label2')
        self._renderText('Label3')
        self._renderShape('ViewPortL')
        self._renderShape('ViewPortR')
        self._renderText('ChordP')
        self._renderText('StrumP')
        self._renderText('Name')
        self._renderShape('ProgressBarBase')
        self._renderShape('ProgressBar')
        self._renderShape('ProgressDot')
        self._renderText('Time')
        self._renderShape('Body')
        self._renderShape('SoundHole')
        self._renderFrets()
        for i in range(6):
            self.strings[5-i].draw()
            self.dots[5-i].draw()
        self._applyCapo()
        self.arrow.draw()
    def _renderShape(self,compoenent,surface=None):
        if not surface:
            surface=self.screen
        if self.structure[compoenent][0]=='rect':
            pygame.draw.rect(surface,self.structure[compoenent][2],self.structure[compoenent][1],self.structure[compoenent][3],border_top_left_radius=self.structure[compoenent][4][0],border_top_right_radius=self.structure[compoenent][4][1],border_bottom_left_radius=self.structure[compoenent][4][2],border_bottom_right_radius=self.structure[compoenent][4][3])
        elif self.structure[compoenent][0]=='circ':
            pygame.draw.circle(surface,self.structure[compoenent][2],(self.structure[compoenent][1][0],self.structure[compoenent][1][1]),self.structure[compoenent][1][2],self.structure[compoenent][3])
    def _renderFrets(self,surface=None):
        if not surface:
            surface=self.screen
        for i in range(13):
            pygame.draw.rect(surface,self.frets[i][2],self.frets[i][1],self.frets[i][3],border_top_left_radius=self.frets[i][4][0],border_top_right_radius=self.frets[i][4][1],border_bottom_left_radius=self.frets[i][4][2],border_bottom_right_radius=self.frets[i][4][3])
    def _applyCapo(self):
        if self.capo_fret>12 or self.capo_fret<1:
            return
        x=self.fretsp[self.capo_fret][0]+int((self.fretsp[self.capo_fret-1][0]-self.fretsp[self.capo_fret][0]+self.fretsp[self.capo_fret][1])//2)
        self.capo[0]=x-round(2.4*self.fretsp[0][1])//2
        pygame.draw.rect(self.screen,Colors['Capo'],self.capo,0,2)
    def _renderText(self,compoenent,surface=None):
        if not surface:
            surface=self.screen
        surf=self.fonts[self.structure[compoenent][2]].render(self.structure[compoenent][0],True,self.structure[compoenent][3][0],self.structure[compoenent][3][1])
        rect=surf.get_rect()
        if self.structure[compoenent][1][0]=='tl':
            rect.topleft=(self.structure[compoenent][1][1],self.structure[compoenent][1][2])
        elif self.structure[compoenent][1][0]=='tm':
            rect.midtop=(self.structure[compoenent][1][1],self.structure[compoenent][1][2])
        elif self.structure[compoenent][1][0]=='tr':
            rect.topright=(self.structure[compoenent][1][1],self.structure[compoenent][1][2])
        elif self.structure[compoenent][1][0]=='ml':
            rect.midleft=(self.structure[compoenent][1][1],self.structure[compoenent][1][2])
        elif self.structure[compoenent][1][0]=='c':
            rect.center=(self.structure[compoenent][1][1],self.structure[compoenent][1][2])
        elif self.structure[compoenent][1][0]=='mr':
            rect.midright=(self.structure[compoenent][1][1],self.structure[compoenent][1][2])
        elif self.structure[compoenent][1][0]=='bl':
            rect.bottomleft=(self.structure[compoenent][1][1],self.structure[compoenent][1][2])
        elif self.structure[compoenent][1][0]=='bm':
            rect.midbottom=(self.structure[compoenent][1][1],self.structure[compoenent][1][2])
        elif self.structure[compoenent][1][0]=='br':
            rect.bottomright=(self.structure[compoenent][1][1],self.structure[compoenent][1][2])
        if re.findall(r'Label\d+',compoenent):
            self.structure['LabelRect'][1][2]=max(self.structure['LabelRect'][1][2],surf.get_width()+20)
        surface.blit(surf,rect)
    def _record(self):
        log('inf','Recording started ...')
        self.recording=True
        fourcc=cv2.VideoWriter_fourcc(*'mp4v')
        self.recorder=cv2.VideoWriter(f'{self.path}-t.mp4',fourcc,FPS,(WIDTH,HEIGHT))
    def _stop(self):
        if not self.recording:
            return
        self.recording=False
        if self.recorder:
            self.recorder.release()
        subprocess.run([
            FM, '-y',
            '-i', f'{self.path}-t.mp4',
            '-i', f'{self.path}.wav',
            '-c:v', 'copy',
            '-c:a', 'aac',
            '-shortest',
            f'{self.path}.mp4'
        ], check=True,env=env)
        os.remove(f'{self.path}-t.mp4')
        save(self.path+'.mp4')
        log('pas','MP4 file written to Downloads/Audiolizer')
    def _addvframe(self):
        if self.recording and self.recorder:
            frame=pygame.surfarray.array3d(self.screen)
            frame=cv2.cvtColor(frame,cv2.COLOR_RGB2BGR)
            frame=np.rot90(frame)
            frame=cv2.flip(frame,0)
            self.recorder.write(frame)
    def parse_ACode2vidi(self):
        lines = readb(self.path+'.AC')
        len_=len(lines)
        ind=0
        while ind<len_-1:
            line=lines[ind]
            frame, func, timept = line
            dur=lines[ind+1][2]-timept
                
            self.frames.append({
                    'frame': frame,
                    'func': func,
                    'timept': timept/self.TPS,
                    'dur': dur/self.TPS
                })
            ind+=1
        self.vidi_dur=(timept+dur)/self.TPS
    def update(self,timept):
        for i in range(6):
            self.strings[i].update(timept)
            self.dots[i].update(timept)
        self.arrow.update(timept)
        
        if self.vidi_dur>0:
                self.structure['Time'][0]=f'{str(int(timept/60)).zfill(2)}:{str(round(timept)%60).zfill(2)}||{str(int(self.vidi_dur/60)).zfill(2)}:{str(round(self.vidi_dur)%60).zfill(2)}'
                progress = timept / self.vidi_dur
                self.structure['ProgressBar'][1][2] = int(progress * self.bar_width)  # Multiply first, then int()
                self.structure['ProgressDot'][1][0] = self.PDot_start + int(progress * self.bar_width)
    def run(self,runner=1,saver=0):
        pygame.mixer.init()
        pygame.mixer.music.load(self.path+'.wav')
        
        dt=0
        timept=0
        last_line=-1
        line=0
        clock= pygame.time.Clock()
        
        cdur=0
        
        plps=1
        
        pygame.mixer.music.play()
        
        if saver:
            self._record()
        
        while runner:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    runner=0
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        log('err','Playback exited by user')
                        runner=0
                    if event.key == pygame.K_SPACE:
                        plps*=-1
                        if plps==1:
                            log('wrn','Playback resumed ...')
                            pygame.mixer.music.unpause()
                        elif plps == -1:
                            log('wrn','Playback paused')
                            pygame.mixer.music.pause()
                        
                    pass
                
            if plps == -1:
                clock.tick(FPS)
                continue
            self.screen.fill(Colors['BackGround'])
            self.setup()
            
            
            if timept>self.vidi_dur:
                last_line=-1
                self._stop()
                pygame.mixer.quit()
                break

            for i, f in enumerate(self.frames):
                if timept >= f['timept']:
                    line = i
                else:
                    break
                
                
            if line != last_line and line <len(self.frames):
                frame_=self.frames[line]
                frame = frame_['frame']
                func= frame_['func']
                fdur=frame_['dur']
                
                if line in self.sequence['Chords'].keys():
                    self.structure['ChordP'][0]=' '.join(self.sequence['Chords'][line][1])
                    
                    cdur=(self.sequence['Chords'][line][0])/len(self.sequence['Chords'][line][1])
                    cdur=cdur/self.TPS
                    
                if line in self.sequence['Strums'].keys():
                    self.structure['StrumP'][0]=''.join(self.sequence['Strums'][line][1])  # Fixed: was 'StrumsP'  
                
                
                
                for ind,i in enumerate(frame):
                    if not i.isdigit():
                        self.dots[ind].place(timept,0,cdur) 
                        continue
                    if not func =='P':   
                        self.dots[ind].place(timept,int(i),cdur) 
                    else:
                        self.dots[ind].place(timept,int(i),fdur) 
                        
                    

                self.arrow.trigger(timept,fdur,func)
                    
                if func in ['D', 'U', 'P', 'H']:
                    for ind,i in enumerate(frame):
                        if not i.isdigit():
                            self.strings[ind].vibrate(timept,duration=-1,fret=self.capo_fret,dirn=-1)
                            continue
                        if func == 'D':
                            self.strings[ind].vibrate(timept,duration=fdur,fret=int(i),dirn=-1)
                        elif func == 'U':
                            self.strings[ind].vibrate(timept,duration=fdur,fret=int(i),dirn=1)
                        elif func == 'P':
                            if int(i)>1:
                                self.strings[ind].vibrate(timept,duration=fdur,fret=int(i),dirn=1)
                            else:
                                self.strings[ind].vibrate(timept,duration=fdur,fret=int(i),dirn=-1)
                                
                                
                            
                            
                last_line=line 
            dt=clock.tick(FPS)/1000.0
            self.update(timept)
            timept+=dt
            if plps==1:
                self._addvframe()
            pygame.display.flip()
        pygame.mixer.quit()
        if saver:
            save(self.path+'.mp4')
        for i in ['.AC','.mid','.wav','.mp4']:
            if os.path.exists(self.path+i):
                os.remove(self.path+i)
        pygame.quit()
        
class Dot():
    def __init__(self,surface,ind,fretsp,stringsp):
        self.surface=surface
        self.color=Colors['Primary']
        
        self.frets=fretsp
        
        self.size=min(stringsp[ind][1]*3,8)
        self.Y=stringsp[ind][0]+stringsp[ind][1]-2
        
        self.fret=0
        
        self.state='idle'
        self.type='tap'
        self.duration=0
        self.timept=0
        self.scale=0
        
        self.keyframes={
            'place':[[0.0,0.9],[0.05,1.05],[0.15,1.0],[0.95,0.995],[0.9995,0.1],[1.0,0.0]],#[%duration,#scale]
        }
        
    def draw(self):
        x=self._fret2pos()
        if x == -1 or self.scale==0.0:    
            return
        pygame.draw.circle(self.surface,self.color,(x,self.Y),self.scale*self.size)
        
    def _fret2pos(self):
        if self.fret==0:
            return -1
        elif self.fret>12:
            return self.frets[12][0]+int((self.frets[11][0]-self.frets[12][0])/2)
        else:
            return self.frets[self.fret][0]+int((self.frets[self.fret-1][0]-self.frets[self.fret][0]+self.frets[self.fret][1])/2)
    def _interpolate(self,progress,keyframes):
        progress = max(0.0, min(1.0, progress))
        prev_kf = keyframes[0]
        next_kf = keyframes[-1]
        
        for i, kf in enumerate(keyframes):
            if kf[0] >= progress:
                next_kf = kf
                prev_kf = keyframes[max(0, i - 1)]
                break
        if prev_kf[0] == next_kf[0]:
            return prev_kf[1]
        t = (progress - prev_kf[0]) / (next_kf[0] - prev_kf[0])
        t = 1 - pow(1 - t, 3)
        return prev_kf[1] + (next_kf[1] - prev_kf[1]) * t
    
    def place(self,timept,fret,duration):
        self.fret=fret
        self.state='motion'
        self.timept=timept
        self.duration=duration
        self.scale=0.0
    def update(self,timept):
        if self.state == 'idle':
            return
        elapsed=timept-self.timept
        if elapsed>=self.duration:
            self.state='idle'
            self.scale=0.0
            return
        progress = elapsed / self.duration
        self.scale = self._interpolate(progress, self.keyframes['place'])
  
class Arrow():
    def __init__(self,surface,container):
        self.surface=surface
        self.colors={
            'U':Colors['Arrow'],
            'D':Colors['Arrow'],
            'H':Colors['Hit'],
        }
        
        self.container=container
        self.width=50
        self.offset=5
        self.head=round(0.3*container[3])
        
        self.center=[ container[0] + container[2] // 2 +self.width//2,container[1]+container[3]//2]
        self.max_=[container[0] + container[2],container[1]+container[3]+5]
        self.min_=[container[0]+self.width//2,container[1]]
        
        
        self.color=None
        self.shape=[]
        self.shapes={}
        
        self._reset()
        
        self.keyframes={
            'U':{
                0.0:[0.3,0.15],
                0.6:[0.8,0.7],
                0.8:[1.05,0.85],
                1.0:[1.0,1.0],
            },
            'D':{
                0.0:[0.2,0.15],
                0.6:[0.8,0.7],
                0.8:[1.05,0.85],
                1.0:[1.0,1.0],
            },
            'H':{
                0.0:[1.0,0.8],
                0.6:[1.0,0.95],
                0.8:[1.0,1.05],
                1.0:[1.0,0.9],
            },
        }
        
        self.state='idle'
        self.type='D'
        self.duration=0
        self.timept=0
        
        self.height=1.0
        self.scale=1.0
    def _reset(self):
        self.height=1.0
        self.scale=1.0
        
        self.shapes={
            'U':[
                [self.center[0], self.min_[1]],  # Top point
                [self.center[0] - self.width, self.min_[1] + self.head],  # Left wing
                [self.center[0] - self.width // 2, self.min_[1] + self.head - self.offset],  # Left neck
                [self.center[0] - self.width // 2, self.max_[1] - self.offset],  # Left bottom
                [self.center[0] + self.width // 2, self.max_[1] - self.offset],  # Right bottom
                [self.center[0] + self.width // 2, self.min_[1] + self.head - self.offset],  # Right neck
                [self.center[0] + self.width, self.min_[1] + self.head], ], # Right wing
            'D':[
                [self.center[0], self.max_[1]],  # Top point
                [self.center[0] - self.width, self.max_[1] - self.head],  # Left wing
                [self.center[0] - self.width // 2, self.max_[1] - self.head + self.offset],  # Left neck
                [self.center[0] - self.width // 2, self.min_[1] - self.offset],  # Left bottom
                [self.center[0] + self.width // 2, self.min_[1] - self.offset],  # Right bottom
                [self.center[0] + self.width // 2, self.max_[1] - self.head + self.offset],  # Right neck
                [self.center[0] + self.width, self.max_[1] - self.head],],  # Right wing 
            'H':[
                [self.center[0]-self.width//2,self.min_[1]],
                [self.center[0]+self.width//2,self.min_[1]],
                [self.center[0]+self.width//2,self.center[1]-self.width//2],
                [self.center[0]+2*self.width,self.center[1]-self.width//2],
                [self.center[0]+2*self.width,self.center[1]+self.width//2],
                [self.center[0]+self.width//2,self.center[1]+self.width//2],
                [self.center[0]+self.width//2,self.max_[1]],
                [self.center[0]-self.width//2,self.max_[1]],
                [self.center[0]-self.width//2,self.center[1]+self.width//2],
                [self.center[0]-2*self.width,self.center[1]+self.width//2],
                [self.center[0]-2*self.width,self.center[1]-self.width//2],
                [self.center[0]-self.width//2,self.center[1]-self.width//2],
            ],
        }
    def _animate(self,progress):
        keyframes = self.keyframes.get(self.type, {})
        keys = sorted(keyframes.keys())
        prev_k, next_k = keys[0], keys[-1]
        for i, k in enumerate(keys):
            if k >= progress:
                next_k = k
                prev_k = keys[max(0, i - 1)]
                break
        if prev_k == next_k:
            hgt, scale = keyframes[prev_k]
        else:
            t = (progress - prev_k) / (next_k - prev_k)
            t = 1 - pow(1 - t, 3)
            hgt = keyframes[prev_k][0] + (keyframes[next_k][0] - keyframes[prev_k][0]) * t
            scale = keyframes[prev_k][1] + (keyframes[next_k][1] - keyframes[prev_k][1]) * t

        base_shape = np.array(self.shapes[self.type])
        if self.type == 'U':
            base_y = self.max_[1] - self.offset
            shape_scaled = base_shape.copy()
            shape_scaled[:, 1] = base_y - (base_y - shape_scaled[:, 1]) * hgt
            center_x = np.mean(shape_scaled[:, 0])
            shape_scaled[:, 0] = (shape_scaled[:, 0] - center_x) * scale + center_x

        elif self.type == 'D':
            head_y = self.min_[1]
            shape_scaled = base_shape.copy()
            shape_scaled[:, 1] = head_y + (shape_scaled[:, 1] - head_y) * hgt
            center_x = np.mean(shape_scaled[:, 0])
            shape_scaled[:, 0] = (shape_scaled[:, 0] - center_x) * scale + center_x

        else:
            center = np.mean(base_shape, axis=0)
            shape_scaled = (base_shape - center) * scale + center

        self.shape = shape_scaled.tolist()
        self.height = hgt
        self.scale = scale
    def draw(self):
        if self.type not in 'DUH':
            return
        if not len(self.shape)>2:
            return
        pygame.draw.polygon(self.surface,self.color,self.shape)
        
    def trigger(self,timept,duration,func):
        if not func in 'DUH':
            self.state='idle'
            self.type=func
            self._reset()
            return
        self.state='motion'
        self.timept=timept
        self.duration=duration
        self.type=func
        self.shape=self.shapes[func]
        self.color=self.colors[func]
    def update(self,timept):
        if self.state == 'idle':
            return
        elapsed=timept-self.timept
        if elapsed>=self.duration:
            self.state='idle'
            self._reset()
            return
        progress = elapsed / self.duration
        self._animate(progress)
class String():
    def __init__(self,surface:pygame.surface,ind,span,frequency,stringsp=[],fretsp=[]):
        self.surface=surface
        
        self.ind=ind
        self.color=Colors['Text']
        self.thickness = stringsp[ind][1]
        self.Y = stringsp[ind][0]
        self.frequency=frequency
        self.start=span[0]
        self.length=span[1]
            
        self.frets=fretsp
        self.points=[]
        self._init_points()
        
        self.fret=self.length
        
        self.state='idle'
        self.vib_timept=0
        self.action_dur=0
        self.y=0
        
        self.amplitude=0
        self.dirn=-1
        
    def _init_points(self):
        self.points = []
        for x in range(self.start, self.start + self.length):
            self.points.append((x, self.Y))
            
    def _fret2pos(self):
        if self.fret==0:
            return self.length
        elif self.fret>12:
            return self.frets[12][0]+int((self.frets[11][0]-self.frets[12][0])/2)
        else:
            return self.frets[self.fret][0]+int((self.frets[self.fret-1][0]-self.frets[self.fret][0]+self.frets[self.fret][1])/2)
    
    def _reset(self):
        for i in range(len(self.points)):
            x_pos = self.start + i
            self.points[i] = (x_pos, self.Y)
            
    def draw(self):
        if not self.points:
            self._init_points()
        if len(self.points) > 1:
            pygame.draw.lines(self.surface, self.color, False, self.points, self.thickness)
            # pygame.draw.circle(self.surface,Colors['Hole'],(self.fret,self.Y),6) 
            return
        for i in range(self.length+1):
            x_pos=self.start+i
            self.points.append((x_pos,self.Y))
        pygame.draw.lines(self.surface,self.color,False,self.points,self.thickness)
        # pygame.draw.circle(self.surface,Colors['Primary'],(self.fret,self.Y),2)
    def vibrate(self,timept,duration=2.0,fret=0,dirn=-1):
        if self.state=='motion':
            self._reset()
        self.fret=fret
        self.fret=self._fret2pos()
        self.state='motion'
        self.vib_timept=timept
        self.action_dur=duration
        self.amplitude= int((self.fret/self.length)*7 )+round(6/self.thickness)
        self.dirn=dirn
    def update(self,timept):
        if self.state == 'idle':
            return
        elapsed=timept-self.vib_timept
        
        if elapsed>=self.action_dur:
            self.state='idle'
            self._reset()
            return
        
        decay=math.exp(-3.0 * elapsed / self.action_dur)
        amplitude = self.amplitude * decay
        if amplitude < 0.1:
            self.state = 'idle'
            self._reset()
            return
        
        for i in range(self.start+5,self.fret):
            x_pos= self.start+i
            x_norm=i/float(self.fret)
            shape_= math.sin(x_norm * math.pi)
            time_ = math.sin(timept * self.frequency * 2.0 * math.pi)
            y_pos= self.Y+self.dirn*(amplitude*shape_*time_)
            self.points[i]=(x_pos,y_pos)
        
        
        
        
