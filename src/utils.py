from datetime import datetime, timezone
local_tz_info = datetime.now().astimezone().tzinfo

def unaware_datetime_to_utc(dt_without_tz: datetime) -> datetime:
  dt_with_tz = datetime.fromtimestamp(dt_without_tz.timestamp(), local_tz_info)
  dt_in_utc = dt_with_tz.astimezone(timezone.utc) 
  return dt_in_utc