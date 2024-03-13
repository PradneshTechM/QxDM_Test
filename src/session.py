import dataclasses
import sys
from datetime import datetime
from typing import List, Any
from enum import Enum
from pymongo import MongoClient, GEO2D
import traceback
import json

from db import DB

class TestCase(Enum):
  TC1 = 0
  TC2 = 1
  
@dataclasses.dataclass
class Session:
  id: str
  serial: str
  service: Any = None
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
  packet_types: List[str] = []
  test_case: TestCase = None
  test_case_id: str = None
  execution_id: str = None
  iteration_id: str = None
  db: str = None
  collection: str = None
  db_client: MongoClient = None
  packet_config_json: dict = {}
  packet_frequency: dict = {}
  
  def parse_config_json(self):
    try:
        with open("./parser/input.json", 'r') as f:
            unparsed_config = json.load(f)
            for key, value in unparsed_config.items():
                splited_key = key.split("--")
                packet_type = splited_key[0].strip()
                packet_name = None
                if len(splited_key) > 1: packet_name = splited_key[1].strip()
                packet_subtitle = None
                if len(splited_key) > 2: packet_subtitle = splited_key[2].strip()
                val = {
                    "packet_type": packet_type
                    # "fields": value
                }
                if packet_subtitle:
                    val["packet_subtitle"] = packet_subtitle
                if packet_name:
                    val["packet_name"] = packet_name
                if '__frequency' in value:
                    self.packet_frequency[packet_type] = value['__frequency']
                    val['packet_frequency'] = value['__frequency']
                self.packet_config_json[packet_type] = val
                self.packet_types.append(val["packet_type"])
    except:
        traceback.print_exc()
        sys.stderr.flush()
        sys.stdout.flush()
  
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