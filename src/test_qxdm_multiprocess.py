from multiprocessing import Pool
import logging
import threading
import time
import concurrent.futures
import sys
import os

from qxdmUtils_new import QXDM

def worker(name, device_index):
  qxdm = QXDM()
  logging.info('Process %s: launching QXDM', name)
  qxdm.launch()
  time.sleep(5)
  logging.info('Process %s: connecting %s', name, device_index)
  qxdm.connect(device_index)
  logging.info('Process %s: connected %s', name, device_index)
  time.sleep(5)
  qxdm.quit()

def get_pid():
  if hasattr(os, 'getppid')

if __name__ == '__main__':
  format = '%(asctime)s: %(message)s'
  logging.basicConfig(format=format, level=logging.INFO, datefmt='%H:%M:%S')

  p = Pool(2)
  p.map(worker, [0, 1], [0, 1])

  with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
    executor.map(thread_function, range(2), range(2))
