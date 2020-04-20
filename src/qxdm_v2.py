from datetime import datetime
import dbus
import os
import subprocess
from time import sleep
from xvfbwrapper import Xvfb
import traceback
from random import randint

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
    self.qxdm_process_pid = None
    self.xvfb_process_pid = None
    self.session = None

  # def launch(self):
  #   self.vdisplay = Xvfb(width=2, height=2, colordepth=8)
  #   self.vdisplay.start()
    
  #   # connect to D-bus session
  #   # self.bus = dbus.SessionBus()
  #   sleep(2)

  #   self.session = "QXDM1"
  #   print('QXDM session :', self.session)
  #   print('bus :', self.bus)

  
  # def connect(self, port_number):
  #   self.port = port_number
  #   print('QXDM connected to device', port_number)
  #   return True

  # def disconnect(self):
  #   self.port = None
  #   print('QXDM successfully disconnected')
  #   return True
  
  # def quit(self):
  #   # close before terminating otherwise next time doesn't work
  #   self.bus.close()
  #   self.vdisplay.stop()
  #   print('QXDM Quit - QXDM Closed')


  def launch(self):
    # start Xvfb server and set DISPLAY env to server's
    disp = randint(10000, 20000)
    xvfb_process = subprocess.Popen(f'Xvfb :{disp} -screen 0 2x2x8'.split(' '))
    self.xvfb_process_pid = xvfb_process.pid
    os.environ['DISPLAY'] = f':{disp}'

    sleep(1)

    bus = dbus.SessionBus()

    # start QXDM process
    qxdm_process = subprocess.Popen(QXDM.PROCESS_PATH)
    self.qxdm_process_pid = qxdm_process.pid
    print("QXDM launched")
    sleep(5)    # must wait until D-bus is available

    # connect to D-bus session
    bus = dbus.SessionBus()
    obj = bus.get_object(QXDM.PROG_NAME, QXDM.OBJ_PATH)
    intf = dbus.Interface(obj, QXDM.INTF_NAME)

    self.session = obj.getQXDMSession(False)
    
    SetVisible = intf.get_dbus_method('SetVisible')
    SetVisible(False, self.session)

    print('QXDM session :', self.session)
    print('QXDM version :', obj.AppVersion())



  def connect(self, port_number):
    bus = dbus.SessionBus()
    obj = bus.get_object(QXDM.PROG_NAME, QXDM.OBJ_PATH)
    intf = dbus.Interface(obj, QXDM.INTF_NAME)

    ConnectDevice = intf.get_dbus_method('ConnectDevice')
    GetConnectionState = intf.get_dbus_method('GetConnectionState')
    ConnectDevice(port_number, self.session)
    # Wait until DIAG server state transitions to connected
    # (we do this for up to five seconds)
    wait_count = 0
    server_state = QXDM.SERVER_DISCONNECTED
    while server_state != QXDM.SERVER_CONNECTED and wait_count < 5:
      sleep(1)
      server_state = GetConnectionState(self.session)
      wait_count += 1
    
    if server_state == QXDM.SERVER_CONNECTED:
      print(f'{self.session} connected to device {port_number}')
      self.port = port_number
      return True
    else:
      print(f'{self.session} unable to connect to device {port_number}')
      self.port = None
      return False


  def disconnect(self):
    bus = dbus.SessionBus()
    obj = bus.get_object(QXDM.PROG_NAME, QXDM.OBJ_PATH)
    intf = dbus.Interface(obj, QXDM.INTF_NAME)

    DisconnectDevice = intf.get_dbus_method('DisconnectDevice')
    GetConnectionState = intf.get_dbus_method('GetConnectionState')

    DisconnectDevice(self.session)
    # wait until DIAG server state transitions to disconnected
    # (we do this for up to five seconds)
    wait_count = 0
    server_state = QXDM.SERVER_CONNECTED
    while server_state != QXDM.SERVER_DISCONNECTED and wait_count < 5:
      sleep(1)
      server_state = GetConnectionState(self.session)
      wait_count += 1

    if server_state == QXDM.SERVER_DISCONNECTED:
      print('QXDM successfully disconnected')
      self.port = None
      return True
    else:
      print('QXDM unable to disconnect')
      return False


  def start_logs(self):
    bus = dbus.SessionBus()
    obj = bus.get_object(QXDM.PROG_NAME, QXDM.OBJ_PATH)
    intf = dbus.Interface(obj, QXDM.INTF_NAME)

    SaveItemStore = intf.get_dbus_method('SaveItemStore')

    now = datetime.now()
    path = f'{os.getcwd()}/temp/temp_{now.strftime("%y%m%d_%H%M%S_%f")}.isf'
    print(path)
    SaveItemStore(path, self.session)
    os.remove(path)
    print('QXDM Start Logs - New logs started')


  def save_logs(self, folder_path, log_name):
    bus = dbus.SessionBus()
    obj = bus.get_object(QXDM.PROG_NAME, QXDM.OBJ_PATH)
    intf = dbus.Interface(obj, QXDM.INTF_NAME)

    SaveItemStore = intf.get_dbus_method('SaveItemStore')

    path = folder_path + '/' + log_name + '.isf'
    print("Path of isf file : ", path)
    SaveItemStore(path, self.session)
    print('QXDM Save Logs - Log saved :', path)


  def quit(self):
    bus = dbus.SessionBus()
    obj = bus.get_object(QXDM.PROG_NAME, QXDM.OBJ_PATH)
    intf = dbus.Interface(obj, QXDM.INTF_NAME)

    QuitApplication = intf.get_dbus_method('QuitApplication')
    print(self.qxdm_process_pid, self.xvfb_process_pid)

    try:
      QuitApplication(self.session)
      subprocess.Popen(f'kill {self.xvfb_process_pid}'.split())
    except Exception as e:
      subprocess.Popen(f'kill {self.qxdm_process_pid}'.split())

    # close before terminating otherwise next time doesn't work
    bus.close()
    print('QXDM Quit - QXDM Closed')


  def port_switch(self, port_number):
    self.disconnect()
    self.connect(port_number)




# qxdm = QXDM()
# try:
#   qxdm.launch()
#   # qxdm.connect(5)
#   # qxdm.start_logs()
#   sleep(3)
#   # qxdm.save_logs('/home/techm/temp', 'test')
#   # sleep(2)
#   qxdm.quit()
# except Exception as ex:
#   qxdm.terminate_processes()
#   traceback.print_exception(type(ex), ex, ex.__traceback__)
