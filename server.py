import http.server
import socketserver
import threading
import webbrowser
import json
import time
import re
import psutil
import os
from threading import Lock
from assets import INPUT, PORT, CONFIG, readb

URL = f"http://localhost:{PORT}"

last_command = None
last_config = None
last_acode = None
last_cli_log = []
last_active=time.time()
lock = Lock()

class Handler(http.server.SimpleHTTPRequestHandler):

     def log_message(self, *args):
          pass

     def do_POST(self):
          global last_command, last_config, last_active
          length = int(self.headers.get('Content-Length', 0))
          try:
               data = json.loads(self.rfile.read(length))
          except:
               self.send_response(400)
               self.end_headers()
               return

          with lock:
               last_active = time.time()
               if self.path == '/cli_command':
                    last_command = data.get('command')
               elif self.path == '/config':
                    last_config = data.get('config')
          self.send_response(200)
          self.end_headers()

     def do_GET(self):
          if self.path == '/get_acode':
               with lock:
                    data = last_acode or ""
               self.send_response(200)
               self.send_header('Content-Type','application/json')
               self.end_headers()
               self.wfile.write(json.dumps({'acode':data}).encode())
          elif self.path == '/get_cli_logs':
               with lock:
                    logs = last_cli_log.copy() if last_cli_log else []
                    last_cli_log.clear()  # Clear after sending
               self.send_response(200)
               self.send_header('Content-Type','application/json')
               self.end_headers()
               self.wfile.write(json.dumps({'logs': logs}).encode())
          else:
               super().do_GET()

class ThreadedServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
     allow_reuse_address = True
     daemon_threads = True
def monitor():
     global last_active
     time.sleep(30)
     while True:
          time.sleep(10)
          with lock:
               inact_time=time.time() - last_active
          if inact_time > 300:
               parentps=psutil.Process(os.getpid())
               for child in parentps.children(recursive=True):
                    child.kill()
               parentps.kill() 

def run():
     threading.Thread(target=monitor, daemon=True).start()

     with ThreadedServer(("", PORT),
          lambda *a, **k: Handler(*a, directory=INPUT, **k)) as srv:

          threading.Thread(target=lambda: webbrowser.open(URL), daemon=True).start()
          srv.serve_forever()

def get_command():
     global last_command
     with lock:
          cmd = last_command
          last_command = None

     if not cmd:
          return None, {}

     m = re.match(r"\s*(\w+)", cmd)
     command = m.group(1) if m else ''
     options = {}

     for o,v1,v2,v3 in re.findall(r"-(\w)(?:\s+(?:'([^']*)'|\"([^\"]*)\"|(\S+)))?", cmd):
          options[o] = v1 or v2 or v3

     return command, options

def get_config():
     global last_config
     with lock:
          cfg = last_config
     if cfg:
          open(CONFIG,'w').write(cfg)
     return cfg

def log(type, message):
    global last_cli_log
    
    colors = {
        'err': '#ff5555',    # red
        'wrn': '#f1fa8c',  # yellow
        'pas': '#50fa7b',  # green
        'inf': '#8be9fd',     # cyan
        'def': "#d3d3d3"   # default green
    }
    
    color = colors.get(type.lower(), colors['def'])
    formatted = f'ADLiz>><span style="color:{color}">[{type.upper()}] {message}</span>'
    
    with lock:
          last_cli_log.append(formatted)
          
def put_acode(file,tpb,bar0):
     global last_acode
     try:
          acode=""
          lines=readb(file)
          i=0
          d=0
          while i<len(lines):
               f,fn,t=lines[i]
               try:
                    d=lines[i+1][2]-t
               except IndexError:
                    d=lines[-1][2]-t
               acode+=f"{i//bar0+1}-{i%bar0 + 1} :{'-'.join(f)}.{fn}[{round(d/tpb,2)}]\n"
               i+=1
          if acode:
               last_acode=acode
          return True
     except:
          last_acode = ""
          return False
