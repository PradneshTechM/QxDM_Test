#!/usr/local/bin/python3.7

import logging
import threading
import time
import concurrent.futures
import sys
from xvfbwrapper import Xvfb
from queue import Queue

from qxdm_lib import QXDM

qxdm = None
lock = threading.Lock()


def worker(device_index):
  logging.info(f'Started worker for {device_index}')
  with lock:
    logging.info(f'Connecting {device_index}')
    qxdm.connect(device_index)

  logging.info(f'Disconnecting {device_index}')
  qxdm.disconnect(device_index)
  

def test_launch_single_qxdm():
  global qxdm
  with Xvfb(width=2, height=2, colordepth=8):
    qxdm = QXDM()

    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
      executor.map(worker, range(5))
    
    qxdm.quit()


if __name__ == '__main__':
  format_str = '[TID %(threadName)s %(asctime)s.%(msecs)03d]: %(message)s'
  logging.basicConfig(format=format_str, level=logging.INFO, datefmt='%Y-%m-%d %H:%M:%S')

  test_launch_single_qxdm()