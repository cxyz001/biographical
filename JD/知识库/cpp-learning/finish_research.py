import hashlib, json, pathlib, urllib.request
root=pathlib.Path(__file__).parent
records=json.loads((root/'research.json').read_text(encoding='utf-8'))
fixes={'chriskohlhoff/asio':('master','asio/src/examples/cpp11/echo/async_tcp_echo_server.cpp'), 'qt/qtbase':('dev','src/corelib/thread/qthread.cpp'), 'opencv/opencv':('4.x','samples/cpp/videocapture_basic.cpp')}
for r in records:
    if 'error' not in r: continue
    branch,path=fixes[r['repository']]
    # Asio now keeps its sources directly under the repository root.
    if r['repository']=='chriskohlhoff/asio': path='src/examples/cpp11/echo/async_tcp_echo_server.cpp'
    url=f"https://raw.githubusercontent.com/{r['repository']}/{branch}/{path}"
    try:
        with urllib.request.urlopen(url,timeout=40) as response: body=response.read().decode()
        r.update(branch=branch,path=path,github_url=f"https://github.com/{r['repository']}/blob/{branch}/{path}",body=body,text_characters=len(body),text_sha256=hashlib.sha256(body.encode()).hexdigest())
        del r['error']
    except Exception as e: r['error']=str(e)
(root/'research.json').write_text(json.dumps(records,ensure_ascii=False,indent=2),encoding='utf-8')
(root/'sources.json').write_text(json.dumps([{k:v for k,v in r.items() if k!='body'} for r in records],ensure_ascii=False,indent=2),encoding='utf-8')
for r in records:
    print('\nREPOSITORY',r['repository'],r.get('error','OK'))
    lines=r.get('body','').splitlines()
    if len(lines)>400:
        # Read selected substantive rules/implementation rather than a huge dump.
        keywords=['R.1:', 'R.20:', 'CP.42:', 'CP.43:', 'shared_ptr', 'moveToThread', 'AutoConnection', 'Benchmark', 'modbus_read_registers']
        found=0
        for i,line in enumerate(lines):
            if any(k in line for k in keywords):
                print('\n'.join(lines[max(0,i-2):i+12]))
                found+=1
                if found>=4: break
    else: print('\n'.join(lines[:100]))
