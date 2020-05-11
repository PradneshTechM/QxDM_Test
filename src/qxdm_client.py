#!/usr/local/bin/python3.7

import logging
from time import sleep
import sys
from pathlib import Path
from threading import Thread
import multiprocessing
import atexit
import shutil
import os

import grpc

import qxdm_pb2
import qxdm_pb2_grpc

_PROCESS_COUNT = multiprocessing.cpu_count()

_worker_channel_singleton = None
_worker_stub_singleton = None

_BASE_PATH = Path(__file__).parent.resolve()
CLIENT_TEST_FOLDER = _BASE_PATH.parent / 'client_test'
SAVE_FILE_PATH_1 = CLIENT_TEST_FOLDER / 'saved_test_1.isf'
SAVE_FILE_PATH_2 = CLIENT_TEST_FOLDER / 'saved_test_2.isf'
SAVE_FILE_PATH_3 = CLIENT_TEST_FOLDER / 'saved_test_3.isf'
SAVE_FILE_PATH_4 = CLIENT_TEST_FOLDER / 'saved_test_4.isf'


def test_connect(device_index):
  logging.info('Connect request')
  response = _worker_stub_singleton.Connect(
    qxdm_pb2.ConnectRequest(device_index=device_index))
  return response.state


def test_disconnect(device_index):
  logging.info('Disconnect request')
  response = _worker_stub_singleton.Disconnect(
    qxdm_pb2.DisconnectRequest(device_index=device_index))
  return response.state


def test_start_log(device_index):
  logging.info('Start log request')
  _worker_stub_singleton.StartLog(
    qxdm_pb2.StartLogRequest(device_index=device_index))


def test_stop_log(device_index, log_path):
  logging.info('Stop log request')
  responses = _worker_stub_singleton.SaveLog(
    qxdm_pb2.SaveLogRequest(device_index=device_index))

  with open(log_path, 'wb') as file_:
    for response in responses:
      file_.write(response.data)
  logging.info(f'Saved log to {log_path}')


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
  worker_pool.starmap(test, args)


def test_connect_e2e(device_index):
  test_connect(device_index)
  sleep(2)
  test_disconnect(device_index)


def test_log_e2e(device_index, log_path):
  test_connect(device_index)
  sleep(2)
  test_start_log(device_index)
  sleep(2)
  test_stop_log(device_index, log_path)
  sleep(2)
  test_disconnect(device_index)
  

def main():
  server_address = 'localhost:40041'
  
  # remove files in client_test folder
  if CLIENT_TEST_FOLDER.exists() and CLIENT_TEST_FOLDER.is_dir():
    shutil.rmtree(CLIENT_TEST_FOLDER)
  os.mkdir(CLIENT_TEST_FOLDER)
  
  # _run_multiprocess_test(server_address, test_connect_e2e, [[0], [1], [2], [3], [4]])
  
  _run_multiprocess_test(server_address, test_log_e2e, [
    [0, SAVE_FILE_PATH_1],
    [1, SAVE_FILE_PATH_2],
    [2, SAVE_FILE_PATH_3],
    [3, SAVE_FILE_PATH_4]
  ])


if __name__ == '__main__':  
  handler = logging.StreamHandler(sys.stdout)
  format = '[PID %(process)d %(asctime)s.%(msecs)03d]: %(message)s'
  logging.basicConfig(format=format, level=logging.INFO, datefmt='%Y-%m-%d %H:%M:%S')
  main()