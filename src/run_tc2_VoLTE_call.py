#!/usr/bin/env python3.7
from gi.repository import GLib, Gio
import logging
import os
from pathlib import Path
import shutil
import sys
import time
from xvfbwrapper import Xvfb

import qxdm_lib
import qcat_lib
from qcat_tests.tc2_VoLTE_Call import main as tc2_volte_call

qcat = None
qxdm = None
device_index_MO = 1
device_index_MT = 1 if device_index_MO == 0 else 0

_BASE_PATH = Path(__file__).parent.resolve()
_TEMP_FOLDER_PATH = (_BASE_PATH.parent / 'temp')
_TC1_TEST_CONFIG = _BASE_PATH / 'qcat_tests/Test_case_1.json'



class HiddenPrints:
    def __enter__(self):
        self._original_stdout = sys.stdout
        sys.stdout = open(os.devnull, 'w')

    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stdout.close()
        sys.stdout = self._original_stdout


def launch_qxdm_qcat_if_not_running():
    global qxdm, qcat

    if not qcat:
        qcat = qcat_lib.QCAT()
    while not qxdm or (qxdm and not qxdm.process_running()):
        try:
            qxdm = qxdm_lib.QXDM()
            if qxdm.process_running():
                logging.info('QXDM launched')
            else:
                logging.info('QXDM could not be re-launched')
            time.sleep(5)
        except GLib.Error:
            logging.info('Could not connect to QXDM Dbus. Check license.')


def connect(device_index, device):
    connected = qxdm.connect(device_index)
    if connected:
        logging.info(f'Connected device: {device}')
    else:
        return logging.info('Could not connect: ')


def disconnect(device_index, device):
    disconnected = qxdm.disconnect(device_index)
    if disconnected:
        logging.info(f'Disconnected device: {device}')
    else:
        return logging.info('Could not disconnect: ')


def main():
    with Xvfb(width=2, height=2, colordepth=8):
        with HiddenPrints():
            launch_qxdm_qcat_if_not_running()

            # remove files in client_test folder
            if _TEMP_FOLDER_PATH.exists() and _TEMP_FOLDER_PATH.is_dir():
                shutil.rmtree(_TEMP_FOLDER_PATH)
            os.mkdir(_TEMP_FOLDER_PATH)

            # connect to device index
            connect(device_index_MO)
            connect(device_index_MT)

            # start logging
            logging.info('Started logging')

            qxdm.start_logs(device_index_MO, 'MO')
            qxdm.start_logs(device_index_MT, 'MT')

        tc2_volte_call()

        # stop logging
        with HiddenPrints():
            logging.info('Stopped logging')
            filepath = qxdm.save_logs(device_index_MO)
            logging.info(f'Log saved to: {filepath}')

            # disconnect from device index
            disconnect(device_index_MO, 'MO')
            disconnect(device_index_MT, 'MT')

            # set name and path of parsed results file
            path, filename = os.path.split(filepath)
            filename = 'tc1_lte_latch'
            raw_filename = f'result_raw_{filename}.txt'
            raw_filepath = os.path.join(path, raw_filename)
            parsed_filename = f'result_parsed_{filename}.txt'
            parsed_filepath = os.path.join(path, parsed_filename)
            validated_filename = f'result_validated_{filename}.txt'
            validated_filepath = os.path.join(path, validated_filename)
            validated_csv_filename = f'result_validated_{filename}.csv'
            validated_csv_filepath = os.path.join(path, validated_csv_filename)

            # call QCAT library on the log file which needs parsing
            logging.info('QCAT parsing log file')
            parsed = qcat_lib.parse_log(filepath,
                                        _TC1_TEST_CONFIG,
                                        raw_filepath,
                                        parsed_filepath,
                                        validated_filepath,
                                        validated_csv_filepath,
                                        qcat)

            if not parsed:
                return logging.error('QCAT parsing failed')

            logging.info('QCAT parsed log file')
            
            logging.info('Quit QXDM and QCAT')
            qxdm.quit()
            qcat.quit()


if __name__ == '__main__':
    format_str = '[%(asctime)s.%(msecs)03d]: %(message)s'
    logging.basicConfig(format=format_str,
                        level=logging.INFO,
                        datefmt='%Y-%m-%d %H:%M:%S')
    main()

