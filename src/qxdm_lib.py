import datetime
import os
import subprocess
import time
import traceback
import collections
import dataclasses
import pathlib

import psutil
from pydbus import SessionBus

_BASE_PATH = pathlib.Path(__file__).parent.resolve()
_TEMP_FOLDER_PATH = (_BASE_PATH.parent / 'temp')

"""
A running QXDM process is abstracted by a QXDM object which launches a QXDM process and keeps track of the process and active sessions in a dictionary of (key: ports, values: Session).

Library users should check process_running() before any other library functions, otherwise a NotRunningException will be thrown if the QXDM process is not running.
"""

@dataclasses.dataclass
class Session:
  '''Class for keeping track of QXDM sessions'''
  session_id: str
  port: int = None
  logging: bool = False

class NotRunningException(Exception):
  pass

class QXDM:
  # DIAG server states
  SERVER_DISCONNECTED = 0
  SERVER_CONNECTED = 1

  PROCESS_PATH = '/opt/qcom/QXDM/QXDM'    # path to QXDM binary
  PROG_NAME = 'com.qcom.QXDM'
  OBJ_PATH = '/QXDMDbusServer'
  INTF_NAME = PROG_NAME


  def __init__(self):
    self.sessions = collections.defaultdict(Session)
    self.process = None
    self.bus = None
    self.qxdm = None  # qxdm dbus object

    self._launch()


  def _launch(self):
    # start QXDM process
    self.process = subprocess.Popen(QXDM.PROCESS_PATH)
    print("QXDM launched")
    self.bus = SessionBus()
    time.sleep(7)    # must wait until D-bus is available
    self.qxdm = self.bus.get(QXDM.PROG_NAME, QXDM.OBJ_PATH)


  def process_running(self) -> bool:
    '''Returns false if process doesn't exist or is a zombie'''
    if not psutil.pid_exists(self.process.pid):
      return False
    return psutil.Process(self.process.pid).status() != psutil.STATUS_ZOMBIE


  def _get_new_session(self) -> Session:
    if not self.process_running():
      raise NotRunningException('QXDM is not running.')

    session_id = self.qxdm.getQXDMSession(True)
    self.qxdm.SetVisible(False, session_id)

    print('QXDM session :', session_id)
    # print('QXDM version :', qxdm.AppVersion())
    return Session(session_id)


  def connect(self, port: int) -> bool:
    try:
      """
      A new session should be retrieved with qxdm.getQXDMSession(True) before each connect attempt.  If multiple sessions are retrieved before a connect attempt, then only the last session is able to connect.
      """
      session = self._get_new_session()
    except Exception:
      raise
    
    self.qxdm.ConnectDevice(port, session.session_id)
    # Wait until DIAG server state transitions to connected
    # (we do this for up to five seconds)
    wait_count = 0
    server_state = QXDM.SERVER_DISCONNECTED
    while server_state != QXDM.SERVER_CONNECTED and wait_count < 5:
      time.sleep(1)
      server_state = self.qxdm.GetConnectionState(session.session_id)
      wait_count += 1
    
    if server_state == QXDM.SERVER_CONNECTED:
      print(f'{session.session_id} connected to device: {port}')
      session.port = port
      self.sessions[port] = session
      return True
    else:
      print(f'{session.session_id} unable to connect to device: {port}')
      return False


  def disconnect(self, port: int) -> bool:
    session = self.sessions[port]
    # if port is not connected ...
    if not session:
      print('Could not find connected port')
      return

    self.qxdm.DisconnectDevice(session.session_id)
    # wait until DIAG server state transitions to disconnected
    # (we do this for up to five seconds)
    wait_count = 0
    server_state = QXDM.SERVER_CONNECTED
    while server_state != QXDM.SERVER_DISCONNECTED and wait_count < 5:
      time.sleep(1)
      server_state = self.qxdm.GetConnectionState(session.session_id)
      wait_count += 1

    if server_state == QXDM.SERVER_DISCONNECTED:
      print(f'{session.session_id} disconnected from device: {session.port}')
      session.port = None
      self.sessions.pop(port)
      return True
    else:
      print(f'{session.session_id} unable to disconnect from device: {session.port}')
      return False


  def start_logs(self, port: int) -> None:
    session = self.sessions[port]
    # if port is not connected ...
    if not session:
      print('Could not find connected port')
      return

    now = datetime.datetime.now()
    path = f'{_TEMP_FOLDER_PATH}/temp_{now.strftime("%y%m%d_%H%M%S_%f")}.isf'
    self.qxdm.SaveItemStore(path, session.session_id)
    os.remove(path)
    session.logging = True
    print(f'{session.session_id} Start Logs - New logs started')


  def save_logs(self, port: int) -> str:
    session = self.sessions[port]
    # if port is not connected ...
    if not session:
      print('Could not find connected port')
      return
    
    now = datetime.datetime.now()
    path = f'{_TEMP_FOLDER_PATH}/log_{now.strftime("%y%m%d_%H%M%S_%f")}_{port}.isf'

    self.qxdm.SaveItemStore(path, session.session_id)
    session.logging = False
    print(f'{session.session_id} Save Logs - Log saved : {path}')
    return path


  def quit(self) -> None:
    try:
      session = self._get_new_session()
      self.qxdm.QuitApplication(session.session_id)
    except Exception:
      self.proc.terminate()
    
    self.process = None
    print('QXDM Quit - QXDM Closed')

  
  def is_connected(self, port: int) -> bool:
    return port in self.sessions
  
  
  def is_logging(self, port: int) -> bool:
    if port in self.sessions:
      return self.sessions[port].logging
    return False
