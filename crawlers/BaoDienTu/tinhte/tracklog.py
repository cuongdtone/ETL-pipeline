import socketio
from bson.json_util import loads, dumps
from datetime import datetime
import time
import yaml
import os
yaml_file = open("settings.yaml")
cfg = yaml.load(yaml_file, Loader=yaml.FullLoader)
HOSTSOCKET = cfg["SOCKET"]["HOST"]
PORTSOCKET = cfg["SOCKET"]["PORT"]
URLSOCKET = cfg["SOCKET"]["URL"]
UNAME = os.popen("uname -n").read().strip()

class TrackLog:
    sio = socketio.Client(
        reconnection=True,
        reconnection_delay=1
    )
    try:
        sio.connect(URLSOCKET)
    except Exception as exc:
        print("Error connect socket: ", exc)

    @sio.event
    def connect(wait_timeout=1):
        print('Connection established')

    @sio.event
    def disconnect():
        print('Disconnected from server')

    def send(self, status, content):
        tracklog = {"ProcessType": "CRAWLDATA", "status" : status, "content" : (f"[{UNAME}]: " + content)}
        print(datetime.now(), tracklog)
        try:
            if self.sio.connected == True:
                self.sio.emit('PythonToNodejs', dumps(tracklog))
            else:
                self.reconnect()
                self.sio.emit('PythonToNodejs', dumps(tracklog))
        except Exception as e:
            print(f"Can't send tracklog : {str(e)}")

    def reconnect(self):
        if self.sio.connected == False:
            time.sleep(0.5)
            self.sio.connect(URLSOCKET)

    def disconnect(self):
        time.sleep(0.5)
        self.sio.disconnect()

tracklog = TrackLog()