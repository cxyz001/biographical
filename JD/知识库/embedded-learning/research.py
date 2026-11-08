"""Fetch GitHub learning references. No third-party Python dependencies."""
import concurrent.futures
import datetime
import hashlib
import json
import pathlib
import urllib.parse
import urllib.request

ROOT = pathlib.Path(__file__).parent
def get(url):
    request = urllib.request.Request(url, headers={'User-Agent': 'embedded-learning-research'})
    with urllib.request.urlopen(request, timeout=35) as response:
        return response.read().decode('utf-8')

queries = ['embedded linux training bootlin', 'buildroot embedded linux', 'linux device driver tutorial', 'openamp rpmsg', 'rknn model zoo', 'rauc ota']
search = []
for query in queries:
    url = 'https://api.github.com/search/repositories?q=' + urllib.parse.quote(query) + '&sort=stars&per_page=4'
    row = {'query': query, 'url': url, 'checked_date': str(datetime.date.today())}
    try:
        row['repositories'] = [x['full_name'] for x in json.loads(get(url))['items']]
    except Exception as exc:
        row['error'] = str(exc)
    search.append(row)
(ROOT/'search-results.json').write_text(json.dumps(search, ensure_ascii=False, indent=2), encoding='utf-8')

items = [
 ('bootlin/training-materials','master','README.md'),
 ('buildroot/buildroot','master','docs/manual/quickstart.adoc'),
 ('yoctoproject/poky','master','README.poky.md'),
 ('u-boot/u-boot','master','doc/board/emulation/qemu-arm.rst'),
 ('torvalds/linux','master','Documentation/i2c/dev-interface.rst'),
 ('torvalds/linux','master','Documentation/driver-api/driver-model/overview.rst'),
 ('torvalds/linux','master','Documentation/devicetree/usage-model.rst'),
 ('torvalds/linux','master','Documentation/core-api/dma-api-howto.rst'),
 ('torvalds/linux','master','Documentation/rpmsg.rst'),
 ('FreeRTOS/FreeRTOS-Kernel','main','README.md'),
 ('OpenAMP/open-amp','main','README.md'),
 ('zephyrproject-rtos/zephyr','main','samples/subsys/ipc/openamp/README.rst'),
 ('linux-can/can-utils','master','README.md'),
 ('eclipse-mosquitto/mosquitto','master','README.md'),
 ('eclipse-paho/paho.mqtt.c','master','src/samples/MQTTClient_publish.c'),
 ('rauc/rauc','master','docs/basic.rst'),
 ('sbabic/swupdate','master','doc/source/swupdate.rst'),
 ('rockchip-linux/rknn-toolkit2','master','README.md'),
 ('airockchip/rknn_model_zoo','main','README.md'),
 ('microsoft/onnxruntime','main','docs/execution-providers/README.md'),
 ('k3s-io/k3s','master','README.md'),
 ('systemd/systemd','main','man/systemd.service.xml'),
 ('tpm2-software/tpm2-tools','master','README.md'),
]
def fetch(item):
    repo, branch, path = item
    row = {'repository': repo, 'branch': branch, 'path': path, 'checked_date': str(datetime.date.today()), 'github_url': f'https://github.com/{repo}/blob/{branch}/{path}'}
    try:
        body = get(f'https://raw.githubusercontent.com/{repo}/{branch}/{path}')
        row.update(body=body, text_sha256=hashlib.sha256(body.encode()).hexdigest(), text_characters=len(body))
    except Exception as exc:
        row['error'] = str(exc)
    return row
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
    records = list(pool.map(fetch, items))
(ROOT/'research.json').write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding='utf-8')
(ROOT/'sources.json').write_text(json.dumps([{k:v for k,v in row.items() if k!='body'} for row in records], ensure_ascii=False, indent=2), encoding='utf-8')
for row in records: print(row['repository'], row['path'], row.get('error', row.get('text_characters')))
print('SEARCH:', json.dumps(search))
