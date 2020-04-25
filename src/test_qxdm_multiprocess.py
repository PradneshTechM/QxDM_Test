#!/usr/local/bin/python3.7

from multiprocessing import Pool, Queue
import logging
import threading
import time
import concurrent.futures
import sys
import os
from xvfbwrapper import Xvfb

import pickle

from qxdm_v2 import QXDM

_PROCESS_COUNT = 2

queue = None

def worker_launch_qxdm_outside(device_index):
  logging.info(f'Started worker for {device_index}')
  
  
  qxdm = None
  for _ in range(queue.qsize()):
    qxdm_instance = queue.get()
    if not qxdm_instance.connected_to():
      qxdm = qxdm_instance
      break
    else:
      queue.put(qxdm_instance)
  
  if not qxdm:
    logging.info(f'No QXDM available for {device_index}')
    return

  logging.info('Display env variable: %s', os.environ['DISPLAY'])

  logging.info('Connecting %s', device_index)

  qxdm.connect(device_index)

  queue.put(qxdm)

  time.sleep(2)

  logging.info('Disconnecting %s', device_index)
  
  qxdm = None
  for _ in range(queue.qsize()):
    qxdm_instance = queue.get()
    if qxdm_instance.connected_to() == device_index:
      qxdm = qxdm_instance
      break
    else:
      queue.put(qxdm_instance)
  
  if not qxdm:
    logging.info(f'No QXDM available for {device_index}')
    return

  qxdm.disconnect()

  queue.put(qxdm)

  time.sleep(2)


def worker_launch_qxdm_inside(device_index):
  logging.info(f'Started worker for {device_index}')
  qxdm = QXDM()
  logging.info('Launching QXDM')
  qxdm.launch()

  time.sleep(2)

  logging.info('Connecting %s', device_index)
  qxdm.connect(device_index)

  queue.put(qxdm)

  time.sleep(2)

  qxdm = queue.get()

  logging.info('Disconnecting %s', device_index)
  qxdm.disconnect()

  time.sleep(2)


# start qxdm processes within parent process where each QXDM is started in its own xvfb virtual display - issue when trying to access Dbus: 'gi.repository.GLib.Error: g-io-error-quark: Timeout was reached (24)'
def test_xvfb_and_qxdm_per_subprocess():
  global queue

  queue = Queue()
  for _ in range(_PROCESS_COUNT):
    qxdm = QXDM()
    qxdm.launch()
    queue.put(qxdm)
  
  with Pool(_PROCESS_COUNT) as p:
    p.map(worker_launch_qxdm_outside, (1, 2, 3, 4))




# start xvfb and qxdm processes within parent process and get qxdm process from sub-processes - issue when trying to access Dbus: 'gi.repository.GLib.Error: g-io-error-quark: Timeout was reached (24)'
def test_launch_qxdm_outside_worker():
  global queue

  with Xvfb(width=2, height=2, colordepth=8):
    queue = Queue()
    for _ in range(_PROCESS_COUNT):
      qxdm = QXDM()
      qxdm.launch()
      queue.put(qxdm)
    
    with Pool(_PROCESS_COUNT) as p:
      p.map(worker_launch_qxdm_outside, (1, 2, 3, 4))
  


# start xvfb in parent process and qxdm within sub-processes - no issue
def test_launch_qxdm_inside_worker():
  global queue

  queue = Queue()

  with Xvfb(width=2, height=2, colordepth=8):
    with Pool(_PROCESS_COUNT) as p:
      p.map(worker_launch_qxdm_inside, (1, 2, 3, 4))
  


if __name__ == '__main__':
  format_str = '[PID %(process)d %(asctime)s]: %(message)s'
  logging.basicConfig(format=format_str, level=logging.INFO, datefmt='%Y-%m-%d %H:%M:%S')

  test_launch_qxdm_inside_worker()
  # test_launch_qxdm_outside_worker()
  # test_xvfb_and_qxdm_per_subprocess()

  
  # logging.info('Display env variable: %s', os.environ['DISPLAY'])

