from datetime import datetime
import dbus
import os
from subprocess import Popen
from time import sleep
from xvfbwrapper import Xvfb
import traceback
import random

# xvfb: https://unix.stackexchange.com/a/105968

class QCAT(object):
  PROCESS_PATH = '/opt/qcom/QCAT/bin/QCAT'
  PROG_NAME = 'com.qcom.QCAT'
  OBJ_PATH = '/QCATDbusServer'
  INTF_NAME = PROG_NAME

  def __init__(self):
    self.port = None
    self.intf = None            # D-bus interface
    self.bus = None
    self.qcat_process = None
    self.vdisplay = None


  def launch(self):
    self.vdisplay = Xvfb(width=2, height=2, colordepth=8)
    self.vdisplay.start()

    self.bus = dbus.SessionBus()

    # start QCAT process
    value = (random.randrange(2**32 - 1) // 100 ) * 100
    self.qcat_process = Popen([QCAT.PROCESS_PATH, '-Automation', str(value)])
    print("QCAT launched")
    sleep(5)    # must wait until D-bus is available

    # connect to D-bus session
    self.bus = dbus.SessionBus()
    obj = self.bus.get_object(QCAT.PROG_NAME, f'{QCAT.OBJ_PATH}_{value}')
    self.intf = dbus.Interface(obj, QCAT.INTF_NAME)

    print('QCAT version :', obj.AppVersion())


  def quit(self):
    Quit = self.intf.get_dbus_method('Quit')

    Quit()
    # close before terminating otherwise next time doesn't work
    self.bus.close()   
    # self.terminate_processes()
    self.vdisplay.stop()
    print('QCAT Quit - QCAT Closed')


  def terminate_processes(self):
    self.qcat_process.terminate() 
    # self.xvfb_process.terminate()
    print('Terminated QCAT and Xvfb processes')


# qcat = QCAT()
# try:
# qcat.launch()
#   qcat.connect(5)
#   qcat.start_logs()
#   sleep(3)
#   qcat.save_logs('/home/techm/temp', 'test')
#   sleep(2)
#   qcat.quit()
# except Exception as ex:
#   qcat.terminate_processes()
#   traceback.print_exception(type(ex), ex, ex.__traceback__)
