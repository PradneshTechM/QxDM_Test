# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: qxdm.proto

import sys
_b=sys.version_info[0]<3 and (lambda x:x) or (lambda x:x.encode('latin1'))
from google.protobuf.internal import enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor.FileDescriptor(
  name='qxdm.proto',
  package='',
  syntax='proto3',
  serialized_options=None,
  serialized_pb=_b('\n\nqxdm.proto\"\x12\n\x10LaunchAppRequest\"&\n\x11LaunchAppResponse\x12\x11\n\tclient_id\x18\x01 \x01(\r\"?\n\x14\x43onnectDeviceRequest\x12\x11\n\tclient_id\x18\x01 \x01(\r\x12\x14\n\x0c\x64\x65vice_index\x18\x02 \x01(\r\"8\n\x15\x43onnectDeviceResponse\x12\x1f\n\x05state\x18\x01 \x01(\x0e\x32\x10.ConnectionState\",\n\x17\x44isconnectDeviceRequest\x12\x11\n\tclient_id\x18\x01 \x01(\r\";\n\x18\x44isconnectDeviceResponse\x12\x1f\n\x05state\x18\x01 \x01(\x0e\x32\x10.ConnectionState\"$\n\x0fStartLogRequest\x12\x11\n\tclient_id\x18\x01 \x01(\r\"\x12\n\x10StartLogResponse\"5\n\x0eSaveLogRequest\x12\x11\n\tclient_id\x18\x01 \x01(\r\x12\x10\n\x08log_name\x18\x02 \x01(\t\"\x1f\n\x0fSaveLogResponse\x12\x0c\n\x04\x64\x61ta\x18\x01 \x01(\x0c\"#\n\x0eQuitAppRequest\x12\x11\n\tclient_id\x18\x01 \x01(\r\"\x11\n\x0fQuitAppResponse*2\n\x0f\x43onnectionState\x12\x10\n\x0c\x44ISCONNECTED\x10\x00\x12\r\n\tCONNECTED\x10\x01\x32\xde\x02\n\x04QXDM\x12\x34\n\tLaunchApp\x12\x11.LaunchAppRequest\x1a\x12.LaunchAppResponse\"\x00\x12@\n\rConnectDevice\x12\x15.ConnectDeviceRequest\x1a\x16.ConnectDeviceResponse\"\x00\x12I\n\x10\x44isconnectDevice\x12\x18.DisconnectDeviceRequest\x1a\x19.DisconnectDeviceResponse\"\x00\x12\x31\n\x08StartLog\x12\x10.StartLogRequest\x1a\x11.StartLogResponse\"\x00\x12\x30\n\x07SaveLog\x12\x0f.SaveLogRequest\x1a\x10.SaveLogResponse\"\x00\x30\x01\x12.\n\x07QuitApp\x12\x0f.QuitAppRequest\x1a\x10.QuitAppResponse\"\x00\x62\x06proto3')
)

_CONNECTIONSTATE = _descriptor.EnumDescriptor(
  name='ConnectionState',
  full_name='ConnectionState',
  filename=None,
  file=DESCRIPTOR,
  values=[
    _descriptor.EnumValueDescriptor(
      name='DISCONNECTED', index=0, number=0,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='CONNECTED', index=1, number=1,
      serialized_options=None,
      type=None),
  ],
  containing_type=None,
  serialized_options=None,
  serialized_start=506,
  serialized_end=556,
)
_sym_db.RegisterEnumDescriptor(_CONNECTIONSTATE)

ConnectionState = enum_type_wrapper.EnumTypeWrapper(_CONNECTIONSTATE)
DISCONNECTED = 0
CONNECTED = 1



_LAUNCHAPPREQUEST = _descriptor.Descriptor(
  name='LaunchAppRequest',
  full_name='LaunchAppRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=14,
  serialized_end=32,
)


_LAUNCHAPPRESPONSE = _descriptor.Descriptor(
  name='LaunchAppResponse',
  full_name='LaunchAppResponse',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='client_id', full_name='LaunchAppResponse.client_id', index=0,
      number=1, type=13, cpp_type=3, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=34,
  serialized_end=72,
)


_CONNECTDEVICEREQUEST = _descriptor.Descriptor(
  name='ConnectDeviceRequest',
  full_name='ConnectDeviceRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='client_id', full_name='ConnectDeviceRequest.client_id', index=0,
      number=1, type=13, cpp_type=3, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='device_index', full_name='ConnectDeviceRequest.device_index', index=1,
      number=2, type=13, cpp_type=3, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=74,
  serialized_end=137,
)


_CONNECTDEVICERESPONSE = _descriptor.Descriptor(
  name='ConnectDeviceResponse',
  full_name='ConnectDeviceResponse',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='state', full_name='ConnectDeviceResponse.state', index=0,
      number=1, type=14, cpp_type=8, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=139,
  serialized_end=195,
)


_DISCONNECTDEVICEREQUEST = _descriptor.Descriptor(
  name='DisconnectDeviceRequest',
  full_name='DisconnectDeviceRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='client_id', full_name='DisconnectDeviceRequest.client_id', index=0,
      number=1, type=13, cpp_type=3, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=197,
  serialized_end=241,
)


_DISCONNECTDEVICERESPONSE = _descriptor.Descriptor(
  name='DisconnectDeviceResponse',
  full_name='DisconnectDeviceResponse',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='state', full_name='DisconnectDeviceResponse.state', index=0,
      number=1, type=14, cpp_type=8, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=243,
  serialized_end=302,
)


_STARTLOGREQUEST = _descriptor.Descriptor(
  name='StartLogRequest',
  full_name='StartLogRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='client_id', full_name='StartLogRequest.client_id', index=0,
      number=1, type=13, cpp_type=3, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=304,
  serialized_end=340,
)


_STARTLOGRESPONSE = _descriptor.Descriptor(
  name='StartLogResponse',
  full_name='StartLogResponse',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=342,
  serialized_end=360,
)


_SAVELOGREQUEST = _descriptor.Descriptor(
  name='SaveLogRequest',
  full_name='SaveLogRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='client_id', full_name='SaveLogRequest.client_id', index=0,
      number=1, type=13, cpp_type=3, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='log_name', full_name='SaveLogRequest.log_name', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=362,
  serialized_end=415,
)


_SAVELOGRESPONSE = _descriptor.Descriptor(
  name='SaveLogResponse',
  full_name='SaveLogResponse',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='data', full_name='SaveLogResponse.data', index=0,
      number=1, type=12, cpp_type=9, label=1,
      has_default_value=False, default_value=_b(""),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=417,
  serialized_end=448,
)


_QUITAPPREQUEST = _descriptor.Descriptor(
  name='QuitAppRequest',
  full_name='QuitAppRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='client_id', full_name='QuitAppRequest.client_id', index=0,
      number=1, type=13, cpp_type=3, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=450,
  serialized_end=485,
)


_QUITAPPRESPONSE = _descriptor.Descriptor(
  name='QuitAppResponse',
  full_name='QuitAppResponse',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=487,
  serialized_end=504,
)

_CONNECTDEVICERESPONSE.fields_by_name['state'].enum_type = _CONNECTIONSTATE
_DISCONNECTDEVICERESPONSE.fields_by_name['state'].enum_type = _CONNECTIONSTATE
DESCRIPTOR.message_types_by_name['LaunchAppRequest'] = _LAUNCHAPPREQUEST
DESCRIPTOR.message_types_by_name['LaunchAppResponse'] = _LAUNCHAPPRESPONSE
DESCRIPTOR.message_types_by_name['ConnectDeviceRequest'] = _CONNECTDEVICEREQUEST
DESCRIPTOR.message_types_by_name['ConnectDeviceResponse'] = _CONNECTDEVICERESPONSE
DESCRIPTOR.message_types_by_name['DisconnectDeviceRequest'] = _DISCONNECTDEVICEREQUEST
DESCRIPTOR.message_types_by_name['DisconnectDeviceResponse'] = _DISCONNECTDEVICERESPONSE
DESCRIPTOR.message_types_by_name['StartLogRequest'] = _STARTLOGREQUEST
DESCRIPTOR.message_types_by_name['StartLogResponse'] = _STARTLOGRESPONSE
DESCRIPTOR.message_types_by_name['SaveLogRequest'] = _SAVELOGREQUEST
DESCRIPTOR.message_types_by_name['SaveLogResponse'] = _SAVELOGRESPONSE
DESCRIPTOR.message_types_by_name['QuitAppRequest'] = _QUITAPPREQUEST
DESCRIPTOR.message_types_by_name['QuitAppResponse'] = _QUITAPPRESPONSE
DESCRIPTOR.enum_types_by_name['ConnectionState'] = _CONNECTIONSTATE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

LaunchAppRequest = _reflection.GeneratedProtocolMessageType('LaunchAppRequest', (_message.Message,), {
  'DESCRIPTOR' : _LAUNCHAPPREQUEST,
  '__module__' : 'qxdm_pb2'
  # @@protoc_insertion_point(class_scope:LaunchAppRequest)
  })
_sym_db.RegisterMessage(LaunchAppRequest)

LaunchAppResponse = _reflection.GeneratedProtocolMessageType('LaunchAppResponse', (_message.Message,), {
  'DESCRIPTOR' : _LAUNCHAPPRESPONSE,
  '__module__' : 'qxdm_pb2'
  # @@protoc_insertion_point(class_scope:LaunchAppResponse)
  })
_sym_db.RegisterMessage(LaunchAppResponse)

ConnectDeviceRequest = _reflection.GeneratedProtocolMessageType('ConnectDeviceRequest', (_message.Message,), {
  'DESCRIPTOR' : _CONNECTDEVICEREQUEST,
  '__module__' : 'qxdm_pb2'
  # @@protoc_insertion_point(class_scope:ConnectDeviceRequest)
  })
_sym_db.RegisterMessage(ConnectDeviceRequest)

ConnectDeviceResponse = _reflection.GeneratedProtocolMessageType('ConnectDeviceResponse', (_message.Message,), {
  'DESCRIPTOR' : _CONNECTDEVICERESPONSE,
  '__module__' : 'qxdm_pb2'
  # @@protoc_insertion_point(class_scope:ConnectDeviceResponse)
  })
_sym_db.RegisterMessage(ConnectDeviceResponse)

DisconnectDeviceRequest = _reflection.GeneratedProtocolMessageType('DisconnectDeviceRequest', (_message.Message,), {
  'DESCRIPTOR' : _DISCONNECTDEVICEREQUEST,
  '__module__' : 'qxdm_pb2'
  # @@protoc_insertion_point(class_scope:DisconnectDeviceRequest)
  })
_sym_db.RegisterMessage(DisconnectDeviceRequest)

DisconnectDeviceResponse = _reflection.GeneratedProtocolMessageType('DisconnectDeviceResponse', (_message.Message,), {
  'DESCRIPTOR' : _DISCONNECTDEVICERESPONSE,
  '__module__' : 'qxdm_pb2'
  # @@protoc_insertion_point(class_scope:DisconnectDeviceResponse)
  })
_sym_db.RegisterMessage(DisconnectDeviceResponse)

StartLogRequest = _reflection.GeneratedProtocolMessageType('StartLogRequest', (_message.Message,), {
  'DESCRIPTOR' : _STARTLOGREQUEST,
  '__module__' : 'qxdm_pb2'
  # @@protoc_insertion_point(class_scope:StartLogRequest)
  })
_sym_db.RegisterMessage(StartLogRequest)

StartLogResponse = _reflection.GeneratedProtocolMessageType('StartLogResponse', (_message.Message,), {
  'DESCRIPTOR' : _STARTLOGRESPONSE,
  '__module__' : 'qxdm_pb2'
  # @@protoc_insertion_point(class_scope:StartLogResponse)
  })
_sym_db.RegisterMessage(StartLogResponse)

SaveLogRequest = _reflection.GeneratedProtocolMessageType('SaveLogRequest', (_message.Message,), {
  'DESCRIPTOR' : _SAVELOGREQUEST,
  '__module__' : 'qxdm_pb2'
  # @@protoc_insertion_point(class_scope:SaveLogRequest)
  })
_sym_db.RegisterMessage(SaveLogRequest)

SaveLogResponse = _reflection.GeneratedProtocolMessageType('SaveLogResponse', (_message.Message,), {
  'DESCRIPTOR' : _SAVELOGRESPONSE,
  '__module__' : 'qxdm_pb2'
  # @@protoc_insertion_point(class_scope:SaveLogResponse)
  })
_sym_db.RegisterMessage(SaveLogResponse)

QuitAppRequest = _reflection.GeneratedProtocolMessageType('QuitAppRequest', (_message.Message,), {
  'DESCRIPTOR' : _QUITAPPREQUEST,
  '__module__' : 'qxdm_pb2'
  # @@protoc_insertion_point(class_scope:QuitAppRequest)
  })
_sym_db.RegisterMessage(QuitAppRequest)

QuitAppResponse = _reflection.GeneratedProtocolMessageType('QuitAppResponse', (_message.Message,), {
  'DESCRIPTOR' : _QUITAPPRESPONSE,
  '__module__' : 'qxdm_pb2'
  # @@protoc_insertion_point(class_scope:QuitAppResponse)
  })
_sym_db.RegisterMessage(QuitAppResponse)



_QXDM = _descriptor.ServiceDescriptor(
  name='QXDM',
  full_name='QXDM',
  file=DESCRIPTOR,
  index=0,
  serialized_options=None,
  serialized_start=559,
  serialized_end=909,
  methods=[
  _descriptor.MethodDescriptor(
    name='LaunchApp',
    full_name='QXDM.LaunchApp',
    index=0,
    containing_service=None,
    input_type=_LAUNCHAPPREQUEST,
    output_type=_LAUNCHAPPRESPONSE,
    serialized_options=None,
  ),
  _descriptor.MethodDescriptor(
    name='ConnectDevice',
    full_name='QXDM.ConnectDevice',
    index=1,
    containing_service=None,
    input_type=_CONNECTDEVICEREQUEST,
    output_type=_CONNECTDEVICERESPONSE,
    serialized_options=None,
  ),
  _descriptor.MethodDescriptor(
    name='DisconnectDevice',
    full_name='QXDM.DisconnectDevice',
    index=2,
    containing_service=None,
    input_type=_DISCONNECTDEVICEREQUEST,
    output_type=_DISCONNECTDEVICERESPONSE,
    serialized_options=None,
  ),
  _descriptor.MethodDescriptor(
    name='StartLog',
    full_name='QXDM.StartLog',
    index=3,
    containing_service=None,
    input_type=_STARTLOGREQUEST,
    output_type=_STARTLOGRESPONSE,
    serialized_options=None,
  ),
  _descriptor.MethodDescriptor(
    name='SaveLog',
    full_name='QXDM.SaveLog',
    index=4,
    containing_service=None,
    input_type=_SAVELOGREQUEST,
    output_type=_SAVELOGRESPONSE,
    serialized_options=None,
  ),
  _descriptor.MethodDescriptor(
    name='QuitApp',
    full_name='QXDM.QuitApp',
    index=5,
    containing_service=None,
    input_type=_QUITAPPREQUEST,
    output_type=_QUITAPPRESPONSE,
    serialized_options=None,
  ),
])
_sym_db.RegisterServiceDescriptor(_QXDM)

DESCRIPTOR.services_by_name['QXDM'] = _QXDM

# @@protoc_insertion_point(module_scope)