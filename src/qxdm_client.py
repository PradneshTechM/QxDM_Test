import logging
from time import sleep
import sys

import grpc

import qxdm_pb2
import qxdm_pb2_grpc

def run():
  with grpc.insecure_channel('localhost:40041') as channel:
    print('Client connected to server at 40041')
    stub = qxdm_pb2_grpc.QXDMStub(channel)

    # launch app
    response = stub.LaunchApp(qxdm_pb2.LaunchAppRequest())
    client_id = response.client_id
    print('Client received: ' + client_id)

    sleep(5)

    # connect device
    response = stub.ConnectDevice(qxdm_pb2.ConnectDeviceRequest(client_id=client_id, device_index=int(sys.argv[2])))

    if (response.state == qxdm_pb2.DISCONNECTED):
      print('Could not connect!'
      )
      stub.QuitApp(qxdm_pb2.QuitAppRequest(client_id=client_id))
      return

    sleep(2)

    # # start log
    # response = stub.StartLog(qxdm_pb2.StartLogRequest(client_id=client_id))

    # # save logs
    # responses = stub.SaveLog(qxdm_pb2.SaveLogRequest(client_id=client_id, log_name=sys.argv[1]))
    # with open(sys.argv[1] + '.isf', 'wb') as file_content:
    #   for response in responses:
    #     file_content.write(response.data)
    # print('Log saved: ' + sys.argv[1] + '.isf')

    # # disconnect device
    # stub.DisconnectDevice(qxdm_pb2.DisconnectDeviceRequest(client_id=client_id))

    # quit app
    response = stub.QuitApp(qxdm_pb2.QuitAppRequest(client_id=client_id))



if __name__ == '__main__':
  logging.basicConfig()
  run()