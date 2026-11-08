import concurrent.futures, datetime, hashlib, json, pathlib, urllib.request

ROOT = pathlib.Path(__file__).parent
HEADERS = {'User-Agent': 'cpp-learning-research'}
def get(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers=HEADERS), timeout=35) as r:
        return r.read().decode('utf-8')
queries = ['modern cpp tutorial', 'cpp core guidelines', 'asio networking cpp', 'qt serialport', 'libmodbus']
search = []
for q in queries:
    try:
        url = 'https://api.github.com/search/repositories?q=' + urllib.parse.quote(q) + '&sort=stars&per_page=4'
        data = json.loads(get(url))
        search.append({'query': q, 'url': url, 'repositories': [x['full_name'] for x in data['items']]})
    except Exception as e:
        search.append({'query': q, 'error': str(e)})
(ROOT/'search-results.json').write_text(json.dumps(search, ensure_ascii=False, indent=2), encoding='utf-8')
items = [
 ('isocpp/CppCoreGuidelines','master','CppCoreGuidelines.md'),
 ('changkun/modern-cpp-tutorial','master','book/zh-cn/03-runtime.md'),
 ('AnthonyCalandra/modern-cpp-features','master','CPP17.md'),
 ('Kitware/CMake','master','Help/guide/tutorial/index.rst'),
 ('google/googletest','main','docs/primer.md'),
 ('chriskohlhoff/asio','master','asio/src/examples/cpp11/echo/async_tcp_echo_server.cpp'),
 ('qt/qtbase','dev','examples/corelib/threads/queuedcustomtype/worker.cpp'),
 ('qt/qtserialport','dev','examples/serialport/terminal/mainwindow.cpp'),
 ('stephane/libmodbus','master','tests/unit-test-client.c'),
 ('linux-can/can-utils','master','README.md'),
 ('eclipse-paho/paho.mqtt.cpp','master','README.md'),
 ('gabime/spdlog','v1.x','README.md'),
 ('google/benchmark','main','docs/user_guide.md'),
 ('opencv/opencv','4.x','samples/cpp/tutorial_code/HighGUI/video-input-psnr-ssim/video-input-psnr-ssim.cpp'),
 ('FFmpeg/FFmpeg','master','doc/examples/decode_video.c'),
 ('wolfpld/tracy','master','README.md'),
 ('microsoft/vcpkg','master','README.md'),
 ('catchorg/Catch2','devel','docs/tutorial.md'),
]
def fetch(x):
    repo, branch, path = x
    url = f'https://raw.githubusercontent.com/{repo}/{branch}/{path}'
    record = {'repository': repo, 'branch': branch, 'path': path, 'github_url': f'https://github.com/{repo}/blob/{branch}/{path}', 'checked_date': str(datetime.date.today())}
    try:
        body = get(url)
        record.update(text_sha256=hashlib.sha256(body.encode()).hexdigest(), text_characters=len(body), body=body)
    except Exception as e:
        record['error'] = str(e)
    return record
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
    records = list(pool.map(fetch, items))
(ROOT/'research.json').write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding='utf-8')
(ROOT/'sources.json').write_text(json.dumps([{k:v for k,v in r.items() if k != 'body'} for r in records], ensure_ascii=False, indent=2), encoding='utf-8')
for r in records:
    print(r['repository'], r.get('text_characters', r.get('error')))
print('SEARCH', json.dumps(search))
