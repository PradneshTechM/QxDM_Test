#!/usr/bin/env python3.7

import logging
from time import sleep
import sys
from pathlib import Path
from threading import Thread
import multiprocessing
import atexit
import shutil
import os

from qcat_tests.tc1_lte_latch import main as tc1_lte_latch
from qcat_tests.tc2_VoLTE_Call import main as tc2_volte_call


import grpc

import qxdm_pb2
import qxdm_pb2_grpc

_PROCESS_COUNT = 2

_worker_channel_singleton = None
_worker_stub_singleton = None

_BASE_PATH = Path(__file__).parent.resolve()
CLIENT_TEST_FOLDER = _BASE_PATH.parent / 'client_test'
SAVE_FILE_PATH_1 = CLIENT_TEST_FOLDER / 'saved_test_1.isf'
SAVE_FILE_PATH_2 = CLIENT_TEST_FOLDER / 'saved_test_2.isf'
SAVE_FILE_PATH_3 = CLIENT_TEST_FOLDER / 'saved_test_3.isf'
SAVE_FILE_PATH_4 = CLIENT_TEST_FOLDER / 'saved_test_4.isf'

QCAT_TEST_CONFIG_1 = _BASE_PATH / 'qcat_tests/Test_case_1.json'
QCAT_TEST_CONFIG_2 = _BASE_PATH / 'qcat_tests/Test_case_2.json'

SAVE_PARSED_FILE_PATH_1 = CLIENT_TEST_FOLDER / 'validated_test_case_1.csv'
SAVE_PARSED_FILE_PATH_2 = CLIENT_TEST_FOLDER / 'validated_test_case_2_MO.csv'


def test_status():
    logging.info('Status request')
    response = _worker_stub_singleton.Status(qxdm_pb2.StatusRequest())
    logging.info(f'Status ready: {response.ready}')
    return response.ready


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


def test_stop_log_send_file(device_index, log_path):
    logging.info('Stop log request')
    responses = _worker_stub_singleton.SaveLog(
        qxdm_pb2.SaveLogRequest(device_index=device_index,
                                send_file=True))

    with open(log_path, 'wb') as file_:
        for response in responses:
            file_.write(response.data)
    logging.info(f'Saved log to {log_path}')


def test_stop_log(device_index):
    logging.info('Stop log request')
    responses = _worker_stub_singleton.SaveLog(
        qxdm_pb2.SaveLogRequest(device_index=device_index,
                                send_file=False))
    return responses.next().filename


def test_parse_log(input_path, test_config_path, output_path):

    logging.info(f'Parse log request on: {input_path}')
    responses = _worker_stub_singleton.ParseLog(
        qxdm_pb2.ParseLogRequest(input_filename=input_path,
                                 test_config_filename=str(test_config_path)))

    with open(output_path, 'wb') as file_:
        for response in responses:
            file_.write(response.data)
    logging.info(f'Saved parsed log to {output_path}')


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


def test_log_no_parse_e2e(device_index, log_path):
    if not test_status():
        return
    test_connect(device_index)
    sleep(2)
    test_start_log(device_index)
    sleep(2)
    test_stop_log_send_file(device_index, log_path)
    sleep(2)
    test_disconnect(device_index)


def test_log_parse_e2e(device_index, test_config_path, output_path):
    if not test_status():
        return
    test_connect(device_index)
    sleep(2)
    test_start_log(device_index)
    sleep(2)
    filename = test_stop_log(device_index)
    logging.info(f'log path: {filename}')
    sleep(2)
    test_disconnect(device_index)
    test_parse_log(filename, test_config_path, output_path)


def tc1(device_index, test_config_path, output_path):
    if not test_status():
        return
    test_connect(device_index)
    sleep(2)
    test_start_log(device_index)
    sleep(2)

    tc1_lte_latch()

    filename = test_stop_log(device_index)
    logging.info(f'log path: {filename}')
    sleep(2)
    test_disconnect(device_index)
    test_parse_log(filename, test_config_path, output_path)


def tc1_e2e(server_address):
    _run_multiprocess_test(server_address, tc1, [
        [0, QCAT_TEST_CONFIG_1, SAVE_PARSED_FILE_PATH_1]
    ])


def tc2_setup(device_index):
    if not test_status():
        return
    test_connect(device_index)
    sleep(2)
    test_start_log(device_index)
    sleep(2)


def tc2_finish(device_index, test_config_path, output_path):
    filename = test_stop_log(device_index)
    logging.info(f'log path: {filename}')
    sleep(2)
    test_disconnect(device_index)
    test_parse_log(filename, test_config_path, output_path)


def tc2_e2e(server_address, device_index, parsed_filepath):
    _run_multiprocess_test(server_address, tc2_setup, [
        [device_index]
    ])

    tc2_volte_call()

    _run_multiprocess_test(server_address, tc2_finish, [
        [device_index, QCAT_TEST_CONFIG_2, parsed_filepath]
    ])
    


def main():
    handler = logging.StreamHandler(sys.stdout)
    format = '[PID %(process)d %(asctime)s.%(msecs)03d]: %(message)s'
    logging.basicConfig(format=format,
                        level=logging.INFO,
                        datefmt='%Y-%m-%d %H:%M:%S')

    server_address = 'localhost:40041'

    # remove files in client_test folder
    if CLIENT_TEST_FOLDER.exists() and CLIENT_TEST_FOLDER.is_dir():
        shutil.rmtree(CLIENT_TEST_FOLDER)
    os.mkdir(CLIENT_TEST_FOLDER)

    #tc1_e2e(server_address)

    tc2_e2e(server_address, 0, SAVE_PARSED_FILE_PATH_2)

    #_run_multiprocess_test(server_address, test_log_parse_e2e, [
    #    [1, QCAT_TEST_CONFIG_1, SAVE_PARSED_FILE_PATH_1]
    #])


    # _run_multiprocess_test(server_address, test_connect_e2e,
    #                        [[0], [1], [2], [3], [4]])

    # _run_multiprocess_test(server_address, test_status, [[]])

    #_run_multiprocess_test(server_address, test_log_no_parse_e2e, [
         # [1, SAVE_FILE_PATH_1],
         # [1, SAVE_FILE_PATH_2],
         # [2, SAVE_FILE_PATH_3],
         # [3, SAVE_FILE_PATH_4]
    #])


if __name__ == '__main__':
    main()
