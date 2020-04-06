import logging
import threading
import time
import concurrent.futures
import sys

from qxdmUtils_new import QXDM

def thread_function(name, device_index):
  qxdm = QXDM()
  logging.info('Thread %s: launching QXDM', name)
  qxdm.launch()
  time.sleep(5)
  logging.info('Thread %s: connecting %s', name, device_index)
  qxdm.connect(device_index)
  logging.info('Thread %s: connected %s', name, device_index)
  time.sleep(5)
  qxdm.quit()


if __name__ == '__main__':
  format = '%(asctime)s: %(message)s'
  logging.basicConfig(format=format, level=logging.INFO, datefmt='%H:%M:%S')

  with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
    executor.map(thread_function, range(2), range(2))
