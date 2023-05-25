from pymongo import MongoClient
from pymongo.errors import BulkWriteError

from session import LogSession

class DB:
  _DB_NAME = "QXDM"
  _DB_HOST = 'localhost'
  _DB_PORT = 27017
  
  _DB_CLIENT = None
  _DB_INSTANCE = None

  def __init__(self):
    print(f'Initializing database instance @{DB._DB_HOST}:{DB._DB_PORT }')
    if not DB._DB_CLIENT:
      DB._DB_CLIENT = MongoClient(DB._DB_HOST, DB._DB_PORT)
    if not DB._DB_INSTANCE:
      DB._DB_INSTANCE = DB._DB_CLIENT[DB._DB_NAME]
    print('Initialized database instance!')
    
  def get_instance():
    return DB._DB_INSTANCE

  def insert_logs(self, logs: list, log_session: LogSession):
    logs_collection = DB._DB_INSTANCE["logs"]
    
    def deserialize(log): 
      log["logID"] = log_session.log_id
      log["serial"] = log_session.serial
      log["startLogTimestamp"] = log_session.start_log_timestamp
      log["endLogTimestamp"] = log_session.end_log_timestamp
      log["maskFile"] = log_session.mask_file
      log["url"] = log_session.app_url
      log["user"] = {
        "name": log_session.user.name,
        "email": log_session.user.email
      }
      return log
    
    deserialized_logs = list(map(deserialize, logs))
    
    try:
      result = logs_collection.insert_many(deserialized_logs)
      print("Inserted logs to db")
      return result
    except BulkWriteError as bwe:
      print(bwe.details)
      print(bwe.details['writeErrors'])
      raise
      
    
    