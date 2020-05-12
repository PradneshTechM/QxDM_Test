#!/usr/local/bin/python3.7

from concurrent import futures
import logging
from xvfbwrapper import Xvfb
from threading import Lock
import datetime
import sys
import time
import shutil
from pathlib import Path
import os

from qxdm_lib import QXDM
import db

import grpc
import qxdm_pb2
import qxdm_pb2_grpc

qxdm = None
lock = Lock()

_BASE_PATH = Path(__file__).parent.resolve()
_TEMP_FOLDER_PATH = (_BASE_PATH.parent / 'temp')
_CHUNK_SIZE = 1024

def read_bytes(file_, num_bytes):
  while True:
    buf = file_.read(num_bytes)
    if not buf:
      break
    yield buf


class HiddenPrints:
  def __enter__(self):
    self._original_stdout = sys.stdout
    sys.stdout = open(os.devnull, 'w')

  def __exit__(self, exc_type, exc_val, exc_tb):
    sys.stdout.close()
    sys.stdout = self._original_stdout


class QXDMServicer(qxdm_pb2_grpc.QXDMServicer):

  def Connect(self, request, context):
    with lock:
      logging.info(f'[Connect] request\t\t| device_index: {request.device_index}')
    
      # qxdm = db.get_object(request.client_id)
      connected = qxdm.connect(request.device_index)
      if connected:
        # db.set_connected(request.client_id, qxdm.port)
        logging.info(f'[Connect] Connected: {request.device_index}')
        connection_state = qxdm_pb2.CONNECTED
      else:
        logging.info(f'[Connect] Could not connect: {request.device_index}')
        connection_state = qxdm_pb2.DISCONNECTED

        # db.set_object(request.client_id, qxdm)

      return qxdm_pb2.ConnectResponse(state=connection_state)


  def Disconnect(self, request, context):
    logging.info(f'[Disconnect] request\t| device_index: {request.device_index}')

  # qxdm = db.get_object(request.client_id)

    connected = qxdm.disconnect(request.device_index)

    if connected:
      logging.info(f'[Disconnect] Disconnected: {request.device_index}')
      connection_state = qxdm_pb2.CONNECTED
    else:
      logging.info(f'[Disconnect] Could not disconnect: {request.device_index}')
      # db.remove_connected(request.client_id)
      connection_state = qxdm_pb2.DISCONNECTED

    # db.set_object(request.client_id, qxdm)

    return qxdm_pb2.DisconnectResponse(state=connection_state)


  def StartLog(self, request, context):
    logging.info(f'[StartLog] request\t\t| device_index: {request.device_index}')

    # qxdm = db.get_object(request.client_id)
    qxdm.start_logs(request.device_index)

    # db.set_logging(request.client_id, datetime.datetime.now().isoformat())
    return qxdm_pb2.StartLogResponse()


  def SaveLog(self, request, context):
    logging.info(f'[SaveLog] request\t\t| device_index: {request.device_index}')

    # qxdm = db.get_object(request.client_id)
    
    filepath = qxdm.save_logs(request.device_index)

    # db.remove_logging(request.client_id)

    # open file and send data in chunks
    with open(filepath, 'rb') as file_content:
      for rec in read_bytes(file_content, _CHUNK_SIZE):
        yield qxdm_pb2.SaveLogResponse(data=rec)
    
    logging.info(f'[SaveLog] Sent logs: {request.device_index}')


def main():
  global qxdm

  bind_address = 'localhost:40041'

  with Xvfb(width=2, height=2, colordepth=8):
    with HiddenPrints():
      qxdm = QXDM()

      logging.info('QXDM launched')

      server = grpc.server(futures.ThreadPoolExecutor(
        max_workers=10, 
        thread_name_prefix='Thread'))
      qxdm_pb2_grpc.add_QXDMServicer_to_server(QXDMServicer(), server)
      server.add_insecure_port(bind_address)
      logging.info(f'Listening on {bind_address}')
      server.start()

      # if not db.is_db_initialized():
      #   logging.info('Initializing database.')
      #   db.initialize_db()

      # remove files in temp folder
      if _TEMP_FOLDER_PATH.exists() and _TEMP_FOLDER_PATH.is_dir():
        shutil.rmtree(_TEMP_FOLDER_PATH)
      os.mkdir(_TEMP_FOLDER_PATH)

      server.wait_for_termination()


if __name__ == '__main__':
  format_str = '[%(threadName)s %(asctime)s.%(msecs)03d]: %(message)s'
  logging.basicConfig(format=format_str, level=logging.INFO, datefmt='%Y-%m-%d %H:%M:%S')
  main()
