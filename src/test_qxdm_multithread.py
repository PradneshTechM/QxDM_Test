#!/usr/local/bin/python3.7

import logging
import threading
import time
import concurrent.futures
import sys
from xvfbwrapper import Xvfb

from qxdm_new_v2 import QXDM


def thread_function(name, device_index):
  xvfb = Xvfb(width=2, height=2, colordepth=8)
  xvfb.start()
  qxdm = QXDM()
  qxdm.launch()
  logging.info('Thread %s: launching QXDM', name)
  logging.info('Thread %s: connecting %s', name, device_index)
  qxdm.connect(device_index)
  logging.info('Thread %s: connected %s', name, device_index)
  # qxdm.quit()
  # xvfb.stop()


if __name__ == '__main__':
  # xvfb = Xvfb(width=2, height=2, colordepth=8)
  # xvfb.start()

  format = '%(asctime)s: %(message)s'
  logging.basicConfig(format=format, level=logging.INFO, datefmt='%H:%M:%S')

  with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
    executor.map(thread_function, range(2), range(2))

  # xvfb.stop()