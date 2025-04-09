import shutil
import time
import os
import requests
import subprocess
import psutil
import json
import warnings
import contextlib
from datetime import datetime
from obswebsocket import obsws, requests as obswsRequests  # noqa: E402
from urllib3.exceptions import InsecureRequestWarning
from tqdm import tqdm
import getpass

old_merge_environment_settings = requests.Session.merge_environment_settings


@contextlib.contextmanager
def no_ssl_verification():
    opened_adapters = set()

    def merge_environment_settings(self, url, proxies, stream, verify, cert):
        # Verification happens only once per connection so we need to close
        # all the opened adapters once we're done. Otherwise, the effects of
        # verify=False persist beyond the end of this context manager.
        opened_adapters.add(self.get_adapter(url))

        settings = old_merge_environment_settings(self, url, proxies, stream, verify, cert)
        settings['verify'] = False

        return settings

    requests.Session.merge_environment_settings = merge_environment_settings

    try:
        with warnings.catch_warnings():
            warnings.simplefilter('ignore', InsecureRequestWarning)
            yield
    finally:
        requests.Session.merge_environment_settings = old_merge_environment_settings

        for adapter in opened_adapters:
            try:
                adapter.close()
            except Exception as e:
                # print('Error :'e)
                pass


def is_process_running(process_name):
    for proc in psutil.process_iter(attrs=['name']):
        if proc.info['name'] and process_name.lower() in proc.info['name'].lower():
            return True
    return False


DETACHED_PROCESS = 0x00000008
CREATE_NEW_PROCESS_GROUP = 0x00000200

obspath = ''

if not os.path.exists(r"C:\Program Files\obs-studio\bin\64bit"):
    if input("Is OBS installed ? y/n") == 'y':
        obspath = input('Where is OBS installed ? example : "C:\\Program Files\\obs-studio\\bin\\64bit"')
    else:
        if input("Do you want me to install and setup your OBS ? y/n") == 'y':
            url = 'https://cdn-fastly.obsproject.com/downloads/OBS-Studio-31.0.2-Windows-Installer.exe'
            # Streaming, so we can iterate over the response.
            response = requests.get(url, stream=True)
            filepath = 'OBS_installer.exe'

            # Sizes in bytes.
            total_size = int(response.headers.get("content-length", 0))
            block_size = 1024

            with tqdm(total=total_size, unit="B", unit_scale=True) as progress_bar:
                with open(filepath, "wb") as file:
                    for data in response.iter_content(block_size):
                        progress_bar.update(len(data))
                        file.write(data)

            if total_size != 0 and progress_bar.n != total_size:
                raise RuntimeError("Could not download file")
            else:
                supress_auto_configuration_wizard = '[General]\nFirstRun=true'
                with open("global.ini", "w") as text_file:
                    text_file.write(supress_auto_configuration_wizard)
                process = subprocess.Popen(
                    ['xcopy', '.\\global.ini', '%appdata%\\obs-studio\\', '/y'],
                    stdin=subprocess.DEVNULL,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    shell=True
                )
                process.wait()
                print('Installing OBS')
                process = subprocess.Popen(
                    [filepath, "/S"],
                    stdin=subprocess.DEVNULL,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    shell=True
                )
                process.wait()
                print('OBS is installed')
                if os.path.exists('global.ini'):
                    os.remove('global.ini')

        else:
            if input("Do you want to install OBS yourself ? y/n") == 'y':
                input('Send anything when OBS is installed')
            if input("Do you want to create an OBS scene for league of legends by yourself ? y/n") == 'n':
                print('preparing a scene for you')

# "C:\Users\%USERNAME%\AppData\Roaming\obs-studio\plugin_config\obs-websocket\config.json"

host = "127.0.0.1"

if os.path.exists(
        r"C:\Users\{0}\AppData\Roaming\obs-studio\plugin_config\obs-websocket\config.json".format(getpass.getuser())):
    is_obs_websocket_enable = True
    with open(r"C:\Users\{0}\AppData\Roaming\obs-studio\plugin_config\obs-websocket\config.json".format(
            getpass.getuser())) as file:
        data = json.load(file)
        password = data['server_password']
        port = data['server_port']
        is_obs_websocket_enable = data['server_enabled']
    if not is_obs_websocket_enable:
        data['server_enabled'] = True
        with open(r"C:\Users\{0}\AppData\Roaming\obs-studio\plugin_config\obs-websocket\config.json".format(
                getpass.getuser()), encoding='utf8') as file:
            json.dump(data, file)

path_to_json = "C:\\Users\\{0}\\AppData\\Roaming\\obs-studio\\basic\scenes\\".format(getpass.getuser())
scenes_file = [pos_json for pos_json in os.listdir(path_to_json) if pos_json.endswith('.json')]

if os.path.exists(path_to_json):
    for file in scenes_file:
        with open(path_to_json + file, encoding='utf8') as json_file:
            data = json.load(json_file)
            uuids = []
            scenes_name = []
            for source in data['sources']:
                try:
                    if source['settings']['window'] == "League of Legends (TM) Client:RiotWindowClass:League of Legends.exe":
                        uuids += [source['uuid']]
                        #print(source['uuid'])
                except Exception as e:
                    #print('Error :', e)
                    pass
            for source in data['sources']:
                if source['id'] == 'scene' and source['uuid'] in uuids:
                    scenes_name += source['name']

# Check if OBS Studio is running
if is_process_running("obs"):
    print("OBS Studio is already running skipping it start.")
else:
    process = subprocess.Popen([
        "obs64.exe", "--minimize-to-tray", "--disable-shutdown-check", "--disable-updater",
        "--scene", '"' + scenes_file[len(scenes_file)-1] + '"'],
        # --scene "League of legends automatic"
        cwd=r"C:\Program Files\obs-studio\bin\64bit",
        shell=True,
        creationflags=DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    print("OBS launched in the background.")
    while not is_process_running("obs"):
        time.sleep(1)

# "C:\Users\%USERNAME%\AppData\Roaming\obs-studio\basic\scenes\Sans nom.json"


ws = obsws(host, port, password)
obsWebSocketConnected = False
while not obsWebSocketConnected:
    try:
        ws.connect()
        obsWebSocketConnected = True
    except Exception as e:
        # print("An error occurred:", e)
        time.sleep(1)
        obsWebSocketConnected = False


def isInGame():
    inGame = False
    if is_process_running('League of Legends.exe'):
        try:
            with no_ssl_verification():
                response = requests.get('https://127.0.0.1:2999/liveclientdata/allgamedata', verify=False)
                gameJson = response.json()
                for event in gameJson['events']['Events']:
                    if event['EventName'] == 'GameStart':
                        inGame = True
        except Exception as e:
            # print("An error occurred:", e)
            inGame = False
        return inGame


time.sleep(5)

try:
    scenes = ws.call(obswsRequests.GetSceneList())
    for s in scenes.getScenes():
        name = s['sceneName']
        if name == 'League of legends automatic' or name in scenes_name:
            print("Switching to scene {}".format(name))
            ws.call(obswsRequests.SetCurrentProgramScene(sceneName=name))
            break
except KeyboardInterrupt:
    pass


def waitForGame():
    isGameStarted = False
    while not isGameStarted:
        # print('game not found :'+str(isGameStarted))
        time.sleep(1)
        isGameStarted = isInGame()


gameData = ''

while True:
    print('Waiting for a game to start')
    if not isInGame():
        waitForGame()
    print('Game started')
    gameStartTime = str(time.time())
    ws.call(obswsRequests.StartRecord())
    videoFileName = datetime.now().strftime('%Y-%m-%d %H-%M-%S')

    while isInGame():
        try:
            with no_ssl_verification():
                gameData = requests.get('https://127.0.0.1:2999/liveclientdata/allgamedata', verify=False).json()
                with open(gameStartTime + ".json", "w") as f:
                    json.dump(gameData, f, indent=4)
        except Exception as e:
            # print("An error occurred:", e)
            test = ''
        time.sleep(1)

    print('Game ended')
    ws.call(obswsRequests.StopRecord())

    response = ws.call(obswsRequests.GetRecordDirectory())
    record_dir = response.getRecordDirectory()  # or response.response['recordDirectory']
    os.makedirs('records\\' + videoFileName, exist_ok=True)

    while True:
        if os.path.exists('records\\' + videoFileName + '\\' + gameStartTime + '.json'):
            break
        try:
            shutil.move(gameStartTime + '.json', 'records\\' + videoFileName)
        except Exception as e:
            fileMoved = False

    while True:
        if os.path.exists('records\\' + videoFileName + '\\' + videoFileName + '.mp4'):
            break
        try:
            shutil.move(record_dir + '\\' + videoFileName + '.mp4', 'records\\' + videoFileName)
            break
        except Exception as e:
            fileMoved = False

    print('Files moved')

    if os.path.exists(record_dir + '\\' + videoFileName + '.mp4') and \
            os.path.exists('records\\' + videoFileName + '\\' + videoFileName + '.mp4'):
        while os.path.exists(record_dir + '\\' + videoFileName + '.mp4'):
            try:
                os.remove(record_dir + '\\' + videoFileName + '.mp4')
            except Exception as e:
                print('Error :' + e)
                time.sleep(1)

    chapters = ''

    script_dir = os.path.dirname(os.path.abspath(__file__))
    script_dir += '/records/' + videoFileName + '/'

    print('Retrieve video file metadata')
    process = subprocess.Popen(
        ['ffmpeg', '-y', '-i', videoFileName + '.mp4', '-f', 'ffmetadata', 'FFMETADATAFILE'],
        cwd=script_dir, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT
    )
    process.wait()
    time.sleep(1)
    filename = 'FFMETADATAFILE'

    # Wait for the file to exist
    while not os.path.exists(script_dir + filename):
        print(f"Waiting for {filename} to be created...")
        time.sleep(1)  # Check every second

    with open(script_dir + filename, 'r', encoding='utf-8') as file:
        chapters = file.read()
        chapters += '\n'

    print('Generating chapters')
    with open('records/' + videoFileName + '/' + gameStartTime + '.json', 'r') as file:
        data = json.load(file)
        riotIdGameName = data['activePlayer']['riotIdGameName']
        for event in data['events']['Events']:
            if event['EventName'] in ['ChampionKill']:
                # firstblood, gamestart, minions spawn, game End, turret destroyed...
                if event['KillerName'] == riotIdGameName or event['VictimName'] == riotIdGameName or riotIdGameName in \
                        event['Assisters']:
                    chapters += '[CHAPTER]\n'
                    chapters += 'TIMEBASE=1/1000\n'
                    chapters += 'START=' + str(int(str(event['EventTime']).split('.')[0]) - 10) + '000' + '\n'
                    chapters += 'END=' + str(int(str(event['EventTime']).split('.')[0]) + 5) + '000' + '\n'
                    chapters += 'title=' + event['KillerName'].strip() + ' killed ' + event['VictimName'].strip() + '\n'
                    chapters += '\n'

    with open("records/" + videoFileName + "/chapters.txt", "w", encoding="utf-8") as text_file:
        text_file.write(chapters)
    # print('ffmpeg -i "2025-04-04 23-16-29.mp4" -i chapters.txt -map_metadata 1 -codec copy chaptered.mp4')

    print('Embed chapters in video')
    process = subprocess.Popen(
        ['ffmpeg', '-i', videoFileName + '.mp4', '-i', 'chapters.txt', '-map_metadata', '1', '-codec', 'copy',
         'chaptered.mp4'],
        cwd=script_dir, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT
    )
    process.wait()
    time.sleep(1)

    if os.path.exists(script_dir + videoFileName + '.mp4'):
        os.remove(script_dir + videoFileName + '.mp4')
        if os.path.exists(script_dir + 'chaptered.mp4'):
            if not os.path.exists(script_dir + videoFileName + '.mp4'):
                os.rename(script_dir + 'chaptered.mp4', script_dir + videoFileName + '.mp4')

ws.disconnect()
