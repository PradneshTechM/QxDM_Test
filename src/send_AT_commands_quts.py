#!/usr/bin/env python3.7
import logging
import os
import sys
import time

import quts_lib

DUT = '94KBA0090A'

class HiddenPrints:
    def __enter__(self):
        self._original_stdout = sys.stdout
        sys.stdout = open(os.devnull, 'w')

    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stdout.close()
        sys.stdout = self._original_stdout


def main(serial, commands):
  quts = None
  raw_service = None

  with HiddenPrints():
    quts = quts_lib.QUTS("QUTS Raw Service AT command")
    logging.info('Started QUTS')

    # connect to raw service to send AT commands
    raw_service = quts.AT_connect(serial)
    
    if raw_service:
      logging.info(f'Connected {serial} for AT commands')
    else:
      raise Exception(f'Could not connect {serial} for AT commands')

    for cmd in commands:
      response = quts.AT_send_command(raw_service, cmd)
      logging.info(f'AT Send>> {cmd}')
      logging.info(f'AT Response<< {response}')
      time.sleep(1)
    
    disconnected = quts.AT_disconnect(raw_service)
    if disconnected:
      logging.info(f'Disconnected {serial} for AT commands')
    else:
      raise Exception(f'Could not disconnect {serial} for AT commands')
    
    quts.stop()
    logging.info('Stopped QUTS client')


if __name__ == '__main__':
    format_str = '[%(asctime)s.%(msecs)03d]: %(message)s'
    logging.basicConfig(format=format_str,
                        level=logging.INFO,
                        datefmt='%Y-%m-%d %H:%M:%S')
    
    serial, *commands = sys.argv[1:] or [DUT, 'AT', 'ATI', 'AT+CGSN']
    logging.info(f'serial: {serial}, AT commands: {commands}')
    main(serial, commands)
