#!/usr/local/bin/python3.7

import logging
import threading
import time
import concurrent.futures
import sys

from qxdm_new_v2 import QXDM

qxdm = QXDM()
qxdm.launch()

def thread_function(name, device_index):
  logging.info('Thread %s: getting QXDM session', name)
  session = qxdm.get_session()
  time.sleep(5)
  logging.info('Thread %s: connecting %s', name, device_index)
  qxdm.connect(session, device_index)
  logging.info('Thread %s: connected %s', name, device_index)
  time.sleep(5)


if __name__ == '__main__':
  format = '%(asctime)s: %(message)s'
  logging.basicConfig(format=format, level=logging.INFO, datefmt='%H:%M:%S')

  with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
    executor.map(thread_function, range(2), range(2))

  qxdm.quit("QXDM1") 