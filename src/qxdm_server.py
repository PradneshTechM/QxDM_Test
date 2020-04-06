from concurrent import futures
import logging
import multiprocessing
from xvfbwrapper import Xvfb
import threading

import grpc

import qxdm_pb2
import qxdm_pb2_grpc
from qxdm import QXDM

_LOG_FOLDER = '/home/techm/tmdc/qxdm/src/temp'
_CHUNK_SIZE = 1024
_PROCESS_COUNT = multiprocessing.cpu_count()
_THREAD_CONCURRENCY = _PROCESS_COUNT

clients = {}
lock = threading.Lock()

def read_bytes(file_, num_bytes):
  while True:
    buf = file_.read(num_bytes)
    if not buf:
      break
    yield buf

class QXDMServicer(qxdm_pb2_grpc.QXDMServicer):
  
  def get_qxdm_instance(self, client_id):
    with lock:
      return clients[client_id]


  def LaunchApp(self, request, context):
    logging.info(f'[LaunchApp] request')

    qxdm = QXDM()
    qxdm.launch()

    client_id = None
    with lock:
      for i in range(1, 10):
        client_id = str(i)
        if str(i) not in clients:
          clients[client_id] = qxdm
          break
      # print(clients)
    return qxdm_pb2.LaunchAppResponse(client_id=client_id)


  def ConnectDevice(self, request, context):
    logging.info(f'[ConnectDevice] request | client_id: {request.client_id}')

    qxdm = self.get_qxdm_instance(request.client_id)
    connected = qxdm.connect(request.device_index)
    if connected:
      connection_state = qxdm_pb2.CONNECTED
    else:
      connection_state = qxdm_pb2.DISCONNECTED
    return qxdm_pb2.ConnectDeviceResponse(state=connection_state)


  def DisconnectDevice(self, request, context):
    logging.info(f'[DisconnectDevice] request | client_id: {request.client_id}')

    qxdm = self.get_qxdm_instance(request.client_id)
    connected = qxdm.disconnect()
    if connected:
      connection_state = qxdm_pb2.CONNECTED
    else:
      connection_state = qxdm_pb2.DISCONNECTED
    return qxdm_pb2.DisconnectDeviceResponse(state=connection_state)


  def StartLog(self, request, context):
    logging.info(f'[StartLog] request | client_id: {request.client_id}')

    qxdm = self.get_qxdm_instance(request.client_id)
    qxdm.start_logs()
    return qxdm_pb2.StartLogResponse()


  def SaveLog(self, request, context):
    logging.info(f'[SaveLog] request | client_id: {request.client_id}')

    qxdm = self.get_qxdm_instance(request.client_id)
    qxdm.save_logs(_LOG_FOLDER, request.log_name)

    # open file and send data in chunks
    with open(_LOG_FOLDER + '/' + request.log_name + '.isf', 'rb') as file_content:
      for rec in read_bytes(file_content, _CHUNK_SIZE):
        yield qxdm_pb2.SaveLogResponse(data=rec)


  def QuitApp(self, request, context):
    logging.info(f'[QuitApp] request | client_id: {request.client_id}')

    qxdm = self.get_qxdm_instance(request.client_id)
    qxdm.quit()
    with lock:
      del clients[request.client_id]
    # print(clients)
    return qxdm_pb2.QuitAppResponse()


def serve():
  format = '%(asctime)s: %(message)s'
  logging.basicConfig(format=format, level=logging.INFO, datefmt='%H:%M:%S')
  options = (('grpc.so_reuseport', 1),)
  server = grpc.server(futures.ThreadPoolExecutor(max_workers=1,), options=options)
  qxdm_pb2_grpc.add_QXDMServicer_to_server(QXDMServicer(), server)
  logging.info('Server listening on port 40041')
  server.add_insecure_port('[::]:40041')
  server.start()
  server.wait_for_termination()

if __name__ == '__main__':
  logging.basicConfig()
  serve()