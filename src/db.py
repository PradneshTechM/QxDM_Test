import redis
import pickle

_r = redis.Redis(host='localhost', port=5041, db=0)

'''
Redis structure
- qxdm:initialized (string): true if qxdm keys are initialized, false otherwise

- qxdm:id (int): the id number of a process within the db

- qxdm:process:ID (hash)
  is_connected:   STRING
  connected_to:   STRING
  is_logging:     STRING
  log_name:       STRING
  log_start_time: STRING
  object:         STRING  serialized object

- qxdm:processes (set): list of all running processes

- qxdm:processes:connected (set): list of all running processes that are connected to a device

- qxdm:processes:logging (set): list of all running processes that are connected and logging
'''

def is_db_initialized():
  return _r.get('qxdm:initialized') != None


def reset_db():
  _r.flushall()


def initialize_db():
  _r.set('qxdm:initialized', 'true')
  _r.set('qxdm:id', 1000)


def add_process():
  next_id = _r.incr('qxdm:id')
  _r.hset(f'qxdm:process:{next_id}', 'is_connected', 'false')
  _r.sadd('qxdm:processes', next_id)
  return next_id


def set_object(id, obj):
  pickled_obj = pickle.dumps(obj)
  _r.hset(f'qxdm:process:{id}', 'object', pickled_obj)


def get_object(id):
  pickled_obj = _r.hget(f'qxdm:process:{id}', 'object')
  return pickle.loads(pickled_obj)


def remove_process(id):
  _r.delete(f'qxdm:process:{id}')
  _r.srem('qxdm:processes', id)
  _r.srem('qxdm:processes:connected', id)
  _r.srem('qxdm:processes:logging', id)


def get_process(id):
  return _r.hgetall(f'qxdm:process:{id}')


def get_processes():
  return _r.smembers('qxdm:processes')


def set_connected(id, port):
  _r.hmset(f'qxdm:process:{id}', 
    {
      'is_connected': 'true',
      'connected_to': port
    }
  )
  _r.sadd('qxdm:processes:connected', id)


def remove_connected(id):
  _r.hdel(f'qxdm:process:{id}', 'connected_to')
  _r.hset(f'qxdm:process:{id}', 'is_connected', 'false')
  _r.srem('qxdm:processes:connected', id)


def get_connected():
  return _r.smembers('qxdm:processes:connected')


def set_logging(id, start_time):
  _r.hmset(f'qxdm:process:{id}',
    {
      'is_logging': 'true',
      'log_start_time': start_time
    }
  )
  _r.sadd('qxdm:processes:logging', id)


def remove_logging(id):
  _r.hdel(f'qxdm:process:{id}', 'log_start_time')
  _r.hset(f'qxdm:process:{id}', 'is_logging', 'false')
  _r.srem('qxdm:processes:logging', id)


def get_logging():
  return _r.smembers('qxdm:processes:logging')