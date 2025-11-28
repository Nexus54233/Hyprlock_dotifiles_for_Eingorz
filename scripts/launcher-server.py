#!/usr/bin/env python3
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import subprocess
import os
import glob

class LauncherHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/apps':
            apps = self.get_applications()
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(apps).encode())
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_POST(self):
        if self.path == '/exec':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode())
            cmd = data.get('cmd', '')
            
            if cmd:
                subprocess.Popen(cmd, shell=True, start_new_session=True)
            
            self.send_response(200)
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(b'OK')
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def get_applications(self):
        apps = []
        desktop_dirs = [
            '/usr/share/applications',
            '/usr/local/share/applications',
            os.path.expanduser('~/.local/share/applications')
        ]
        
        seen = set()
        
        for desktop_dir in desktop_dirs:
            if not os.path.exists(desktop_dir):
                continue
            
            for filepath in glob.glob(f'{desktop_dir}/*.desktop'):
                filename = os.path.basename(filepath)
                if filename in seen:
                    continue
                seen.add(filename)
                
                try:
                    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                        name = None
                        exec_cmd = None
                        no_display = False
                        
                        for line in f:
                            line = line.strip()
                            if line.startswith('Name=') and not name:
                                name = line.split('=', 1)[1]
                            elif line.startswith('Exec='):
                                exec_cmd = line.split('=', 1)[1]
                                exec_cmd = exec_cmd.replace('%U', '').replace('%F', '')
                                exec_cmd = exec_cmd.replace('%u', '').replace('%f', '')
                                exec_cmd = exec_cmd.replace('%i', '').replace('%c', '')
                                exec_cmd = exec_cmd.replace('%k', '').strip()
                            elif line.startswith('NoDisplay=true'):
                                no_display = True
                                break
                        
                        if name and exec_cmd and not no_display:
                            apps.append({'name': name, 'cmd': exec_cmd})
                except:
                    pass
        
        return sorted(apps, key=lambda x: x['name'].lower())
    
    def log_message(self, format, *args):
        pass  # Suppress log messages

if __name__ == '__main__':
    server = HTTPServer(('localhost', 8888), LauncherHandler)
    print('Launcher server running on http://localhost:8888')
    server.serve_forever()
