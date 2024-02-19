from dotenv import load_dotenv
load_dotenv()

from collections import defaultdict
import os
import traceback
import logging
import time
from pathlib import Path
from datetime import datetime
import sys
import win32com.client
import pythoncom
import signal
import socketio
import eventlet
from asyncio import Future
import asyncio
import argparse
import json
from pubsub import pub
import multiprocessing
queue = multiprocessing.Queue()
import psutil
import quts_lib
import qcat_lib_win as qcat_lib

from db import DB
from session import Session, LogSession, ATSession, TestCase
from exception import QConnectException
worker = {}

_BASE_PATH = Path(__file__).parent.resolve()
_LOG_FOLDER_PATH = Path(_BASE_PATH.parent / 'logs')
_TC1_TEST_CONFIG = _BASE_PATH / 'qcat_tests/Test_case_1.json'
_TC2_TEST_CONFIG = _BASE_PATH / 'qcat_tests/Test_case_2.json'
_CERT_PATH = os.environ.get("CERT_PATH")
_KEY_PATH = os.environ.get("KEY_PATH")


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
  try:
    global quts
    quts = quts_lib.QUTS('qConnect service')
    logging.info('Started QUTS client')
    return {
      'data': {
        'status': 'started QUTS',
      }
    }
  except Exception as e:
    raise QConnectException(QConnectException.Codes.QUTS, f"Could not start QUTS client: {e}")
    


@sio.event
def QUTS_diag_connect(sid, data):
    if not quts:
      return { 'error': str(QConnectException(QConnectException.Codes.QUTS, "QUTS not running")) }
    
    try:
      id, serial, user, app_url, device = data['id'], data['serial'], data['user'], data['appUrl'], data['device']
      
      if 'mask' in data and data['mask'] is not None:
        mask_file = data['mask']
        logging.info(f'Using mask file {mask_file}')
      else:
        mask_file = None
        
      if 'packets' in data and data['packets'] is not None:
        packets = data['packets']
        logging.info(f'Using packet type list ({len(packets)} packets)')
      else:
        packets = None
        
      diag_service = quts.diag_connect(serial, packets, mask_file)

      if diag_service:
        logging.info(f'Connected {serial} diag')
      else:
        raise Exception(f'Could not connect {serial} diag')
      sys.stdout.flush()
      
      sessions[id] = LogSession(id, serial, service=diag_service, user=user, app_url=app_url, device=device)
      
      if 'mask' in data and data['mask'] is not None:
        mask_file = data['mask']
        sessions[id].mask_file = mask_file
      if 'config' in data and data['config'] is not None:
        config_file = data['config']
        logging.info(f'Using config file {config_file}')
        sys.stdout.flush()
        sessions[id].config_file = config_file
        
      if 'testCaseID' in data and data['testCaseID'] is not None:
        test_case_id = data['testCaseID']
        logging.info(f'Test case: {test_case_id}')
        sys.stdout.flush()
        sessions[id].test_case_id = test_case_id
        
      if 'db' in data and data['db'] is not None:
        logging.info(f'Using database: {data["db"]}')
        sys.stdout.flush()
        sessions[id].db = data['db']
        
      if 'collection' in data and data['collection'] is not None:
        logging.info(f'Using collection: {data["collection"]}')
        sys.stdout.flush()
        sessions[id].collection = data["collection"]
        
      sessions[id].init_db_connection()
      
      return {
        'data': {
          'id': id,
          'status': 'connected diag',
          'services': get_services_status()
        }
      }
    except Exception as e:
      traceback.print_exc()
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
        'services': get_services_status()
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
        'services': get_services_status()
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

    user = log_sessions[log_id].user
    user_id = user["email"].split('@', 1)[0]
    log_file_paths, log_file_names = quts.diag_log_save(user_id, log_id, log_sessions[log_id].serial)
    logging.info('Saved logs')

    log_sessions[log_id].raw_logs = log_file_paths
    log_sessions[log_id].end_log_timestamp = get_current_timestamp()
    logging.info(log_sessions[log_id].raw_logs)

    return {
      'data': {
        'id': log_sessions[log_id].id,
        'logId': log_id,
        'logFilePath': log_sessions[log_id].raw_logs[0],
        'logFileName': log_file_names[0],
        'startLogTimestamp': log_sessions[log_id].start_log_timestamp.isoformat(),
        'endLogTimestamp': log_sessions[log_id].end_log_timestamp.isoformat(),
        'status': 'saved log',
        'services': get_services_status()
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
    raise QConnectException(QConnectException.Codes.QCAT, f"Could not start QCAT client: {e}")


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
  
def parse_in_background(log_id, log_session, log_file, json_filepath):
  #  thread management system
  try:
   free_memory = psutil.virtual_memory().available
  except FileNotFoundError:
   free_memory = 3221225500
  qc = win32com.client.Dispatch("QCAT6.Application")
  if queue.empty() and free_memory > 3221225472:
   
    worker[log_id] = qcat_lib.QCATWorker(qc, log_id, log_session, log_file, json_filepath)
    worker[log_id].start()
  else:
    queue.put({log_id, log_session, log_file, json_filepath})
  while not queue.empty():
    try:
      free_memory = psutil.virtual_memory().available
    except FileNotFoundError:
      free_memory = 3221225500
    if free_memory > 3221225472:
      values =  queue.get()
      worker[log_id] = qcat_lib.QCATWorker(qc, values.log_id, values.log_session, values.log_file, values.json_filepath)
      worker[log_id].start()
    time.sleep(60)
@sio.event
def QCAT_parse_all(sid, data):
  if not qcat:
    return { 'error': str(QConnectException(QConnectException.Codes.QCAT, "QCAT not running")) }
  
  try:
    log_id = data['log_id']
    if log_id not in log_sessions:
      raise Exception(f'log_id not found: {log_id}')
      
    log_session = log_sessions[log_id]

    log_file = log_session.raw_logs[0]  # USE FIRST LOG FILE

    filename = Path(log_file).stem
    folder = Path(log_file).parent
    raw_filepath = str(folder / f'parsed_raw_{filename}.txt')
    json_filepath = str(folder / f'parsed_json_{filename}.json')

    # call QCAT library on the log file which needs parsing
    logging.info('QCAT parsing log file')
    
    parse_in_background(log_id, log_session, log_file, json_filepath)
    
    return {
      'data': {
        'id': log_sessions[log_id].id,
        'log_id': log_id,
        'startLogTimestamp': log_session.start_log_timestamp.isoformat(),
        'endLogTimestamp': log_session.end_log_timestamp.isoformat(),
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

def get_services_status():
  return {
    "QUTS": not not quts,
    "QCAT": not not qcat
  }

def signal_handler(sig, frame):
  logging.info('Ctrl+C detected')
  QUTS_stop(None, None)
  QCAT_stop(None, None)
  sys.exit(0)

def parse_args():
  parser = argparse.ArgumentParser("qConnect_service")
  parser.add_argument("--env", help="The running environment of the server (dev/prod).", type=str, default="development")
  return parser.parse_args()

def main():
  args = parse_args()
  
  try:
    QUTS_start(None, None)
  except QConnectException as quts_exception:
    logging.error(f"ERROR QUTS_start {quts_exception}")
    sys.stdout.flush()
    sys.stderr.flush()
  try:
    QCAT_start(None, None)
  except QConnectException as qcat_exception:
    logging.error(f"ERROR QCAT_start {qcat_exception}")
    sys.stdout.flush()
    sys.stderr.flush()
    
  signal.signal(signal.SIGINT, signal_handler)
  signal.signal(signal.SIGTERM, signal_handler)
  
  # init websocket server and wrap it in ssl config if running in prod environment
  logging.info(f'Service running in {args.env} mode')
  listen = eventlet.listen(('', 6001))
  eventlet.wsgi.server(
    (
      listen 
        # if args.env == "development" else ( eventlet.wrap_ssl(
        #   listen, 
        #   certfile=_CERT_PATH,
        #   keyfile=_KEY_PATH,
        #   server_side=True
        # ))
    ), app
  )

if __name__ == '__main__':
  format_str = '[%(asctime)s.%(msecs)03d]: %(message)s'
  logging.basicConfig(format=format_str,
                      level=logging.INFO,
                      datefmt='%Y-%m-%d %H:%M:%S')
  main()

