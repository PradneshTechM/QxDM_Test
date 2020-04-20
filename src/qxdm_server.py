#!/usr/local/bin/python3.7

from concurrent import futures
import logging
import multiprocessing
from xvfbwrapper import Xvfb
import threading
import datetime
import sys
import time

from qxdm_new_v2 import QXDM
import db

import grpc
import qxdm_pb2
import qxdm_pb2_grpc

_ONE_DAY = datetime.timedelta(days=1)

_LOG_FOLDER = '/home/techm/tmdc/qxdm/src/temp'
_CHUNK_SIZE = 1024
_PROCESS_COUNT = multiprocessing.cpu_count()
_THREAD_CONCURRENCY = _PROCESS_COUNT

def read_bytes(file_, num_bytes):
  while True:
    buf = file_.read(num_bytes)
    if not buf:
      break
    yield buf

class QXDMServicer(qxdm_pb2_grpc.QXDMServicer):

  def LaunchApp(self, request, context):
    logging.info(f'[LaunchApp] request')

    qxdm = QXDM()
    qxdm.launch()

    client_id = db.add_process()
    db.set_object(client_id, qxdm)

    return qxdm_pb2.LaunchAppResponse(client_id=client_id)


  def ConnectDevice(self, request, context):
    logging.info(f'[ConnectDevice] request | client_id: {request.client_id}')

    
    qxdm = db.get_object(request.client_id)

    connected = qxdm.connect(request.device_index)

    if connected:
      db.set_connected(request.client_id, qxdm.port)
      connection_state = qxdm_pb2.CONNECTED
    else:
      connection_state = qxdm_pb2.DISCONNECTED

    db.set_object(request.client_id, qxdm)

    return qxdm_pb2.ConnectDeviceResponse(state=connection_state)


  def DisconnectDevice(self, request, context):
    logging.info(f'[DisconnectDevice] request | client_id: {request.client_id}')

    qxdm = db.get_object(request.client_id)

    connected = qxdm.disconnect()

    if connected:
      connection_state = qxdm_pb2.CONNECTED
    else:
      db.remove_connected(request.client_id)
      connection_state = qxdm_pb2.DISCONNECTED

    db.set_object(request.client_id, qxdm)

    return qxdm_pb2.DisconnectDeviceResponse(state=connection_state)


  def StartLog(self, request, context):
    logging.info(f'[StartLog] request | client_id: {request.client_id}')

    qxdm = db.get_object(request.client_id)
    
    qxdm.start_logs()

    db.set_logging(request.client_id, datetime.now())
    return qxdm_pb2.StartLogResponse()


  def SaveLog(self, request, context):
    logging.info(f'[SaveLog] request | client_id: {request.client_id}')

    qxdm = db.get_object(request.client_id)

    qxdm.save_logs(_LOG_FOLDER, request.log_name)

    db.remove_logging(request.client_id)

    # open file and send data in chunks
    with open(_LOG_FOLDER + '/' + request.log_name + '.isf', 'rb') as file_content:
      for rec in read_bytes(file_content, _CHUNK_SIZE):
        yield qxdm_pb2.SaveLogResponse(data=rec)


  def QuitApp(self, request, context):
    logging.info(f'[QuitApp] request | client_id: {request.client_id}')

    qxdm = db.get_object(request.client_id)

    qxdm.quit()

    db.remove_process(request.client_id)
    
    return qxdm_pb2.QuitAppResponse()


def _wait_forever(server):
  try:
    while True:
      time.sleep(_ONE_DAY.total_seconds())
  except KeyboardInterrupt:
    server.stop(None)


def _run_server(bind_address):
  """Start a server in a subprocess."""
  logging.info('Starting new server.')
  options = (('grpc.so_reuseport', 1),)

  server = grpc.server(
    futures.ThreadPoolExecutor(max_workers=_THREAD_CONCURRENCY,),
    options=options)
  qxdm_pb2_grpc.add_QXDMServicer_to_server(QXDMServicer(), server)
  server.add_insecure_port(bind_address)
  logging.info(f'Listening on {bind_address}')
  server.start()
  _wait_forever(server)


def main():
  if not db.is_db_initialized():
    logging.info('Initializing database.')
    db.initialize_db()

  bind_address = 'localhost:40041'
  workers = []
  for _ in range(_PROCESS_COUNT):
    worker = multiprocessing.Process(target=_run_server, args=(bind_address,))
    worker.start()
    workers.append(worker)
  for worker in workers:
    worker.join()


if __name__ == '__main__':
  handler = logging.StreamHandler(sys.stdout)
  format = '[PID %(process)d %(asctime)s]: %(message)s'
  logging.basicConfig(format=format, level=logging.INFO, datefmt='%Y-%m-%d %H:%M:%S')
  main()