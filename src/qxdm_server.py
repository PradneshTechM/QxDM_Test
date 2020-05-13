#!/usr/local/bin/python3.7

from concurrent import futures
import logging
from xvfbwrapper import Xvfb
import threading
import datetime
import sys
import time
import shutil
from pathlib import Path
import os

import qxdm_lib

import grpc
import qxdm_pb2
import qxdm_pb2_grpc

"""
This gRPC server handles the following requests:
1. connect a device index
2. disconnect a device index
3. start logging for a device index
4. stop logging for a device index
5. QXDM status

qxdm_lib.QXDM manages active sessions.  If QXDM stops running (e.g. crashes, power failure), all connections and logging is lost anyways so no external database is necessary - server will automatically restart QXDM itself or when a request comes in.

Known issues:
* if QXDM isn't running between qxdm.process_running() calls, yet the library function is called, an unhandled exception is thrown - server will recover after _PROCESS_CHECK_INTERVAL seconds if QXDM can be launched successfully.
* if QXDM can't be run the first time, e.g. due to no/invalid license, the following exception is raised:
  gi.repository.GLib.Error: g-dbus-error-quark: GDBus.Error:org.freedesktop.DBus.Error.ServiceUnknown: The name com.qcom.QXDM was not provided by any .service files (2)
"""

qxdm = None
qxdm_lock = threading.Lock()
launching_lock = threading.Lock()

_PROCESS_CHECK_INTERVAL = 60
_BASE_PATH = Path(__file__).parent.resolve()
_TEMP_FOLDER_PATH = (_BASE_PATH.parent / 'temp')
_CHUNK_SIZE = 1024


def read_bytes(file_, num_bytes):
  while True:
    buf = file_.read(num_bytes)
    if not buf:
      break
    yield buf


# https://stackoverflow.com/a/28034554
def do_every(period,f,*args):
  def g_tick():
    t = time.time()
    count = 0
    while True:
        count += 1
        yield max(t + count*period - time.time(),0)
  g = g_tick()
  while True:
    time.sleep(next(g))
    f(*args)


class HiddenPrints:
  def __enter__(self):
    self._original_stdout = sys.stdout
    sys.stdout = open(os.devnull, 'w')

  def __exit__(self, exc_type, exc_val, exc_tb):
    sys.stdout.close()
    sys.stdout = self._original_stdout


class QXDMServicer(qxdm_pb2_grpc.QXDMServicer):

  def Connect(self, request, context):
    with qxdm_lock:
      logging.info(f'[Connect] request\t\t| device_index: {request.device_index}')

      if not qxdm.process_running():
        context.abort(
          code=grpc.StatusCode.FAILED_PRECONDITION,
          details='QXDM not running. Try again later.'
        )
        launch_qxdm_if_not_running()

      connected = qxdm.connect(request.device_index)

      if connected:
        logging.info(f'[Connect] Connected: {request.device_index}')
        connection_state = qxdm_pb2.CONNECTED
      else:
        logging.info(f'[Connect] Could not connect: {request.device_index}')
        connection_state = qxdm_pb2.DISCONNECTED

      return qxdm_pb2.ConnectResponse(state=connection_state)


  def Disconnect(self, request, context):
    logging.info(f'[Disconnect] request\t| device_index: {request.device_index}')

    if not qxdm.process_running():
      context.abort(
        code=grpc.StatusCode.FAILED_PRECONDITION,
        details='QXDM not running. Try again later.'
      )
      launch_qxdm_if_not_running()

    connected = qxdm.disconnect(request.device_index)

    if connected:
      logging.info(f'[Disconnect] Disconnected: {request.device_index}')
      connection_state = qxdm_pb2.CONNECTED
    else:
      logging.info(f'[Disconnect] Could not disconnect: {request.device_index}')
      connection_state = qxdm_pb2.DISCONNECTED

    return qxdm_pb2.DisconnectResponse(state=connection_state)


  def StartLog(self, request, context):
    logging.info(f'[StartLog] request\t\t| device_index: {request.device_index}')

    if not qxdm.process_running():
      context.abort(
        code=grpc.StatusCode.FAILED_PRECONDITION,
        details='QXDM not running. Try again later.'
      )
      launch_qxdm_if_not_running()

    qxdm.start_logs(request.device_index)

    return qxdm_pb2.StartLogResponse()


  def SaveLog(self, request, context):
    logging.info(f'[SaveLog] request\t\t| device_index: {request.device_index}')

    if not qxdm.process_running():
      context.abort(
        code=grpc.StatusCode.FAILED_PRECONDITION,
        details='QXDM not running. Try again later.'
      )
      launch_qxdm_if_not_running()

    filepath = qxdm.save_logs(request.device_index)

    # open file and send data in chunks
    with open(filepath, 'rb') as file_content:
      for rec in read_bytes(file_content, _CHUNK_SIZE):
        yield qxdm_pb2.SaveLogResponse(data=rec)
    
    logging.info(f'[SaveLog] Sent logs: {request.device_index}')


  def Status(self, request, context):
    ready = qxdm.process_running()
    if not ready:
      # launch in another thread
      threading.Thread(target=launch_qxdm_if_not_running)

    logging.info(f'[Status] request, response: {ready}')

    return qxdm_pb2.StatusResponse(ready=ready)


def launch_qxdm_if_not_running(log = 'QXDM re-launched.'):
  global qxdm, launching_lock

  # only 1 thread with launching_lock can execute below
  with launching_lock:
    # qxdm hasn't been started before, or it was running but not anymore
    if not qxdm or (qxdm and not qxdm.process_running()):
      qxdm = qxdm_lib.QXDM()
      if qxdm.process_running():
        logging.info(log)
      else:
        logging.info('QXDM could not be re-launched.')


def main():
  bind_address = 'localhost:40041'

  with Xvfb(width=2, height=2, colordepth=8):
    with HiddenPrints():
      launch_qxdm_if_not_running('QXDM launched.')

      server = grpc.server(futures.ThreadPoolExecutor(
        max_workers=10, 
        thread_name_prefix='Thread'))
      qxdm_pb2_grpc.add_QXDMServicer_to_server(QXDMServicer(), server)
      server.add_insecure_port(bind_address)
      logging.info(f'Listening on {bind_address}')
      server.start()

      # remove files in temp folder
      if _TEMP_FOLDER_PATH.exists() and _TEMP_FOLDER_PATH.is_dir():
        shutil.rmtree(_TEMP_FOLDER_PATH)
      os.mkdir(_TEMP_FOLDER_PATH)

      # launch QXDM if it's not running every _PROCESS_CHECK_INTERVAL
      do_every(_PROCESS_CHECK_INTERVAL, launch_qxdm_if_not_running, 
        'QXDM not running. Launching it.')

      server.wait_for_termination()


if __name__ == '__main__':
  format_str = '[%(threadName)s %(asctime)s.%(msecs)03d]: %(message)s'
  logging.basicConfig(format=format_str, level=logging.INFO, datefmt='%Y-%m-%d %H:%M:%S')
  main()
