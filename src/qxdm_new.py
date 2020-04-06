from datetime import datetime
from pydbus import SessionBus
import os
from subprocess import Popen
from time import sleep
from xvfbwrapper import Xvfb
import traceback

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
    self.qxdm_process = None
    self.vdisplay = None
    self.qxdm = None


  def launch(self):
    self.vdisplay = Xvfb(width=2, height=2, colordepth=8)
    self.vdisplay.start()
    
    bus = SessionBus()

    # # start Xvfb server and set DISPLAY env to server's
    # self.xvfb_process = Popen('Xvfb :987 -screen 0 2x2x8'.split(' '))
    # os.environ['DISPLAY'] = ':987'

    # start QXDM process
    self.qxdm_process = Popen(QXDM.PROCESS_PATH)
    print("QXDM launched")
    sleep(5)    # must wait until D-bus is available

    self.qxdm = bus.get(QXDM.PROG_NAME, QXDM.OBJ_PATH)
    self.session = self.qxdm.getQXDMSession(False)

    self.qxdm.SetVisible(False, self.session)

    print('QXDM session :', self.session)
    print('QXDM version :', self.qxdm.AppVersion())


  def connect(self, port_number):
    self.qxdm.ConnectDevice(port_number, self.session)
    # Wait until DIAG server state transitions to connected
    # (we do this for up to five seconds)
    wait_count = 0
    server_state = QXDM.SERVER_DISCONNECTED
    while server_state != QXDM.SERVER_CONNECTED and wait_count < 5:
      sleep(1)
      server_state = self.qxdm.GetConnectionState(self.session)
      wait_count += 1
    
    if server_state == QXDM.SERVER_CONNECTED:
      print('QXDM connected to device', port_number)
      self.port = port_number
      return True
    else:
      print('QXDM unable to connect to device', port_number)
      self.port = None
      return False


  def disconnect(self):
    self.qxdm.DisconnectDevice(self.session)
    # wait until DIAG server state transitions to disconnected
    # (we do this for up to five seconds)
    wait_count = 0
    server_state = QXDM.SERVER_CONNECTED
    while server_state != QXDM.SERVER_DISCONNECTED and wait_count < 5:
      sleep(1)
      server_state = self.qxdm.GetConnectionState(self.session)
      wait_count += 1

    if server_state == QXDM.SERVER_DISCONNECTED:
      print('QXDM successfully disconnected')
      self.port = None
      return True
    else:
      print('QXDM unable to disconnect')
      return False


  def start_logs(self):
    now = datetime.now()
    path = f'{os.getcwd()}/temp/temp_{now.strftime("%y%m%d_%H%M%S_%f")}.isf'
    print(path)
    self.qxdm.SaveItemStore(path, self.session)
    os.remove(path)
    print('QXDM Start Logs - New logs started')


  def save_logs(self, folder_path, log_name):
    path = folder_path + '/' + log_name + '.isf'
    print("Path of isf file : ", path)
    self.qxdm.SaveItemStore(path, self.session)
    print('QXDM Save Logs - Log saved :', path)


  def quit(self):
    self.qxdm.QuitApplication(self.session)
    self.terminate_processes()
    self.vdisplay.stop()
    print('QXDM Quit - QXDM Closed')


  def terminate_processes(self):
    self.qxdm_process.terminate() 
    # self.xvfb_process.terminate()
    print('Terminated QXDM and Xvfb processes')


  def port_switch(self, port_number):
    self.disconnect()
    self.connect(port_number)




# qxdm = QXDM()
# try:
# qxdm.launch()
#   qxdm.connect(5)
#   qxdm.start_logs()
#   sleep(3)
#   qxdm.save_logs('/home/techm/temp', 'test')
#   sleep(2)
#   qxdm.quit()
# except Exception as ex:
#   qxdm.terminate_processes()
#   traceback.print_exception(type(ex), ex, ex.__traceback__)
