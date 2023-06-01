from collections import defaultdict
import os
import logging
from pathlib import Path
from datetime import datetime
import sys
import signal
import socketio
import eventlet
from asyncio import Future
import asyncio

import quts_lib
import qcat_lib_win as qcat_lib

from db import DB
from session import Session, LogSession, ATSession, TestCase

_BASE_PATH = Path(__file__).parent.resolve()
_LOG_FOLDER_PATH = Path(_BASE_PATH.parent / 'logs')
_TC1_TEST_CONFIG = _BASE_PATH / 'qcat_tests/Test_case_1.json'
_TC2_TEST_CONFIG = _BASE_PATH / 'qcat_tests/Test_case_2.json'


class HiddenPrints:
  def __enter__(self):
    self._original_stdout = sys.stdout
    sys.stdout = open(os.devnull, 'w')

  def __exit__(self, exc_type, exc_val, exc_tb):
    sys.stdout.close()
    sys.stdout = self._original_stdout

sio = socketio.Server()
app = socketio.WSGIApp(sio)
quts = None
qcat = None

sessions = defaultdict(Session)
log_sessions = defaultdict(LogSession)

db = DB()

@sio.event
def QUTS_start(sid, data):
  global quts
  quts = quts_lib.QUTS('qConnect service')
  logging.info('Started QUTS client')
  return {
    'data': {
      'status': 'started QUTS',
    }
  }


@sio.event
def QUTS_diag_connect(sid, data):
    try:
      id, serial, user, app_url, device = data['id'], data['serial'], data['user'], data['appUrl'], data['device']
      
      if 'mask' in data and data['mask'] is not None:
        mask_file = data['mask']
        logging.info(f'Using mask file {mask_file}')
        diag_service = quts.diag_connect(serial, mask_file)
      else:
        diag_service = quts.diag_connect(serial)

      if diag_service:
        logging.info(f'Connected {serial} diag')
      else:
        raise Exception(f'Could not connect {serial} diag')
      
      sessions[id] = LogSession(id, serial, service=diag_service, user=user, app_url=app_url, device=device)
      if 'mask' in data and data['mask'] is not None:
        mask_file = data['mask']
        sessions[id].mask_file = mask_file
      
      return {
        'data': {
          'id': id,
          'status': 'connected diag',
        }
      }
    except Exception as e:
      logging.error(str(e))
      return { 'error': str(e) }


@sio.event
def QUTS_diag_disconnect(sid, data):
  try:
    id = data['id']
    if id not in sessions:
      raise Exception(f'id not found: {id}')
    
    if not sessions[id].service:
      raise Exception(f'Device not connected for id: {id}')

    disconnected = quts.diag_disconnect(sessions[id].service)
    if disconnected:
      logging.info(f'Disconnected {sessions[id].serial} diag')
    else:
      raise Exception(f'Could not disconnect {sessions[id].serial} diag')

    sessions[id].service = None
    return {
      'data': {
        'id': id,
        'status': 'disconnected diag',
      }
    }
  except Exception as e:
    logging.error(e)
    return { 'error': str(e) }


@sio.event
def QUTS_log_start(sid, data):
  try:
    id, log_id = data['id'], data['log_id']
    if id not in sessions:
      raise Exception(f'id not found: {id}')
    
    session = sessions[id]
    if not session.service:
      raise Exception(f'No service for id: {id}')

    quts.diag_log_start()
    logging.info('Started logging')

    session.log_id = log_id
    session.start_log_timestamp = get_current_timestamp()
    log_sessions[log_id] = session

    return {
      'data': {
        'id': id,
        'logId': log_id,
        'startLogTimestamp': session.start_log_timestamp.isoformat(),
        'status': 'started logging',
      }
    }
  except Exception as e:
    logging.error(e)
    return { 'error': str(e) }


@sio.event
def QUTS_log_stop(sid, data):
  try:
    log_id = data['log_id']
    if log_id not in log_sessions:
      raise Exception(f'log_id not found: {log_id}')
    if not log_sessions[log_id].service:
      raise Exception(f'No service for log_id: {log_id}')

    log_files = quts.diag_log_save(log_sessions[log_id].serial)
    logging.info('Saved logs')

    log_sessions[log_id].raw_logs = log_files
    log_sessions[log_id].end_log_timestamp = get_current_timestamp()
    logging.info(log_sessions[log_id].raw_logs)

    return {
      'data': {
        'id': log_sessions[log_id].id,
        'logId': log_id,
        'logFile': log_sessions[log_id].raw_logs[0],
        'startLogTimestamp': log_sessions[log_id].start_log_timestamp.isoformat(),
        'endLogTimestamp': log_sessions[log_id].end_log_timestamp.isoformat(),
        'status': 'saved log',
      }
    }
  except Exception as e:
    logging.error(e)
    return { 'error': str(e) }


@sio.event
def QUTS_stop(sid, data):
  global quts
  if not quts:
    logging.info('QUTS not running')
    return {
      'data': {
        'status': 'QUTS not running',
      }
    }
  
  quts.stop()
  quts = None
  logging.info('Stopped QUTS client')

  return {
    'data': {
      'status': 'stopped QUTS',
    }
  }


@sio.event
def QCAT_start(sid, data):
  global qcat
  try:
    qcat = qcat_lib.QCAT()
    logging.info('Started QCAT client')
    return {
      'data': {
        'status': 'started QCAT',
      }
    }
  except Exception as e:
    logging.error("Could not start QCAT client")
    logging.error(e)


@sio.event
def QCAT_process(sid, data):
  try:
    log_id, test_case = data['log_id'], data['test_case']
    if log_id not in log_sessions:
      raise Exception(f'log_id not found: {log_id}')
    
    log_session = log_sessions[log_id]

    log_file = log_session.raw_logs[0]  # USE FIRST LOG FILE

    test_config = None
    filename = None
    if test_case == 'TC1':
      test_config = _TC1_TEST_CONFIG
      log_session.test_case = TestCase.TC1
      filename = 'TC1_LTE_latch'
    elif test_case == 'TC2':
      test_config = _TC2_TEST_CONFIG
      log_session.test_case = TestCase.TC2
      filename = 'TC2_VoLTE_call_MO'
    else:
      raise Exception(f'Unknown test case: {test_case}')

    # path, filename = os.path.split(log_file)
    # filename = 'tc1_lte_latch'
    # raw_filename = f'result_raw_{filename}.txt'
    # raw_filepath = os.path.join(path, raw_filename)
    # parsed_filename = f'result_parsed_{filename}.txt'
    # parsed_filepath = os.path.join(path, parsed_filename)
    # validated_filename = f'result_validated_{filename}.txt'
    # validated_filepath = os.path.join(path, validated_filename)
    # validated_csv_filename = f'result_validated_{filename}.csv'
    # validated_csv_filepath = os.path.join(path, validated_csv_filename)

    # set name and path of parsed results file
    folder = Path(log_file).parent
    raw_filepath = str(folder / f'result_raw_{filename}.txt')
    parsed_filepath = str(folder / f'result_parsed_{filename}.txt')
    validated_filepath = str(folder / f'result_validated_{filename}.txt')
    validated_csv_filepath = str(folder / f'result_validated_{filename}.csv')

    # call QCAT library on the log file which needs parsing
    logging.info('QCAT parsing log file')
    parsed = qcat_lib.parse_log(log_file,
                                test_config,
                                raw_filepath,
                                parsed_filepath,
                                validated_filepath,
                                validated_csv_filepath,
                                qcat)
    
    log_session.validated_logs = validated_csv_filepath

    if not parsed:
      raise Exception(f'QCAT parsing failed for log_id: {log_id}')

    logging.info('QCAT parsed log file')

    return {
      'data': {
        'id': log_sessions[log_id].id,
        'log_id': log_id,
        'status': 'successfully processed log',
      }
    }
  except Exception as e:
    logging.error(e)
    return { 'error': str(e) }

@sio.event
def QCAT_parse_all(sid, data):
  try:
    log_id = data['log_id']
    if log_id not in log_sessions:
      raise Exception(f'log_id not found: {log_id}')
      
    if not qcat:
      raise Exception('QCAT not running...')
    
    log_session = log_sessions[log_id]

    log_file = log_session.raw_logs[0]  # USE FIRST LOG FILE

    filename = Path(log_file).stem
    folder = Path(log_file).parent
    raw_filepath = str(folder / f'parsed_raw_{filename}.txt')
    json_filepath = str(folder / f'parsed_json_{filename}.json')

    # call QCAT library on the log file which needs parsing
    logging.info('QCAT parsing log file')
    
    def parse(future: Future):
      parsedJsonArr = qcat_lib.parse_raw_log_json(log_file,
                                json_filepath,
                                qcat)
      if not parsedJsonArr:
        raise Exception(f'QCAT raw JSON parsing failed for log_id: {log_id}')
      print('QCAT parsed log file')
      
      insertLogsResult = db.insert_logs(parsedJsonArr, log_session)
      print(f'Inserted {len(insertLogsResult.inserted_ids)} to db')
      
      sio.emit("QCAT_parse_done", {
        'data': {
          'id': log_sessions[log_id].id,
          'log_id': log_id,
          'startLogTimestamp': log_session.start_log_timestamp.isoformat(),
          'endLogTimestamp': log_session.end_log_timestamp.isoformat(),
          'jsonFile': json_filepath,
          'packetCount': len(parsedJsonArr),
          'insertedCount': len(insertLogsResult.inserted_ids),
          'status': 'Parsing success',
        }
      })
      
      future.set_result(True)
      
    parse_future = Future()
    asyncio.create_task(parse(parse_future))
    
    return {
      'data': {
        'id': log_sessions[log_id].id,
        'log_id': log_id,
        'startLogTimestamp': log_session.start_log_timestamp.isoformat(),
        'endLogTimestamp': log_session.end_log_timestamp.isoformat(),
        'jsonFile': json_filepath,
        'status': 'Parsing started',
      }
    }
    
    # DISABLE TEXT PARSING 
    # parsedText = qcat_lib.parse_raw_log(log_file,
    #                             raw_filepath,
    #                             qcat)
    # if not parsedText:
    #   raise Exception(f'QCAT raw text parsing failed for log_id: {log_id}')
      
  except Exception as e:
    logging.error(e)
    return { 'error': str(e) }


@sio.event
def get_log(sid, data):
  try:
    log_id = data['log_id']

    if log_id in log_sessions and log_sessions[log_id].validated_logs:
      test_case = 'TC1' if log_sessions[log_id].test_case == TestCase.TC1 else 'TC2'
      return {
        'data': {
          'filepath' : log_sessions[log_id].validated_logs,
          'test_case':  test_case,
        }
      }
    elif log_id in log_sessions:
      raise Exception(f'Log not processed for log_id: {log_id}')
    else:
      raise Exception(f'log_id not found: {log_id}')
  except Exception as e:
    logging.error(e)
    return { 'error': str(e) }


@sio.event
def QCAT_stop(sid, data):
  global qcat
  if not qcat:
    logging.info('QCAT not running')
    return {
      'data': {
        'status': 'QCAT not running',
      }
    }

  qcat.quit()
  qcat = None
  logging.info('Stopped QCAT client')

  return {
    'data': {
      'status': 'stopped QCAT',
    }
  }


@sio.event
def AT_start(sid, data):
  try:
    id, serial = data['id'], data['serial']
    raw_service = quts.AT_connect(serial)

    if raw_service:
      logging.info(f'Connected {serial} for AT commands')
    else:
      raise Exception(f'Could not connect {serial} for AT commands')

    sessions[id] = ATSession(id, service=raw_service, serial=serial)
    
    return {
      'data': {
        'id': id,
        'status': 'connected serial',
      }
    }
  except Exception as e:
    logging.error(e)
    return { 'error' : str(e) }


@sio.event
def AT_stop(sid, data):
  try:
    id = data['id']

    if id not in sessions:
      raise Exception(f'id not found: {id}')

    log_item = sessions[id]

    if not log_item.service:
      raise Exception(f'Device not connected for id: {id}')

    disconnected = quts.AT_disconnect(log_item.service)
    if disconnected:
      logging.info(f'Disconnected {log_item.serial} for AT commands')
    else:
      raise Exception(f'Could not disconnect {log_item.serial} for AT commands')
    
    log_item.service = None

    return {
      'data': {
        'id': id,
        'status': 'disconnected serial',
      }
    }
  except Exception as e:
    logging.error(e)
    return { 'error': str(e) }


@sio.event
def AT_send(sid, data):
  try:
    id = data['id']

    if id not in sessions:
      raise Exception(f'id not found: {id}')

    raw_service = sessions[id].service
    if not raw_service:
      raise Exception(f'No service for id: {id}')

    response = []
    for cmd in data['commands']:
      response.append({
        'command': cmd,
        'response': quts.AT_send_command(raw_service, cmd)
      })
    
    return { 'data': response }
  except Exception as e:
    logging.error(e)
    return { 'error': str(e) }


@sio.event
def stop_all(sid, data):
  logging.info('stopping all child processes')
  QUTS_stop(None, None)
  QCAT_stop(None, None)
  return True


@sio.on('*')
def catch_all(event, sid, data):
  print('catch_all', event, sid, data)
  pass


@sio.event
def connect(sid, environ, auth):
  print('connect ', sid)
  pass


@sio.event
def disconnect(sid):
  print('disconnect ', sid)
  pass



def get_current_timestamp():
  return datetime.now()

def signal_handler(sig, frame):
  logging.info('Ctrl+C detected')
  QUTS_stop(None, None)
  QCAT_stop(None, None)
  sys.exit(0)


def main():
  QUTS_start(None, None)
  QCAT_start(None, None)
  signal.signal(signal.SIGINT, signal_handler)
  signal.signal(signal.SIGTERM, signal_handler)
  eventlet.wsgi.server(eventlet.listen(('', 6001)), app)


if __name__ == '__main__':
  format_str = '[%(asctime)s.%(msecs)03d]: %(message)s'
  logging.basicConfig(format=format_str,
                      level=logging.INFO,
                      datefmt='%Y-%m-%d %H:%M:%S')
  main()

