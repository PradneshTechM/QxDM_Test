#!/usr/bin/env python3.7
import logging
import os
from pathlib import Path
import shutil
import sys
import time

import quts_lib
import qcat_lib_win as qcat_lib
from qcat_tests.tc2_VoLTE_Call_tmdc import main as tc2_volte_call

_BASE_PATH = Path(__file__).parent.resolve()
_TEMP_FOLDER_PATH = (_BASE_PATH.parent / 'temp')
_FINAL_FOLDER_PATH = (_BASE_PATH.parent / 'TC2_VoLTE_call_logs')
_TC2_TEST_CONFIG = _BASE_PATH / 'qcat_tests/Test_case_2.json'

DUT_MO = '96041FFBA0007B'
DUT_MT = '94KBA0090A'

class HiddenPrints:
    def __enter__(self):
        self._original_stdout = sys.stdout
        sys.stdout = open(os.devnull, 'w')

    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stdout.close()
        sys.stdout = self._original_stdout


def main():
    quts = quts_lib.QUTS("volte_call")
    logging.info('Started QUTS')

    # remove files in client_test folder
    if _TEMP_FOLDER_PATH.exists() and _TEMP_FOLDER_PATH.is_dir():
        shutil.rmtree(_TEMP_FOLDER_PATH)
    os.mkdir(_TEMP_FOLDER_PATH)

    # remove files in client_test folder
    if _FINAL_FOLDER_PATH.exists() and _FINAL_FOLDER_PATH.is_dir():
        shutil.rmtree(_FINAL_FOLDER_PATH)

    diag_service_1 = quts.diag_connect(DUT_MO)
    diag_service_2 = quts.diag_connect(DUT_MT)
    if not diag_service_1 or not diag_service_2:
        raise Exception(f'Could not connect {not diag_service_1 or not diag_service_2} diag')
    logging.info(f'Connected {DUT_MO} diag')
    logging.info(f'Connected {DUT_MT} diag')
    
    # start logging
    logging.info('Started logging')
    quts.diag_log_start()

    # run automation script
    tc2_volte_call()

    log_files = quts.diag_log_save(DUT_MO)
    logging.info('Saved logs')

    # disconnected each device
    for device, diag_service in [(DUT_MO, diag_service_1), (DUT_MT, diag_service_2)]:
        disconnected = quts.diag_disconnect(diag_service)
        if disconnected:
            logging.info(f'Disconnected {device} diag')
        else:
            raise Exception(f'Could not disconnect {device} diag')

    quts.stop()
    logging.info('Stopped QUTS client')

    qcat = qcat_lib.QCAT()
    logging.info('Started QCAT client')

    # set name and path of parsed results file
    path, filename = os.path.split(log_files[0])
    filename = 'tc2_VoLTE_call'
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
    parsed = qcat_lib.parse_log(log_files[0],
                                _TC2_TEST_CONFIG,
                                raw_filepath,
                                parsed_filepath,
                                validated_filepath,
                                validated_csv_filepath,
                                qcat)

    if not parsed:
        raise Exception('QCAT parsing failed')

    logging.info('QCAT parsed log file')
    
    logging.info('Quit QCAT')
    qcat.quit()

    shutil.move(str(_TEMP_FOLDER_PATH), str(_FINAL_FOLDER_PATH))


if __name__ == '__main__':
    format_str = '[%(asctime)s.%(msecs)03d]: %(message)s'
    logging.basicConfig(format=format_str,
                        level=logging.INFO,
                        datefmt='%Y-%m-%d %H:%M:%S')
    main()
