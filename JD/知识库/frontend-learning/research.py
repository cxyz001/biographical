"""Search GitHub and record source files actually read."""
import concurrent.futures
import datetime
import hashlib
import json
import pathlib
import urllib.parse
import urllib.request

ROOT = pathlib.Path(__file__).parent
SOURCES = [
 ('mdn/content','main','files/en-us/learn_web_development/core/scripting/fetching_data/index.md'),
 ('microsoft/TypeScript-Website','v2','packages/documentation/copy/en/handbook-v2/Narrowing.md'),
 ('reactjs/react.dev','main','src/content/learn/synchronizing-with-effects.md'),
 ('vuejs/docs','main','src/guide/essentials/reactivity-fundamentals.md'),
 ('vitejs/vite','main','docs/guide/env-and-mode.md'),
 ('TanStack/query','main','docs/framework/react/guides/query-keys.md'),
 ('vercel/next.js','canary','docs/01-app/03-api-reference/01-directives/use-client.mdx'),
 ('OAI/OpenAPI-Specification','main','versions/3.1.1.md'),
 ('mswjs/msw','main','README.md'),
 ('microsoft/playwright','main','README.md'),
 ('vitest-dev/vitest','main','docs/guide/index.md'),
 ('GoogleChrome/web-vitals','main','README.md'),
 ('electron/electron','main','docs/tutorial/security.md'),
 ('expressjs/express','master','Readme.md'),
 ('apache/echarts','master','README.md'),
 ('single-spa/single-spa','main','README.md'),
]

def get(url):
    request=urllib.request.Request(url,headers={'User-Agent':'frontend-learning'})
    with urllib.request.urlopen(request,timeout=20) as response:
        return response.read().decode('utf-8')

def read(item):
    repo,branch,path=item
    record=dict(repository=repo,branch=branch,path=path,date=str(datetime.date.today()),url=f'https://github.com/{repo}/blob/{branch}/{path}')
    try:
        body=get(f'https://raw.githubusercontent.com/{repo}/{branch}/{path}')
        record.update(characters=len(body),sha256=hashlib.sha256(body.encode()).hexdigest())
        words=['cleanup','race','AbortController','unknown','queryKey','serializ','VITE_','contextIsolation','nodeIntegration','getCLS','getINP','getLCP','reactive','ref(','test(','http.get','app.get','nullable','security']
        lines=body.splitlines()
        selected=set(range(min(10,len(lines))))
        for i,line in enumerate(lines):
            if any(word in line for word in words):
                selected.update(range(max(0,i-1),min(len(lines),i+3)))
        excerpt='\n'.join(f'{i+1}: {lines[i]}' for i in sorted(selected))[:6500]
        return record,excerpt
    except Exception as exc:
        return dict(record,error=str(exc)),''

if __name__=='__main__':
    searches=[]
    for query in ['react documentation','vue documentation','typescript handbook','frontend mock service worker','playwright end to end']:
        try:
            data=json.loads(get('https://api.github.com/search/repositories?q='+urllib.parse.quote(query)+'&per_page=2'))
            searches.append(dict(query=query,results=[dict(repository=x['full_name'],url=x['html_url']) for x in data['items']]))
        except Exception as exc:
            searches.append(dict(query=query,error=str(exc)))
    (ROOT/'search-results.json').write_text(json.dumps(searches,ensure_ascii=False,indent=2),encoding='utf-8')
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
        results=list(pool.map(read,SOURCES))
    (ROOT/'sources.json').write_text(json.dumps([x[0] for x in results],ensure_ascii=False,indent=2),encoding='utf-8')
    for record,excerpt in results:
        print(record['repository'],record.get('error','OK'))
        print(excerpt)
