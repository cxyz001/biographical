"""Record GitHub searches and the upstream documentation actually read."""
import concurrent.futures
import datetime
import hashlib
import json
import pathlib
import urllib.parse
import urllib.request

ROOT = pathlib.Path(__file__).parent
SOURCES = [
 ('ros2/ros2_documentation','rolling','source/Tutorials/Beginner-CLI-Tools/Understanding-ROS2-Topics/Understanding-ROS2-Topics.rst'),
 ('ros2/ros2_documentation','rolling','source/Concepts/Intermediate/About-Quality-of-Service-Settings.rst'),
 ('ros2/ros2_documentation','rolling','source/Tutorials/Intermediate/Tf2/Introduction-To-Tf2.rst'),
 ('ros-controls/ros2_control','master','README.md'),
 ('ros-navigation/navigation2','main','README.md'),
 ('moveit/moveit2','main','README.md'),
 ('gazebosim/gz-sim','gz-sim9','README.md'),
 ('ruckig/ruckig','main','README.md'),
 ('OpenEtherCATsociety/SOEM','master','README.md'),
 ('linux-can/can-utils','master','README.md'),
 ('pymodbus-dev/pymodbus','dev','README.rst'),
 ('FreeRTOS/FreeRTOS-Kernel','main','README.md'),
 ('kicad/kicad-doc','master','README.adoc'),
 ('ngspice/ngspice','master','README'),
 ('OpenEnergyMonitor/emonlib','master','README.md'),
 ('EVerest/everest-core','main','README.md'),
 ('EVerest/libocpp','main','README.md'),
 ('OpenEVSE/open_evse','master','README.md'),
 ('Klipper3d/klipper','master','docs/Overview.md'),
 ('pyvisa/pyvisa','main','README.rst'),
]

def get(url):
    req=urllib.request.Request(url,headers={'User-Agent':'robot-hardware-learning'})
    with urllib.request.urlopen(req,timeout=18) as response:
        return response.read().decode('utf-8')

def read(item):
    repo,branch,path=item
    record=dict(repository=repo,branch=branch,path=path,date=str(datetime.date.today()),url=f'https://github.com/{repo}/blob/{branch}/{path}')
    try:
        body=get(f'https://raw.githubusercontent.com/{repo}/{branch}/{path}')
        record.update(characters=len(body),sha256=hashlib.sha256(body.encode()).hexdigest())
        lines=body.splitlines()
        words=['QoS','reliab','frame','topic','velocity','acceleration','jerk','license','License','safety','Safety','simulation','OCPP','calibrat','real-time','instrument','query(']
        selected=set(range(min(15,len(lines))))
        for i,line in enumerate(lines):
            if any(word in line for word in words):
                selected.update(range(max(0,i-1),min(len(lines),i+3)))
        return record,'\n'.join(f'{i+1}: {lines[i]}' for i in sorted(selected))[:4800]
    except Exception as exc:
        return dict(record,error=str(exc)),''

if __name__=='__main__':
    searches=[]
    for query in ['ros2 control navigation','robot trajectory ruckig','kicad hardware design','EV charging EVerest','ocpp charge point','pyvisa instruments']:
        try:
            data=json.loads(get('https://api.github.com/search/repositories?q='+urllib.parse.quote(query)+'&per_page=2'))
            searches.append(dict(query=query,results=[dict(repository=x['full_name'],url=x['html_url']) for x in data['items']]))
        except Exception as exc:
            searches.append(dict(query=query,error=str(exc)))
    (ROOT/'search-results.json').write_text(json.dumps(searches,ensure_ascii=False,indent=2),encoding='utf-8')
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
        results=list(pool.map(read,SOURCES))
    (ROOT/'sources.json').write_text(json.dumps([r for r,b in results],ensure_ascii=False,indent=2),encoding='utf-8')
    for record,excerpt in results:
        print(record['repository'],record.get('error','OK'))
        print(excerpt)
