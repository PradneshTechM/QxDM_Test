from datetime import datetime
from pydbus import SessionBus
import os
from subprocess import Popen
from time import sleep
from xvfbwrapper import Xvfb
import traceback
import random

# xvfb: https://unix.stackexchange.com/a/105968

class QXDM(object):
  # DIAG server states
  SERVER_DISCONNECTED = 0
  SERVER_CONNECTED = 1

  PROCESS_PATH = '/opt/qcom/QXDM/QXDM'
  PROG_NAME = 'com.qcom.QXDM'
  OBJ_PATH = '/QXDMDbusServer'
  INTF_NAME = PROG_NAME

  def __init__(self):
    self.port = None
    self.session = None         # D-bus qxdm session
    self.qxdm_process_pid = None
    self.logging = False
    # self.xvfb_process_pid = None


  def launch(self):    
    # start Xvfb server and set DISPLAY env to server's
    # disp = random.randint(10000, 20000)
    # xvfb_process = Popen(f'Xvfb :{disp} -screen 0 2x2x8'.split(' '))
    # self.xvfb_process_pid = xvfb_process.pid
    # os.environ['DISPLAY'] = f':{disp}'

    sleep(2)

    bus = SessionBus()

    # start QXDM process
    qxdm_process = Popen(QXDM.PROCESS_PATH)
    self.qxdm_process_pid = qxdm_process.pid
    print("QXDM launched")
    sleep(5)    # must wait until D-bus is available

    qxdm = bus.get(QXDM.PROG_NAME, QXDM.OBJ_PATH)
    
    self.session = qxdm.getQXDMSession(True)
    qxdm.SetVisible(False, self.session)

    print('QXDM session :', self.session)
    # print('QXDM version :', qxdm.AppVersion())


  def connect(self, port_number):
    bus = SessionBus()
    qxdm = bus.get(QXDM.PROG_NAME, QXDM.OBJ_PATH)
    
    qxdm.ConnectDevice(port_number, self.session)
    # Wait until DIAG server state transitions to connected
    # (we do this for up to five seconds)
    wait_count = 0
    server_state = QXDM.SERVER_DISCONNECTED
    while server_state != QXDM.SERVER_CONNECTED and wait_count < 5:
      sleep(1)
      server_state = qxdm.GetConnectionState(self.session)
      wait_count += 1
    
    if server_state == QXDM.SERVER_CONNECTED:
      print(f'{self.session} connected to device: {port_number}')
      self.port = port_number
      return True
    else:
      print(f'{self.session} unable to connect to device: {port_number}')
      self.port = None
      return False


  def disconnect(self):
    bus = SessionBus()
    qxdm = bus.get(QXDM.PROG_NAME, QXDM.OBJ_PATH)

    qxdm.DisconnectDevice(self.session)
    # wait until DIAG server state transitions to disconnected
    # (we do this for up to five seconds)
    wait_count = 0
    server_state = QXDM.SERVER_CONNECTED
    while server_state != QXDM.SERVER_DISCONNECTED and wait_count < 5:
      sleep(1)
      server_state = qxdm.GetConnectionState(self.session)
      wait_count += 1

    if server_state == QXDM.SERVER_DISCONNECTED:
      print(f'{self.session} disconnected from device: {self.port}')
      self.port = None
      return True
    else:
      print(f'{self.session} unable to disconnect from device: {self.port}')
      return False


  def start_logs(self):
    bus = SessionBus()
    qxdm = bus.get(QXDM.PROG_NAME, QXDM.OBJ_PATH)

    now = datetime.now()
    path = f'{os.getcwd()}/temp/temp_{now.strftime("%y%m%d_%H%M%S_%f")}.isf'
    print(path)
    qxdm.SaveItemStore(path, self.session)
    os.remove(path)
    self.logging = True
    print('QXDM Start Logs - New logs started')


  def save_logs(self):
    bus = SessionBus()
    qxdm = bus.get(QXDM.PROG_NAME, QXDM.OBJ_PATH)
    
    now = datetime.now()
    path = f'{os.getcwd()}/temp/log_{now.strftime("%y%m%d_%H%M%S_%f")}.isf'

    print("Path of isf file : ", path)
    qxdm.SaveItemStore(path, self.session)
    self.logging = False
    print('QXDM Save Logs - Log saved :', path)
    return path


  def quit(self):
    bus = SessionBus()
    qxdm = bus.get(QXDM.PROG_NAME, QXDM.OBJ_PATH)

    try:
      qxdm.QuitApplication(self.session)
      # Popen(f'kill {self.xvfb_process_pid}'.split())
    except Exception as e:
      Popen(f'kill {self.qxdm_process_pid}'.split())
    
    print('QXDM Quit - QXDM Closed')


  def port_switch(self, port_number):
    self.disconnect()
    self.connect(port_number)
  
  def connected_to(self):
    return self.port
  
  def is_logging(self):
    return self.logging



# for _ in range(2):
#   qxdm = QXDM()
#   qxdm.launch()
#   sleep(2)
#   qxdm.connect(5)
#   sleep(2)
#   qxdm.quit()

  # qxdm.start_logs()
  # sleep(3)
  # qxdm.save_logs('/home/techm/temp', 'test')
  # sleep(2)
#   qxdm.quit()
# except Exception as ex:
#   qxdm.terminate_processes()
#   traceback.print_exception(type(ex), ex, ex.__traceback__)
