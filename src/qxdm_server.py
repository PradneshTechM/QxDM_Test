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

'''

Discoveries:
1. qxdm.getQXDMSession(True) - must pass True for multi-process concurrent connection to work, otherwise only a 1 device will connect.  For multi-thread only 1 device connects whether parameter is true or false.


Issues:

1. 
Xvfb started in server vs. before each QXDM process launched
  - started in server: even with different subprocesses that receive connect request, only 1 device connects
  - started before each QXDM process launched: if different subprocesses receive connect requests, multiple devices connect.  if same subprocess receives connect requests, only 1 device connects.

2. 
if same subprocess calls quit() multiple times, 1 process successfully quits and another throws exception: 'g-dbus-error-quark: GDBus.Error:org.freedesktop.DBus.Error.ServiceUnknown: The name com.qcom.QXDM was not provided by any .service files (2)'

if different subprocesses call quit(), there's no exception.

3. 
after one cycle of launching and quitting app, any subsequent launch request comes throws an exception: 'gi.repository.GLib.GError: g-io-error-quark: The connection is closed (18)'

* frequent error on qxdm.quit(), doesn't seem to have any impact
'XIO:  fatal IO error 22 (Invalid argument) on X server ":19701"
      after 420 requests (418 known processed) with 0 events remaining.'

DO NOT CALL QUIT()
'''

queue = None

_ONE_DAY = datetime.timedelta(days=1)

_LOG_FOLDER = '/home/techm/tmdc/qxdm/src/temp'
_CHUNK_SIZE = 1024
_PROCESS_COUNT = 2
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
    logging.info(f'[ConnectDevice] request | device_index: {request.device_index}')
    
    # qxdm = db.get_object(request.client_id)
    qxdm = None
    for _ in range(queue.qsize()):
      qxdm_instance = queue.get()
      if not qxdm_instance.connected_to():
        qxdm = qxdm_instance
        break
      else:
        queue.put(qxdm_instance)

    if not qxdm:
      logging.info(f'No QXDM available for {request.device_index}')
      return
    
    logging.info(f'session: {qxdm.session}')

    connected = qxdm.connect(request.device_index)

    if connected:
      # db.set_connected(request.client_id, qxdm.port)
      connection_state = qxdm_pb2.CONNECTED
    else:
      connection_state = qxdm_pb2.DISCONNECTED

    # db.set_object(request.client_id, qxdm)
    queue.put(qxdm)

    return qxdm_pb2.ConnectDeviceResponse(state=connection_state)


  def DisconnectDevice(self, request, context):
    logging.info(f'[DisconnectDevice] request | device_index: {request.device_index}')

    # qxdm = db.get_object(request.client_id)
    qxdm = None
    for _ in range(queue.qsize()):
      qxdm_instance = queue.get()
      if qxdm_instance.connected_to() == request.device_index:
        qxdm = qxdm_instance
        break
      else:
        queue.put(qxdm_instance)

    if not qxdm:
      logging.info(f'No QXDM available for {request.device_index}')
      return

    connected = qxdm.disconnect()

    if connected:
      connection_state = qxdm_pb2.CONNECTED
    else:
      # db.remove_connected(request.client_id)
      connection_state = qxdm_pb2.DISCONNECTED

    # db.set_object(request.client_id, qxdm)
    queue.put(qxdm)

    return qxdm_pb2.DisconnectDeviceResponse(state=connection_state)


  def StartLog(self, request, context):
    logging.info(f'[StartLog] request | client_id: {request.client_id}')

    qxdm = db.get_object(request.client_id)
    
    qxdm.start_logs()

    db.set_logging(request.client_id, datetime.datetime.now().isoformat())
    return qxdm_pb2.StartLogResponse()


  def SaveLog(self, request, context):
    logging.info(f'[SaveLog] request | client_id: {request.client_id}')

    qxdm = db.get_object(request.client_id)
    
    filepath = qxdm.save_logs()

    db.remove_logging(request.client_id)

    # open file and send data in chunks
    with open(filepath, 'rb') as file_content:
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
  global queue
  if not db.is_db_initialized():
    logging.info('Initializing database.')
    db.initialize_db()
  
  queue = multiprocessing.Queue()

  with Xvfb(width=2, height=2, colordepth=8):
    for _ in range(1):
      qxdm = QXDM()
      qxdm.launch()
      queue.put(qxdm)

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
  format = '[PID %(process)d %(asctime)s.%(msecs)03d]: %(message)s'
  logging.basicConfig(format=format, level=logging.INFO, datefmt='%Y-%m-%d %H:%M:%S')
  main()