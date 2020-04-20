from multiprocessing import Pool
import logging
import threading
import time
import concurrent.futures
import sys
import os

import pickle

from qxdm_new_v2 import QXDM

def worker(device_index):
  info('worker function')
  qxdm = QXDM()
  logging.info('launching QXDM %s', device_index)
  qxdm.launch()

  pickled_qxdm = pickle.dumps(qxdm)
  qxdm = None
  time.sleep(2)
  qxdm = pickle.loads(pickled_qxdm)

  logging.info('connecting %s', device_index)
  qxdm.connect(device_index)

  time.sleep(2)

  pickled_qxdm = pickle.dumps(qxdm)
  qxdm = None
  time.sleep(2)
  qxdm = pickle.loads(pickled_qxdm)

  qxdm.disconnect()

  time.sleep(2)
  qxdm.quit()

def info(title):
  print(title)
  print('module name:', __name__)
  print('parent process:', os.getpid())
  print('process id:', os.getpid())


if __name__ == '__main__':
  format = '%(asctime)s: %(message)s'
  logging.basicConfig(format=format, level=logging.INFO, datefmt='%H:%M:%S')

  info('main line')
  with Pool(2) as p:
    p.map(worker, (0, 1))

