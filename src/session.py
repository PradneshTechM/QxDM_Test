import dataclasses
from datetime import datetime
from typing import List, Any
from enum import Enum

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

class LogSession(Session):
  log_id: str = None
  mask_file: str = None
  raw_logs: List[str] = None
  validated_logs: List[str] = None
  test_case: TestCase = None

class ATSession(Session):
  pass