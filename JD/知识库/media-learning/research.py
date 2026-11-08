"""Reproduce GitHub searches and record the exact upstream files read."""
import concurrent.futures
import datetime
import hashlib
import json
import pathlib
import urllib.request
import urllib.parse

ROOT = pathlib.Path(__file__).parent
SOURCES = [
 ('FFmpeg/FFmpeg','master','doc/examples/remux.c'),
 ('FFmpeg/FFmpeg','master','doc/examples/decode_video.c'),
 ('FFmpeg/FFmpeg','master','doc/muxers.texi'),
 ('GStreamer/gst-docs','master','markdown/tutorials/basic/hello-world.md'),
 ('ossrs/srs','develop','README.md'),
 ('ZLMediaKit/ZLMediaKit','master','README.md'),
 ('bluenviron/mediamtx','main','README.md'),
 ('video-dev/hls.js','master','README.md'),
 ('webrtc/samples','gh-pages','src/content/peerconnection/pc1/js/main.js'),
 ('pion/webrtc','master','examples/README.md'),
 ('coturn/coturn','master','README.md'),
 ('648540858/wvp-GB28181-pro','master','README.md'),
 ('FFmpeg/FFmpeg','master','doc/indevs.texi'),
 ('ggerganov/whisper.cpp','master','examples/stream/README.md'),
 ('k2-fsa/sherpa-onnx','master','README.md'),
 ('aiortc/aiortc','main','examples/server/README.rst'),
]

def get(url):
 req=urllib.request.Request(url,headers={'User-Agent':'media-learning-research','Accept':'application/vnd.github+json'})
 with urllib.request.urlopen(req,timeout=25) as r: return r.read().decode('utf-8')

def source(item):
 repo,branch,path=item
 record=dict(repository=repo,branch=branch,path=path,checked_date=str(datetime.date.today()),github_url=f'https://github.com/{repo}/blob/{branch}/{path}')
 try:
  body=get(f'https://raw.githubusercontent.com/{repo}/{branch}/{path}')
  record.update(text_sha256=hashlib.sha256(body.encode()).hexdigest(),text_characters=len(body))
  return record,body
 except Exception as exc: return dict(record,error=str(exc)),''

if __name__=='__main__':
 searches=[]
 for query in ['ffmpeg remux examples','webrtc samples','rtsp streaming server','GB28181 wvp','streaming speech recognition sherpa']:
  try:
   data=json.loads(get('https://api.github.com/search/repositories?q='+urllib.parse.quote(query)+'&per_page=3'))
   searches.append(dict(query=query,results=[dict(repository=x['full_name'],url=x['html_url'],description=x['description']) for x in data['items']]))
  except Exception as exc: searches.append(dict(query=query,error=str(exc)))
 with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool: results=list(pool.map(source,SOURCES))
 (ROOT/'search-results.json').write_text(json.dumps(searches,ensure_ascii=False,indent=2),encoding='utf-8')
 (ROOT/'sources.json').write_text(json.dumps([r for r,b in results],ensure_ascii=False,indent=2),encoding='utf-8')
 for r,b in results:
  print(r['repository'],r['path'],r.get('error','OK'))
  if b:
   # Display relevant excerpts, not just repository metadata.
   lines=b.splitlines()
   words=['rescale','write_header','write_trailer','send_packet','receive_frame','keyframe','hls_time','hls_flags','listen','docker run','iceServers','turn:','RTSP','GB28181','stream','license','License','createOffer','setRemoteDescription']
   selected=set(range(min(18,len(lines))))
   for i,line in enumerate(lines):
    if any(w in line for w in words): selected.update(range(max(0,i-1),min(len(lines),i+3)))
   print('\n'.join(f'{i+1}: {lines[i]}' for i in sorted(selected))[:11500])
