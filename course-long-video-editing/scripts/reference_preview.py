"""Serve the bundled public reference gallery on loopback only."""
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
from functools import partial
from pathlib import Path
import re,shutil
ROOT=Path(__file__).resolve().parents[1]/'assets/examples/quality-baseline'
class Handler(SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
 def list_directory(self,path):self.send_error(404);return None
 def send_head(self):
  self.remaining=None;p=Path(self.translate_path(self.path)).resolve()
  if not p.is_relative_to(ROOT.resolve()):self.send_error(403);return None
  header=self.headers.get('Range')
  if header and p.is_file():
   match=re.fullmatch(r'bytes=(\d+)-(\d*)',header)
   if match:
    size=p.stat().st_size;a=int(match[1]);b=min(int(match[2]) if match[2] else size-1,size-1)
    if a>b:self.send_error(416);return None
    stream=p.open('rb');stream.seek(a);self.remaining=b-a+1
    self.send_response(206);self.send_header('Content-Type',self.guess_type(str(p)));self.send_header('Content-Range',f'bytes {a}-{b}/{size}');self.send_header('Content-Length',str(self.remaining));self.send_header('Accept-Ranges','bytes');self.end_headers();return stream
  return super().send_head()
 def end_headers(self):
  self.send_header('X-Content-Type-Options','nosniff');self.send_header('Content-Security-Policy',"default-src 'self'; img-src 'self' data:; media-src 'self'; style-src 'self'; script-src 'self'");super().end_headers()
 def copyfile(self,source,out):
  try:
   if self.remaining is None:shutil.copyfileobj(source,out)
   else:
    while self.remaining:
     chunk=source.read(min(self.remaining,1024*1024))
     if not chunk:break
     out.write(chunk);self.remaining-=len(chunk)
  except (BrokenPipeError,ConnectionResetError):pass
def main():
 server=ThreadingHTTPServer(('127.0.0.1',0),partial(Handler,directory=str(ROOT)))
 print(f'http://127.0.0.1:{server.server_port}/gallery.html',flush=True)
 try:server.serve_forever()
 except KeyboardInterrupt:server.server_close()
if __name__=='__main__':main()
