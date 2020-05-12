import redis
import pickle

_r = redis.Redis(host='localhost', port=5041, db=0)

'''
Redis structure
- qxdm:initialized (string): true if qxdm keys are initialized, false otherwise

- qxdm:process (hash)
  object:         STRING  serialized object
'''

def is_db_initialized():
  return _r.get('qxdm:initialized') != None


def reset_db():
  _r.flushall()


def initialize_db():
  _r.set('qxdm:initialized', 'true')


def set_process(id, obj):
  pickled_obj = pickle.dumps(obj)
  _r.hset('qxdm:process', 'object', pickled_obj)


def get_process():
  pickled_obj = _r.hget('qxdm:process:', 'object')
  return pickle.loads(pickled_obj)


def remove_process(id):
  _r.hdel('qxdm:process', 'object')
