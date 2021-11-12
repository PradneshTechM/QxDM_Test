#!/usr/bin/env python3.7
import logging
import os
from pathlib import Path
import shutil
import sys
import time

import quts_lib
import qcat_lib_win as qcat_lib
from qcat_tests.tc1_lte_latch_tmdc import main as tc1_lte_latch

_BASE_PATH = Path(__file__).parent.resolve()
_TEMP_FOLDER_PATH = Path(_BASE_PATH.parent / 'temp')
_FINAL_FOLDER_PATH = (_BASE_PATH.parent / 'TC1_lte_latch_logs')
_TC1_TEST_CONFIG = _BASE_PATH / 'qcat_tests/Test_case_1.json'

DUT = '94KBA0090A'

class HiddenPrints:
    def __enter__(self):
        self._original_stdout = sys.stdout
        sys.stdout = open(os.devnull, 'w')

    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stdout.close()
        sys.stdout = self._original_stdout


def main():
  quts = quts_lib.QUTS("lte_latch")
  logging.info('Started QUTS')

  # remove files in client_test folder
  if _TEMP_FOLDER_PATH.exists() and _TEMP_FOLDER_PATH.is_dir():
      shutil.rmtree(_TEMP_FOLDER_PATH)
  os.mkdir(_TEMP_FOLDER_PATH)

  # remove files in client_test folder
  if _FINAL_FOLDER_PATH.exists() and _FINAL_FOLDER_PATH.is_dir():
      shutil.rmtree(_FINAL_FOLDER_PATH)

  # connect to device diag
  diag_service = quts.diag_connect(DUT)
  
  if diag_service:
    logging.info(f'Connected {DUT} diag')
  else:
    raise Exception(f'Could not connect {DUT} diag')

  logging.info('Started logging')
  quts.diag_log_start()

  # run automation script
  tc1_lte_latch(DUT)

  log_files = quts.diag_log_save(DUT)
  logging.info('Saved logs')

  disconnected = quts.diag_disconnect(diag_service)
  if disconnected:
    logging.info(f'Disconnected {DUT} diag')
  else:
    raise Exception(f'Could not disconnect {DUT} diag')
  
  quts.stop()
  logging.info('Stopped QUTS client')

  qcat = qcat_lib.QCAT()
  logging.info('Started QCAT client')

  # set name and path of parsed results file
  path, filename = os.path.split(log_files[0])  # USE FIRST LOG FILE
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
  parsed = qcat_lib.parse_log(log_files[0],
                              _TC1_TEST_CONFIG,
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
