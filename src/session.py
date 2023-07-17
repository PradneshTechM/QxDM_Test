import dataclasses
import sys
from datetime import datetime
from typing import List, Any
from enum import Enum
from pymongo import MongoClient, GEO2D
import traceback

from db import DB

class TestCase(Enum):
  TC1 = 0
  TC2 = 1
  
@dataclasses.dataclass
class Session:
  id: str
  serial: str
  service: Any
  start_log_timestamp: datetime = None
  end_log_timestamp: datetime = None
  user: Any = None
  app_url: str = None
  device: Any = None

class LogSession(Session):
  log_id: str = None
  mask_file: str = None
  config_file: str = None
  raw_logs: List[str] = None
  validated_logs: List[str] = None
  test_case: TestCase = None
  test_case_id: str = None
  db: str = None
  collection: str = None
  db_client: MongoClient = None
  
  def init_db_connection(self):
    self.db_client = DB.get_default_client()
    try:
      print("Initializing database connection")
      sys.stdout.flush()
      if self.db: 
        self.db_instance = self.db_client.get_database(self.db)
        print(self.db_instance)
        sys.stdout.flush()
      else:
        self.db_instance = DB.get_instance()
    except:
      traceback.print_exc()
      sys.stdout.flush()
      
class ATSession(Session):
  pass