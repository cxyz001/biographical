import hashlib
import json
import pathlib
import urllib.request

root = pathlib.Path(__file__).parent
rows = json.loads((root/'research.json').read_text(encoding='utf-8'))
fixes = {'yoctoproject/poky':'README.poky', 'microsoft/onnxruntime':'README.md'}
for row in rows:
    if 'error' not in row:
        continue
    path = fixes.get(row['repository'], row['path'])
    if path == 'Documentation/rpmsg.rst': path='Documentation/driver-api/rpmsg.rst'
    url = f"https://raw.githubusercontent.com/{row['repository']}/{row['branch']}/{path}"
    try:
        with urllib.request.urlopen(url, timeout=40) as response:
            body = response.read().decode('utf-8')
        row.update(path=path, github_url=f"https://github.com/{row['repository']}/blob/{row['branch']}/{path}",body=body,text_characters=len(body),text_sha256=hashlib.sha256(body.encode()).hexdigest())
        del row['error']
    except Exception as exc:
        row['error']=str(exc)
(root/'research.json').write_text(json.dumps(rows, ensure_ascii=False, indent=2),encoding='utf-8')
(root/'sources.json').write_text(json.dumps([{k:v for k,v in r.items() if k!='body'} for r in rows],ensure_ascii=False,indent=2),encoding='utf-8')
for row in rows:
    print('\nSOURCE:',row['repository'],row['path'],row.get('error','OK'))
    lines = row.get('body','').splitlines()
    print('\n'.join(lines[:32]))
    words = ['bootcount','mark-good','dma_map_single','dma_mapping_error','I2C_RDWR','rproc','rpmsg_send','watchdog','ExecStart','qemu-system','make qemu','xTask','execution provider','RK3588']
    snippets=0
    for i,line in enumerate(lines[32:],32):
        if any(w.lower() in line.lower() for w in words):
            print('\n'.join(lines[max(0,i-2):i+12]))
            snippets+=1
            if snippets==2: break
