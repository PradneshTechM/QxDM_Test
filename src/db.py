import sys
import os
from pymongo import MongoClient, GEO2D
from pymongo.errors import BulkWriteError

from session import LogSession

class DB:
  _DB_NAME = os.environ.get("DB_NAME") if os.environ.get("DB_NAME") else "qxdm_dev"
  _DB_HOST = os.environ.get("DB_HOST")
  _DB_USER = os.environ.get("DB_USER")
  _DB_PASS = os.environ.get("DB_PASS")
  _DB_PORT = os.environ.get("DB_PORT")
  _DB_TABLE = os.environ.get("DB_TABLE") if os.environ.get("DB_TABLE") else "logs"
  
  _DB_CLIENT = None
  _DB_INSTANCE = None

  def __init__(self):
    if not DB._DB_CLIENT:
      if not DB._DB_HOST:
        # remote db not defined, use local db
        print(f'Initializing database instance @localhost:27017')
        DB._DB_CLIENT = MongoClient("localhost", 27017)
      else:
        print(f'Initializing database instance @{DB._DB_HOST}:{DB._DB_PORT}')
        DB._DB_CLIENT = MongoClient(DB._DB_HOST, int(DB._DB_PORT), username=DB._DB_USER, password=DB._DB_PASS, authSource=DB._DB_NAME)
    if not DB._DB_INSTANCE:
      DB._DB_INSTANCE = DB._DB_CLIENT[DB._DB_NAME]
    print(f'Initialized database instance {DB._DB_NAME}')
    
    self._create_indexes()
    
  def _create_indexes(self): 
    DB._DB_INSTANCE[DB._DB_TABLE].create_index([("_server.location", GEO2D)])
    
  def get_instance():
    return DB._DB_INSTANCE

  def insert_logs(self, logs: list, log_session: LogSession):
    logs_collection = DB._DB_INSTANCE[DB._DB_TABLE]
    
    def deserialize(log): 
      metadata = {}
      metadata["_logID"] = log_session.log_id
      metadata["_device"] = {
        "serial": log_session.serial,
        "manufacturer": log_session.device["manufacturer"] if log_session.device and "manufacturer" in log_session.device else "",
        "model": log_session.device["model"] if log_session.device and "model" in log_session.device else "",
        "software": f'{log_session.device["platform"] if "platform" in log_session.device else ""} {log_session.device["sdk"] if "sdk" in log_session.device else ""}' if log_session.device else "",
        "imei": log_session.device["phone"]["imei"] if log_session.device and "phone" in log_session.device and "imei" in log_session.device["phone"] else "",
      }
      if log_session.start_log_timestamp:
        metadata["_startLogTimestamp"] = log_session.start_log_timestamp
      if log_session.end_log_timestamp:
        metadata["_endLogTimestamp"] = log_session.end_log_timestamp
      if log_session.mask_file:
        metadata["_maskFile"] = log_session.mask_file
      metadata["_filePath"] = log_session.raw_logs[0]
      if log_session.device:
        metadata["_server"] = {
          "url": log_session.app_url,
          "location": [log_session.device["location"]["longitude"] if "location" in log_session.device and "longitude" in log_session.device["location"] else 0,
              log_session.device["location"]["latitude"] if "location" in log_session.device and "latitude" in log_session.device["location"] else 0
          ]
        }
      if log_session.user:
        metadata["_user"] = {
          "name": log_session.user["name"] if log_session.user["name"] else "",
          "email": log_session.user["email"] if log_session.user["email"] else ""
        }
      return { **metadata, **log }
    
    deserialized_logs = list(map(deserialize, logs))
    
    try:
      result = logs_collection.insert_many(deserialized_logs)
      print("Inserted logs to db")
      return result
    except BulkWriteError as bwe:
      print(bwe.details)
      print(bwe.details['writeErrors'])
      raise
    finally:
      sys.stdout.flush()
      sys.stderr.flush()
      
    
    