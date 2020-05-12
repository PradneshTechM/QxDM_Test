import datetime
import os
import subprocess
import time
import traceback
import collections
import dataclasses
import pathlib

from pydbus import SessionBus

_BASE_PATH = pathlib.Path(__file__).parent.resolve()
_TEMP_FOLDER_PATH = (_BASE_PATH.parent / 'temp')

@dataclasses.dataclass
class Session:
  '''Class for keeping track of QXDM sessions'''
  session_id: str
  port: int = None
  logging: bool = False


class QXDM(object):
  # DIAG server states
  SERVER_DISCONNECTED = 0
  SERVER_CONNECTED = 1

  PROCESS_PATH = '/opt/qcom/QXDM/QXDM'    # path to QXDM binary
  PROG_NAME = 'com.qcom.QXDM'
  OBJ_PATH = '/QXDMDbusServer'
  INTF_NAME = PROG_NAME


  def __init__(self):
    self.sessions = collections.defaultdict(Session)
    self.process_pid = None

    self._launch()


  def _launch(self):
    # start QXDM process
    qxdm_process = subprocess.Popen(QXDM.PROCESS_PATH)
    self.process_pid = qxdm_process.pid
    print("QXDM launched")
    time.sleep(5)    # must wait until D-bus is available


  def _get_new_session(self, bus):
    qxdm = bus.get(QXDM.PROG_NAME, QXDM.OBJ_PATH)
    session_id = qxdm.getQXDMSession(True)
    qxdm.SetVisible(False, session_id)

    print('QXDM session :', session_id)
    # print('QXDM version :', qxdm.AppVersion())
    return Session(session_id)


  def connect(self, port):
    bus = SessionBus()
    session = self._get_new_session(bus)

    qxdm = bus.get(QXDM.PROG_NAME, QXDM.OBJ_PATH)
    
    qxdm.ConnectDevice(port, session.session_id)
    # Wait until DIAG server state transitions to connected
    # (we do this for up to five seconds)
    wait_count = 0
    server_state = QXDM.SERVER_DISCONNECTED
    while server_state != QXDM.SERVER_CONNECTED and wait_count < 5:
      time.sleep(1)
      server_state = qxdm.GetConnectionState(session.session_id)
      wait_count += 1
    
    if server_state == QXDM.SERVER_CONNECTED:
      print(f'{session.session_id} connected to device: {port}')
      session.port = port
      self.sessions[port] = session
      return True
    else:
      print(f'{session.session_id} unable to connect to device: {port}')
      return False


  def disconnect(self, port):
    session = self.sessions[port]
    # if port is not connected ...
    if not session:
      print('Could not find connected port')
      return

    bus = SessionBus()
    qxdm = bus.get(QXDM.PROG_NAME, QXDM.OBJ_PATH)

    qxdm.DisconnectDevice(session.session_id)
    # wait until DIAG server state transitions to disconnected
    # (we do this for up to five seconds)
    wait_count = 0
    server_state = QXDM.SERVER_CONNECTED
    while server_state != QXDM.SERVER_DISCONNECTED and wait_count < 5:
      time.sleep(1)
      server_state = qxdm.GetConnectionState(session.session_id)
      wait_count += 1

    if server_state == QXDM.SERVER_DISCONNECTED:
      print(f'{session.session_id} disconnected from device: {session.port}')
      session.port = None
      self.sessions.pop(port)
      return True
    else:
      print(f'{session.session_id} unable to disconnect from device: {session.port}')
      return False


  def start_logs(self, port):
    session = self.sessions[port]
    # if port is not connected ...
    if not session:
      print('Could not find connected port')
      return

    bus = SessionBus()
    qxdm = bus.get(QXDM.PROG_NAME, QXDM.OBJ_PATH)

    now = datetime.datetime.now()
    path = f'{_TEMP_FOLDER_PATH}/temp_{now.strftime("%y%m%d_%H%M%S_%f")}.isf'
    qxdm.SaveItemStore(path, session.session_id)
    os.remove(path)
    session.logging = True
    print(f'{session.session_id} Start Logs - New logs started')


  def save_logs(self, port):
    session = self.sessions[port]
    # if port is not connected ...
    if not session:
      print('Could not find connected port')
      return

    bus = SessionBus()
    qxdm = bus.get(QXDM.PROG_NAME, QXDM.OBJ_PATH)
    
    now = datetime.datetime.now()
    path = f'{_TEMP_FOLDER_PATH}/log_{now.strftime("%y%m%d_%H%M%S_%f")}_{port}.isf'

    qxdm.SaveItemStore(path, session.session_id)
    session.logging = False
    print(f'{session.session_id} Save Logs - Log saved : {path}')
    return path


  def quit(self):
    bus = SessionBus()
    qxdm = bus.get(QXDM.PROG_NAME, QXDM.OBJ_PATH)

    try:
      session = self._get_new_session(bus)
      qxdm.QuitApplication(session.session_id)
    except Exception:
      subprocess.Popen(f'kill {self.process_pid}'.split())
    
    print('QXDM Quit - QXDM Closed')

  
  def is_connected(self, port):
    return port in self.sessions
  
  
  def is_logging(self, port):
    if port in self.sessions:
      return self.sessions[port].logging
    return False
