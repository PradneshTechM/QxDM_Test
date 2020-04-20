#!/usr/local/bin/python3.7

import logging
from time import sleep
import sys

import grpc

import qxdm_pb2
import qxdm_pb2_grpc

def test_launch(stub):
  response = stub.LaunchApp(qxdm_pb2.LaunchAppRequest())
  return response.client_id

def test_connect(stub, client_id, device_index):
  response = stub.ConnectDevice(qxdm_pb2.ConnectDeviceRequest(
    client_id=client_id, 
    device_index=device_index
  ))

def test_quit(stub, client_id):
  response = stub.QuitApp(qxdm_pb2.QuitAppRequest(client_id=client_id))
  print(response)

def run():
  with grpc.insecure_channel('localhost:40041') as channel:
    print('Client connected to server at 40041')
    stub = qxdm_pb2_grpc.QXDMStub(channel)

    client_id_1 = test_launch(stub)
    client_id_2 = test_launch(stub)

    sleep(2)

    test_connect(stub, client_id_1, 0)
    test_connect(stub, client_id_1, 1)

    sleep(2)

    test_quit(stub, client_id_2)
    test_quit(stub, client_id_1)

    # # connect device
    # response = stub.ConnectDevice(qxdm_pb2.ConnectDeviceRequest(client_id=client_id, device_index=int(sys.argv[2])))

    # if (response.state == qxdm_pb2.DISCONNECTED):
    #   print('Could not connect!'
    #   )
    #   stub.QuitApp(qxdm_pb2.QuitAppRequest(client_id=client_id))
    #   return

    # sleep(2)

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
    # response = stub.QuitApp(qxdm_pb2.QuitAppRequest(client_id=client_id))



if __name__ == '__main__':
  logging.basicConfig()
  run()