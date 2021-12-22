import os
import sys
import time
from typing import List
import re
from pathlib import Path
import collections
import dataclasses
import datetime

# The path where QUTS files are installed
if sys.platform == 'linux' or sys.platform == 'linux2':
  sys.path.append('/opt/qcom/QUTS/Support/python')
else:
  sys.path.append('C:\Program Files (x86)\Qualcomm\QUTS\Support\python')

import QutsClient
import Common.ttypes

import DiagService.DiagService
import DiagService.constants
import DiagService.ttypes

import RawService.RawService
import RawService.constants
import RawService.ttypes

import QXDMService.QxdmService
import QXDMService.constants
import QXDMService.ttypes


_BASE_PATH = Path(__file__).parent.resolve()
_LOG_FOLDER_PATH = (_BASE_PATH.parent / 'logs')
LOGMASK_FILEPATH = _BASE_PATH.parent / 'default.dmc'


class QUTS:
  def __init__(self, name: str):
    self.client = self._start_quts_client(name)

    # device manager has all device related info
    self.device_manager = self.client.getDeviceManager()


  def _start_quts_client(self, name):
    client = None
    try:
      client = QutsClient.QutsClient(name)
    except Exception as e:
      print('Exception starting client')
    if client:
      print('Initialized client')
    else:
      print('Client did not instantiate')
    return client


  def _get_device_protocols(self, serial: str):
    '''Returns device info for a given serial number'''
    device_list = self.device_manager.getDeviceList()
    for device in device_list:
      if serial == device.adbSerialNumber:
        return device.protocols
    else:
      raise KeyError('Input serial is not found in QUTS')


  def AT_connect(self, serial: str) -> RawService.RawService.Client:
    '''
    Reference: Qualcomm's "KBA-201116084941 How to send AT command with QUTS automation"
    '''
    if not serial or serial == '':
      raise ValueError('Input serial cannot be None or empty string')
    
    protocols = self._get_device_protocols(serial)

    raw_service = None
    unknown_protocol = None
    # check device has default protocol for modem port
    for p in protocols:
      if "Modem" in p.description:
        print(f'Found HS-USB Modem Protocol handle, Description {p.description} ProtocolHandle: {p.protocolHandle}')
        unknown_protocol = p
        break
    else:
      raise ValueError('Input serial found but default protocol for modem port not found in QUTS')

    # try to override the default UNKNOWN protocol with DUN for modem port
    self.device_manager.overrideUnknownProtocol(unknown_protocol.protocolHandle, Common.ttypes.ProtocolType.PROT_DUN)

    # create QUTS service
    raw_service = RawService.RawService.Client(self.client.createService(RawService.constants.RAW_SERVICE_NAME, unknown_protocol.deviceHandle))

    # associate device with QUTS service
    if raw_service.initializeService(unknown_protocol.protocolHandle, 3, 3):
      raise ConnectionError(f'AT connect failed for serial: {serial}, device handle: {unknown_protocol.deviceHandle}, procotol: {unknown_protocol.protocolHandle}')

    print(f'AT connect succeeded for serial: {serial}, device handle: {unknown_protocol.deviceHandle}, protocol: {unknown_protocol.protocolHandle}')

    return raw_service


  def AT_send_command(self, raw_service: RawService.RawService.Client, cmd: str) -> str:
    '''Sends AT commands'''
    cmd = f'\r\n{cmd}\r'
    input = bytearray(cmd, encoding='utf-8')
    output = raw_service.sendRequest(input, 2000)
    return output.decode('utf-8')


  def AT_disconnect(self, raw_service: RawService.RawService.Client) -> bool:
    '''Stops rawService instance.'''
    error_code = raw_service.destroyService()
    if error_code:
      print('Error stopping diagSerice instance:', error_code)
      return False
    else:
      print('diagService instance stopped')
      return True


  def diag_connect(self, serial: str, logmask_filepath=LOGMASK_FILEPATH) -> DiagService.DiagService.Client:
    '''Connects to given device diag with serial number with given filepath to logmask.  Default logmask is used if none is provided.'''
    if not serial or serial == '':
      raise ValueError('Input serial cannot be None or empty string')

    protocols = self._get_device_protocols(serial)

    diag_service = None
    diag_protocol = None
    # check device has diag protocol
    for p in protocols:
      if p.protocolType == 0:  # diag type
        diag_protocol = p
        break
    else:
      raise ValueError('Input serial found but diag protocol not found in QUTS')

    diag_service = DiagService.DiagService.Client(self.client.createService(DiagService.constants.DIAG_SERVICE_NAME, diag_protocol.deviceHandle))

    if diag_service.initializeServiceByProtocol(diag_protocol.protocolHandle):
      raise ConnectionError(f'Diag connect failed for serial: {serial}, device handle: {diag_protocol.deviceHandle}, procotol: {diag_protocol.protocolHandle}')

    diag_service.setLoggingMask(QutsClient.readFile(logmask_filepath), Common.ttypes.LogMaskFormat.DMC_FORMAT)

    print(f'Diag connect succeeded for serial: {serial}, device handle: {diag_protocol.deviceHandle}, protocol: {diag_protocol.protocolHandle}')

    return diag_service


  def diag_disconnect(self, diag_service: DiagService.DiagService.Client) -> bool:
    '''Stops diagService instance.'''
    error_code = diag_service.destroyService()
    if error_code:
      print('Error stopping diagSerice instance:', error_code)
      return False
    else:
      print('diagService instance stopped')
      return True


  def is_connected(self, serial, diag_service: DiagService.DiagService.Client) -> bool:
    '''Returns True if device with serial number is connected to diag.'''
    device_handle = diag_service.getDevice()
    
    device_list = self.device_manager.getDeviceList()
    for device in device_list:
      if serial == device.adbSerialNumber and device_handle == device.deviceHandle:
        print(f'{serial} is connected')
        return True

    print(f'{serial} is not connected')
    return False


  def diag_log_start(self):
    print('Log started')
    self.device_manager.startLogging()


  def diag_log_save(self, *args: str) -> List[str]:
    '''Saves separate log files for given serial numbers passed .'''
    filenames = {}  # maps (key: protocol handle, value: file path)
    for serial in args:
      now = datetime.datetime.now()
      dt_format = now.strftime("%y%m%d_%H%M%S.%f")
      prefix = f'{dt_format}_{serial}'
      path = f'{_LOG_FOLDER_PATH}/{prefix}/{prefix}.hdf'

      protocol_handle = None
      for protocol in self._get_device_protocols(serial):
        if protocol.protocolType == 0:  # diag type
          protocol_handle = protocol.protocolHandle
          break
      else:
        raise Exception(f'Could not find {serial} diag')

      filenames[protocol_handle] = path

    files = self.device_manager.saveLogFilesWithFilenames(filenames)
    
    print('Log(s) saved:')
    for fn in files:
      print(f'\t{fn}')

    return files


  def diag_log_reset(self):
    '''Resets the log.'''
    print('Resetting logs')
    self.device_manager.resetLogFiles()


  def stop(self):
    '''Stops QUTS client.'''
    print('QUTS client stopped')
    self.client.stop()


def test():
  DUT1 = '94KBA0090A'
  DUT2 = '96041FFBA0007B'

  quts = QUTS('test')

  diag_service_1 = quts.diag_connect(DUT1)
  diag_service_2 = quts.diag_connect(DUT2)

  quts.diag_log_start()

  time.sleep(5)

  quts.diag_log_save(DUT1)

  quts.diag_log_reset()

  time.sleep(10)
  
  quts.diag_log_save(DUT1, DUT2)

  quts.is_connected(DUT1, diag_service_1)
  quts.is_connected(DUT2, diag_service_2)
  quts.is_connected(DUT1 + 'a', diag_service_1)

  quts.stop()


if __name__ == '__main__':
  test()
