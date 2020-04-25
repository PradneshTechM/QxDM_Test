#!/usr/local/bin/python3.7

import logging
from time import sleep
import sys
from pathlib import Path
from threading import Thread
import multiprocessing
import atexit


import grpc

import qxdm_pb2
import qxdm_pb2_grpc

_PROCESS_COUNT = 4

_worker_channel_singleton = None
_worker_stub_singleton = None

_BASE_PATH = Path(__file__).parent.resolve()
SAVE_FILE_PATH_1 = _BASE_PATH / 'test/saved_test_1.isf'
SAVE_FILE_PATH_2 = _BASE_PATH / 'test/saved_test_2.isf'


def test_launch():
  logging.info('Launch request')
  response = _worker_stub_singleton.LaunchApp(qxdm_pb2.LaunchAppRequest())
  return response.client_id

def test_connect(device_index):
  logging.info('Connect request')
  response = _worker_stub_singleton.ConnectDevice(
    qxdm_pb2.ConnectDeviceRequest(device_index=device_index))
  return response.state

def test_disconnect(device_index):
  logging.info('Disconnect request')
  response = _worker_stub_singleton.DisconnectDevice(
    qxdm_pb2.DisconnectDeviceRequest(device_index=device_index))
  return response.state

def test_start_log(client_id):
  logging.info('Start log request')
  _worker_stub_singleton.StartLog(qxdm_pb2.StartLogRequest(client_id=client_id))

def test_stop_log(client_id, log_path):
  logging.info('Stop log request')
  responses = _worker_stub_singleton.SaveLog(
    qxdm_pb2.SaveLogRequest(client_id=client_id))

  with open(log_path, 'wb') as file_:
    for response in responses:
      file_.write(response.data)


def _shutdown_worker():
  logging.info('Shutting worker process down.')
  if _worker_channel_singleton is not None:
    _worker_channel_singleton.stop()


def _initialize_worker(server_address):
  global _worker_channel_singleton
  global _worker_stub_singleton
  logging.info('Initializing worker process.')
  _worker_channel_singleton = grpc.insecure_channel(server_address)
  _worker_stub_singleton = qxdm_pb2_grpc.QXDMStub(_worker_channel_singleton)
  atexit.register(_shutdown_worker)


def _run_multiprocess_test(server_address, test, args):
  worker_pool = multiprocessing.Pool(
    processes=_PROCESS_COUNT,
    initializer=_initialize_worker,
    initargs=(server_address,))
  worker_pool.map(test, args)


def test_connect_e2e(device_index):
  # client_id = test_launch()
  test_connect(device_index)
  # test_quit(client_id)
  sleep(2)

  test_disconnect(device_index)

def test_quit(client_id):
  _worker_stub_singleton.QuitApp(qxdm_pb2.QuitAppRequest(client_id=client_id))


def test_log_e2e(device_index, log_path):
  client_id = test_launch()
  sleep(2)
  test_connect(client_id, device_index)
  sleep(2)
  test_start_log(client_id)
  sleep(2)
  test_stop_log(client_id, log_path)
  sleep(2)
  test_quit(client_id)
  


def main():
  server_address = 'localhost:40041'
  _run_multiprocess_test(server_address, test_connect_e2e, (0,))

  # thread1 = Thread(target=test_connect_e2e, args=(stub, 0))
  # thread2 = Thread(target=test_connect_e2e, args=(stub, 1))
  
  # thread1 = Thread(target=test_log_e2e, args=(stub, 0, SAVE_FILE_PATH_1))
  # thread1 = Thread(target=test_log_e2e, args=(stub, 0, SAVE_FILE_PATH_2))

  # thread1.start()
  # thread2.start()
  # thread1.join()
  # thread2.join()

  # client_id_1 = test_launch(stub)
  # client_id_2 = test_launch(stub)

  # sleep(2)

  # test_connect(stub, client_id_1, 0)
  # test_connect(stub, client_id_2, 1)

  # sleep(2)

  # test_start_log(stub, client_id_1)

  # # test_disconnect(stub, client_id_1)
  # # test_disconnect(stub, client_id_2)

  # sleep(2)

  # test_stop_log(stub, client_id_2)

  # sleep(2)

  # test_quit(stub, client_id_1)
  # test_quit(stub, client_id_2)

  

  # test_quit(stub, client_id_2)
  # test_quit(stub, client_id_1)




if __name__ == '__main__':  
  handler = logging.StreamHandler(sys.stdout)
  format = '[PID %(process)d %(asctime)s.%(msecs)03d]: %(message)s'
  logging.basicConfig(format=format, level=logging.INFO, datefmt='%Y-%m-%d %H:%M:%S')
  main()