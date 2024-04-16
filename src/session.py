import dataclasses
import sys
from datetime import datetime
from typing import List, Any
from enum import Enum
from pymongo import MongoClient, GEO2D
import traceback
import json
import re
from utils import str_to_datetime

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
  locations: List[dict] = []
  url: str = 'https://webhook.site/512dbad9-64da-444c-8e86-420c609e60ed'
  
  def set_locations(self, locations: dict[str, List[dict]]):
    def map_locs(loc: dict):
      return ({
        "latitude": loc["latitude"],
        "longitude": loc["longitude"],
        "timestamp": str_to_datetime(loc["timestamp"]),
      })
    
    device_locs = list(map(map_locs, locations["deviceLocations"]))
    server_locs = list(map(map_locs, locations["serverLocations"]))
    
    self.locations = []
    i = j = 0

    while i < len(device_locs) and j < len(server_locs):
      if device_locs[i]["timestamp"] < server_locs[j]["timestamp"]:
        self.locations.append(device_locs[i])
        i += 1
      else:
        self.locations.append(server_locs[j])
        j += 1

    while i < len(device_locs):
      self.locations.append(device_locs[i])
      i += 1

    while j < len(server_locs):
      self.locations.append(server_locs[j])
      j += 1
      
  def has_locations(self) -> bool:
    return len(self.locations) > 0 
    
  def get_closest_location(self, timestamp) -> dict:
    closest = min(self.locations, key=lambda obj: abs(obj["timestamp"] - timestamp))
    return closest
  
  def parse_config_json(self, packet_filter: list[str] | None):
    DOUBLE_SPACE = "  "
    DOUBLE_DASH  = "--"
    ONE_SPACE_r = "^(0x....) "
    ONE_SPACE = " "
    
    for input_file in [
        "./parser/input.json",
        "./parser/P2.json",
        "./parser/P3.json",
        "./parser/P4.json",
        "./parser/P5.json",
    ]:
      with open(input_file, 'r') as f:
          unparsed_config: dict[(str, dict)] = json.load(f)
          for key, value in unparsed_config.items(): 
              try:
                splitted_key: list[str] = []
                if DOUBLE_SPACE in key:
                  splitted_key = key.split(DOUBLE_SPACE)
                elif DOUBLE_DASH in key: 
                  splitted_key = key.split(DOUBLE_DASH)
                else:
                  splitted_key = re.split(ONE_SPACE_r, key)
                splitted_key = list(filter(lambda sk: len(sk) > 0, splitted_key))
               
                packet_type = splitted_key[0].strip()
                if not packet_type.startswith("0x"):
                  continue
                if(packet_filter is not None and packet_type not in packet_filter):
                  continue
                
                packet_name = None
                if len(splitted_key) > 1: packet_name = splitted_key[1].strip()
                packet_subtitle = None
                if len(splitted_key) > 2: packet_subtitle = splitted_key[2].strip()
                val = {
                    "packet_type": packet_type
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
              finally:
                f.close()
        
    print(self.packet_config_json)
    print(self.packet_types)
    sys.stdout.flush()
    
  
  def init_db_and_collection(self):
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