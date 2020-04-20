from datetime import datetime
import dbus
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
    self.intf = None            # D-bus interface
    self.bus = None
    self.qxdm_process = None
    self.vdisplay = None


  def launch(self):
    self.vdisplay = Xvfb(width=2, height=2, colordepth=8)
    self.vdisplay.start()

    self.bus = dbus.SessionBus()

    # start QXDM process
    self.qxdm_process = Popen(QXDM.PROCESS_PATH)
    print("QXDM launched")
    sleep(5)    # must wait until D-bus is available

    # connect to D-bus session
    self.bus = dbus.SessionBus()


  def get_session(self):
    obj = self.bus.get_object(QXDM.PROG_NAME, QXDM.OBJ_PATH)
    self.intf = dbus.Interface(obj, QXDM.INTF_NAME)
    session = obj.getQXDMSession(False)
    
    SetVisible = self.intf.get_dbus_method('SetVisible')
    SetVisible(False, session)

    print('QXDM session :', session)
    print('QXDM version :', obj.AppVersion())
    return session


  def connect(self, session, port_number):
    ConnectDevice = self.intf.get_dbus_method('ConnectDevice')
    GetConnectionState = self.intf.get_dbus_method('GetConnectionState')
    ConnectDevice(port_number, session)
    # Wait until DIAG server state transitions to connected
    # (we do this for up to five seconds)
    wait_count = 0
    server_state = QXDM.SERVER_DISCONNECTED
    while server_state != QXDM.SERVER_CONNECTED and wait_count < 5:
      sleep(1)
      server_state = GetConnectionState(session)
      wait_count += 1
    
    if server_state == QXDM.SERVER_CONNECTED:
      print(f'{session} connected to device {port_number}')
      self.port = port_number
      return True
    else:
      print(f'{session} unable to connect to device {port_number}')
      self.port = None
      return False


  def disconnect(self, session):
    DisconnectDevice = self.intf.get_dbus_method('DisconnectDevice')
    GetConnectionState = self.intf.get_dbus_method('GetConnectionState')

    DisconnectDevice(session)
    # wait until DIAG server state transitions to disconnected
    # (we do this for up to five seconds)
    wait_count = 0
    server_state = QXDM.SERVER_CONNECTED
    while server_state != QXDM.SERVER_DISCONNECTED and wait_count < 5:
      sleep(1)
      server_state = GetConnectionState(session)
      wait_count += 1

    if server_state == QXDM.SERVER_DISCONNECTED:
      print('QXDM successfully disconnected')
      self.port = None
      return True
    else:
      print('QXDM unable to disconnect')
      return False


  def start_logs(self, session):
    SaveItemStore = self.intf.get_dbus_method('SaveItemStore')

    now = datetime.now()
    path = f'{os.getcwd()}/temp/temp_{now.strftime("%y%m%d_%H%M%S_%f")}.isf'
    print(path)
    SaveItemStore(path, session)
    os.remove(path)
    print('QXDM Start Logs - New logs started')


  def save_logs(self, session, folder_path, log_name):
    SaveItemStore = self.intf.get_dbus_method('SaveItemStore')

    path = folder_path + '/' + log_name + '.isf'
    print("Path of isf file : ", path)
    SaveItemStore(path, session)
    print('QXDM Save Logs - Log saved :', path)


  def quit(self, session):
    QuitApplication = self.intf.get_dbus_method('QuitApplication')

    QuitApplication(session)
    # close before terminating otherwise next time doesn't work
    self.bus.close()
    # self.terminate_processes()
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