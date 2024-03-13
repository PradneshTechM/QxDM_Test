#!/usr/bin/env python3.7
from pathlib import Path
import random
import os
from datetime import date,timedelta,datetime
import json
import sys
import math
import csv
import win32com.client
from pubsub import pub
from typing import List
import traceback
import pythoncom
import threading
import yaml
import parser.main as parser
from datetime import datetime
from utils import unaware_datetime_to_utc

import message
from message import ParsedRawMessage
from parser.main import ParsedRawMessage as Message
from session import LogSession
from db import DB

_AUTOMATION_DELETE_LOGS_AFTER_PARSING = bool(os.environ.get("AUTOMATION_DELETE_LOGS_AFTER_PARSING", 'True').lower() in ('true', '1', 't'))
print("_AUTOMATION_DELETE_LOGS_AFTER_PARSING", _AUTOMATION_DELETE_LOGS_AFTER_PARSING)
sys.stdout.flush()

class HiddenPrints:
    def __enter__(self):
        self._original_stdout = sys.stdout
        sys.stdout = open(os.devnull, 'w')
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stdout.close()
        sys.stdout = self._original_stdout
        pass

class QCAT:
    def __init__(self):
        self.qcat = None  # QCAT app
        self.raw_messages = []
        self.parsed_messages = []
        self.validated_messages = []
        self.saved_values = {}

        self._launch()

    def _launch(self):
        # start QCAT process
        self.qcat = win32com.client.Dispatch("QCAT6.Application")
        print("QCAT launched")
        if not self.qcat:
            print('ERROR: Unable to invoke QCAT application')

    def parse(self, input, messages):
        print('Opening log file: ' + input)
        self.qcat.OpenLog(input)

        packet = self.qcat.FirstPacket
        if not packet:
            print('ERROR: Unable to get Packet object')

        print('Loading log packets from log file...')

        self.raw_messages = []
        self.parsed_raw_messages = []
        self.parsed_messages = []
        self.validated_messages = []
        self.saved_values = {}

        count = 0
        i = 0
        msg = None
        while packet:
            if not msg:
                msg = messages[i % len(messages)]
                i += 1
            name = packet.Name
            subtitle = packet.Subtitle
            datetime = packet.TimestampAsString
            packet_type = packet.Type
            text = packet.Text

            if msg.is_same_message_type(subtitle, packet_type, text):
                raw_msg = msg.get_contents(name, datetime, text)
                self.raw_messages.append(raw_msg)

                parsed_msg = msg.parse(name, datetime, text)
                self.parsed_messages.append(parsed_msg)

                self.validated_messages.append(parsed_msg.validate())
                count += 1
                msg = None
            if not packet.Next():
                break

        print(count, 'packets loaded.')
        
    def parse_raw(self, input):
        CHUNK_SIZE = 10000
        print('Opening log file: ' + input)
        self.qcat.OpenLog(input)

        packet = self.qcat.FirstPacket
        if not packet:
            print('ERROR: Unable to get Packet object')

        print('Loading log packets from log file...')

        self.parsed_raw_messages = []
        parsed_raw_messages = []

        count = 0
        while packet:
            name = packet.Name
            subtitle = packet.Subtitle
            datetime = packet.TimestampAsString
            packet_type = packet.Type
            packet_length = packet.Length
            text = packet.Text
            
            raw_msg = ParsedRawMessage(count, packet_type, packet_length, name, subtitle, datetime, text)
            # self.parsed_raw_messages.append(raw_msg)
            parsed_raw_messages.append(raw_msg)

            count += 1
            if count % CHUNK_SIZE == 0:
                print(count, 'packets loaded.')
                pub.sendMessage('messages', data={"messages": parsed_raw_messages, "chunk_num": int(count / CHUNK_SIZE)})
                parsed_raw_messages = []
            if not packet.Next():
                break
            
        if count % CHUNK_SIZE != 0:
            pub.sendMessage('messages', data={"messages": parsed_raw_messages, "chunk_num": math.ceil(count / CHUNK_SIZE)})
        
        print(count, 'packets loaded.')
        return count

    def set_packet_filter(self, packet_types):
        # get the filter
        filt = self.qcat.PacketFilter
        if not filt:
            print('ERROR: Unable to get Filter object')

        # set the filter
        if packet_types is not None:
            filt.SetAll(False)
            for packet in packet_types:
                filt.Set(packet, True)
            filt.Commit()

    def quit(self):
        self.qcat.closeFile()
        # self.qcat.Exit()
        self.qcat = None
        print('QCAT Quit - QCAT Closed')

class QCATWorker(threading.Thread):
    qcat_worker = None
    packet_config = None
    packet_config_json = {}
    packet_frequency = {}
    packet_types = []
    
    def __init__(self, qcat, log_id, log_session: LogSession, log_file, json_filepath):
        threading.Thread.__init__(self)
        super().__init__()
        
        try:
            self.qcat = qcat 
            self.log_id = log_id
            self.log_file = log_file
            self.json_filepath = json_filepath
            self.log_session = log_session
            self.config_file = self.log_session.config_file
            self.packet_types = self.log_session.packet_types
            self.packet_config_json = self.log_session.packet_config_json
            self.packet_frequency = self.log_session.packet_frequency
            sys.stdout.flush()
            
            self.marshalled_qcat = pythoncom.CoMarshalInterThreadInterfaceInStream(pythoncom.IID_IDispatch, self.qcat)
        except:
            traceback.print_exc()
            sys.stdout.flush()
            raise

    def parse_config(self):
        try:
            with open(self.config_file, 'r') as f:
                unparsed_config = yaml.load(f, Loader=yaml.FullLoader)
                for key, value in unparsed_config.items():
                    splited_key = key.split("--")
                    packet_type, packet_name = splited_key[:2]
                    packet_name = packet_name.strip()
                    packet_type = packet_type.strip()
                    packet_subtitle = None
                    if len(splited_key) > 2: packet_subtitle = splited_key[2].strip()
                    val = {
                        "packet_type": packet_type.lower(),
                        "packet_name": packet_name.strip(),
                        "fields": value
                    }
                    if '__event_frequency' in value:
                        #self.packet_frequency[val["packet_type"]]=60000/value['__event_frequency']
                        val['packet_frequency'] = 60000/value['__event_frequency']
                        del val["fields"]["__event_frequency"]
                    if '__db_collection_name' in value:
                        val['custom_dbcollection'] = val["fields"]["__db_collection_name"]
                        del val["fields"]["__db_collection_name"]
                    if '__raw_data' in value:
                        val['rawDataTag'] = val["fields"]["__raw_data"]
                        del val["fields"]["__raw_data"]
                    if packet_subtitle:
                        val["packet_subtitle"] = packet_subtitle
                        key = packet_type + " -- " + packet_subtitle
                    else:
                        key = packet_type
                    key = key.strip() 
                    self.packet_config[key] = val
                    self.packet_types.append(val["packet_type"])
        except:
            traceback.print_exc()
            sys.stderr.flush()
            sys.stdout.flush()
            
    
    def run(self) -> None:
        pythoncom.CoInitialize()
        self.qcat_worker = win32com.client.Dispatch(
            pythoncom.CoGetInterfaceAndReleaseStream(self.marshalled_qcat, pythoncom.IID_IDispatch)
        )
        self.parse_raw_log_json()
        pythoncom.CoUninitialize()
        
        # post-insert all to db
        # not needed anymore since we're actively updating to db for every chunk
        
            # parsedJsonArr = self.get_all_chunks(self.json_filepath)
            # sys.stdout.flush()
            # sys.stderr.flush()
            
            # print(f'Inserting {len(parsedJsonArr)} to db...')
            # insertLogsResult = DB.insert_logs(parsedJsonArr, self.log_session)
            # if insertLogsResult:
            #     print(f'Inserted {len(insertLogsResult.inserted_ids)} to db!')
            # sys.stdout.flush()
            # sys.stderr.flush()
        
        return_val = {
                'data': {
                'log_id': self.log_id,
                'startLogTimestamp': self.log_session.start_log_timestamp.isoformat(),
                'endLogTimestamp': self.log_session.end_log_timestamp.isoformat(),
                'jsonFile': self.json_filepath,
                'status': 'Parsing success',
            }
        }
        print(json.dumps(return_val, indent=2))

    def checkPacketAllowedbyConf(self,packet_type_raw,now):
        if not self.packet_config:
            return True
        elif packet_type_raw not in self.packet_config:
            return False
        elif "packet_frequency" not in self.packet_config[packet_type_raw]:
            return True
        elif packet_type_raw not in self.nextPacketAllowedat :
            return True
        elif self.nextPacketAllowedat[packet_type_raw] < now:
            return True
        else:
            return False
        
    def checkPacketAllowedbyJsonConf(self, packet_type, now):
        result = False
        if packet_type not in self.packet_config_json:
            result = False
        elif "packet_frequency" not in self.packet_config_json[packet_type]:
            result = True
        elif packet_type not in self.nextPacketAllowedat :
            result = True
        elif self.nextPacketAllowedat[packet_type] < now:
            result = True
        else:
            result = False
            
        if ((self.packet_config_json) and (packet_type in self.packet_config_json) and ("packet_frequency" in self.packet_config_json[packet_type])):
            freq_type = self.packet_config_json[packet_type]["packet_frequency"]
            delay = 0
            match freq_type:
                case "Event":
                    delay = 0
                case "Per Second":
                    delay = 1000
                case "Event [One]":
                    delay = 10000000000
                case _:
                    delay = 10000000000
            self.nextPacketAllowedat[packet_type] = now + timedelta(milliseconds=delay)
            
        return result
        
    def parse_raw(self, input):
        CHUNK_SIZE = 10000
        print('Opening log file: ' + input)
        self.qcat_worker.OpenLog(input)
        # self.qcat_worker.OpenLog("C:\\2024-01-17_095410_20f2043d_R3CRB05RT5J.hdf")
        
        packet_filter = self.qcat_worker.PacketFilter
        
        # assign packet filter before parsing
        if self.log_session.packet_types is not None:
            packet_filter.SetAll(False) 
            for packet in self.log_session.packet_types:
                packet_type_as_int = int(packet, 16)
                packet_filter.Set(packet_type_as_int, True) 
            packet_filter.Commit()

        packet = self.qcat_worker.FirstPacket
        if not packet:
            print('ERROR: Unable to get Packet object')

        print('Loading log packets from log file...')

        raw_messages = []
        self.nextPacketAllowedat ={}
        index = 0
        total_count = 0
        while packet:
            packet_type = packet.Type
            name = packet.Name
            subtitle = packet.Subtitle
            datetimestring = packet.TimestampAsString
            packet_length = packet.Length
            text = packet.Text 
            
            if isinstance(packet_type, int):
                packet_type_hex1 = hex(packet_type)
            else: 
                packet_type_hex1 = packet_type       
                packet_type = int(packet_type_hex1, 16)
                
            packet_type_hex = "0x" + packet_type_hex1[2:].upper()
            packet_type_raw = ( 
                            packet_type_hex + " -- "  + subtitle 
                            if subtitle and len(subtitle) > 0 
                            else packet_type_hex
                        )
            packet_type_all = ( 
                            packet_type_hex + " -- " + name 
                            + (" -- " + subtitle if subtitle and len(subtitle) > 0 
                            else "")
                        )
        
            if len(self.packet_types) > 0 and packet_type_hex not in self.packet_types:
                index += 1
                if index % CHUNK_SIZE == 0:
                    print(total_count, 'packets loaded to parse.')
                    print(index, 'packets walked over.')
                    sys.stdout.flush()
                if not packet.Next():
                    break
                else:
                    continue

            sys.stdout.flush()
            if ((not self.packet_config_json) or (packet_type_hex in self.packet_config_json)):
                now = datetime.strptime(datetimestring, '%Y %b %d  %H:%M:%S.%f')
                if self.checkPacketAllowedbyJsonConf(packet_type_hex, now):
                    raw_msg = parser.ParsedRawMessage(index, packet_type_hex, packet_length, name, packet_type_all, subtitle, datetimestring, text, now)
                    
                    raw_messages.append(raw_msg)

                    index += 1
                    total_count += 1
                    if index % CHUNK_SIZE == 0:
                        print(total_count, 'packets loaded to parse.')
                        sys.stdout.flush()
                        pub.sendMessage(self.log_id, data={"log_id": self.log_id, "messages": raw_messages, "chunk_num": int(index / CHUNK_SIZE)})
                        raw_messages = []
                    
                else:
                    pass
                            
            else:
                pass

            if not packet.Next():
                break

                   
            
        if index % CHUNK_SIZE != 0:
            pub.sendMessage(self.log_id, data={"log_id": self.log_id, "messages": raw_messages, "chunk_num": math.ceil(index / CHUNK_SIZE)})
        
        self.qcat_worker.closeFile()
        
        print(index, 'packets walked over.')
        sys.stdout.flush()
        return total_count 
    
    def parse_raw_log_json(self):
        print('QCAT json log parsing started')
        def messages_listener(data):
            try:
                messages: list[Message] = data["messages"]
                chunk_num = data["chunk_num"]
                log_id = data["log_id"]
                
                # parse to json
                json_arr = {'default':[]}
                count = 0

                for raw_msg in messages:
                    arr = []
                    with HiddenPrints():
                        arr = raw_msg.to_json()
                        
                    if arr is None: 
                        continue
                        
                    for payload, metadata in arr:
                        if payload is None: 
                            continue
                            
                        count += 1
                        
                        timestamp: datetime = payload["Time"]
                        # timestamp directly from QCAT is already in UTC
                        # timestamp_as_utc = unaware_datetime_to_utc(timestamp)
                        payload["Time"] = timestamp
                        
                        collection_name = 'default'
                        if "__collection" in payload:
                            collection_name = payload["__collection"]
                            if collection_name not in json_arr:
                                json_arr[collection_name] = []
                            del payload["__collection"]
                                
                        json_arr[collection_name].append({
                            **metadata,
                            **payload
                        })
                        
                if json_arr:
                    print(f'Inserting chunk {chunk_num} for log {log_id} with {count} packets to db...')
                    sys.stdout.flush()
                    for collection_name in json_arr:
                        insertLogsResult = DB.insert_logs(json_arr[collection_name], self.log_session, collection_name)
                        if insertLogsResult:
                            print(f'Inserted {len(insertLogsResult.inserted_ids)} to {collection_name}')
                            sys.stdout.flush()
                        
            except:
                traceback.print_exc()
                sys.stdout.flush()
                sys.stderr.flush()
        
        pub.subscribe(messages_listener, self.log_id)
        total_count = self.parse_raw(self.log_file)
        pub.unsubscribe(messages_listener, self.log_id)
        
        # print(f'Successfuly parsed a total of {total_count} packets for log {self.log_id}!')
        # sys.stdout.flush()
        # sys.stderr.flush()
        
        if _AUTOMATION_DELETE_LOGS_AFTER_PARSING:
            if os.path.exists(self.log_file):
                os.remove(self.log_file)
                print(f'deleted log {self.log_id} from disk at {self.log_file}')
            sys.stdout.flush()
            sys.stderr.flush()
        
        return total_count
    
    def get_all_chunks(self, filepath):
        all_packets = []
        suffix = 1
        while True:
            chunk_path = f'{filepath}.{suffix}'
            if os.path.isfile(chunk_path):
                with open(chunk_path, 'r') as file:
                    try:
                        data = json.load(file)
                        all_packets += data
                    except json.JSONDecodeError:
                        print(f"Error decoding JSON in file: {chunk_path}")
                        sys.stdout.flush()
                        sys.stderr.flush()
                        break
                    finally:
                        suffix += 1
            else: break
        return all_packets
    
    

def parse_json_config(filename):
    print('Loading test config:', filename)
    with open(filename) as f:
        TC_json = json.load(f)

    # print(json.dumps(TC_json, indent=2))

    # load device specs
    device_specs = {}
    with open(TC_json['device_specs']) as f:
        device_spec_json = json.load(f)
        for key, value in device_spec_json.items():
            device_specs[key] = value

    # build message requirements
    messages = []
    for test_file in TC_json['tests']:
        with open(test_file) as f:
            test_json = json.load(f)

        for json_msg in test_json['messages']:
            fields = []
            for json_field in json_msg['fields']:
                field = message.Field(
                    field_name=json_field.get('field_name', None),
                    regex=json_field.get('regex', None),
                    search_2=json_field.get('search_2', None),
                    field_type=message.FieldType[json_field['field_type']],
                    get_value=json_field['get_value'],
                    expected_value=json_field.get('expected_value', None),
                    validation_regex=json_field.get('validation_regex', None),
                    validation_type=message.ValidationType[json_field['validation_type']]
                )
                device_spec = device_specs.get(field.field_name, None)
                if device_spec:
                    field.expected_value = device_spec
                fields.append(field)

            msg = message.Message(
                description=json_msg['description'],
                packet_type=int(json_msg['packet_type'], 16),
                subtitle=json_msg['subtitle'],
                fields=fields,
                must_match_field=json_msg.get('must_match_field', None),
                saved_values=device_specs
            )
            messages.append(msg)
    return TC_json, messages, device_specs


def parse_log(input_filename, test_filename, raw_filename,
              parsed_filename, validated_filename, validated_csv, qcat):
    print('QCAT log analysis started')
    TC_json, messages, device_specs = parse_json_config(test_filename)

    name = TC_json['name']
    preconditions = TC_json['preconditions']
    description = TC_json['description']
    packet_types = [int(packet, 16) for packet in TC_json['packet_types']]

    print('Parsing:', name)

    qcat.set_packet_filter(packet_types)
    qcat.parse(input_filename, messages)
    qcat.saved_values = device_specs

    with open(raw_filename, 'w') as f:
        for raw_msg in qcat.raw_messages:
            f.write(raw_msg.to_string())
    print('raw messages:', raw_filename)

    with open(parsed_filename, 'w') as f:
        for parsed_msg in qcat.parsed_messages:
            parsed_msg_str = parsed_msg.to_string()
            f.write(parsed_msg_str)
            # print(parsed_msg_str)
    print('parsed messages:', parsed_filename)

    with open(validated_filename, 'w') as f:
        f.write('================================================================================\n\n')
        f.write(f'Test Case Name:\n{name}\n\n')
        f.write('Preconditions:\n' + '\n'.join(preconditions) + '\n\n')
        f.write('Test Description:\n' + '\n'.join(description) + '\n\n')
        f.write('================================================================================\n\n')
        for validated_msg in qcat.validated_messages:
            validated_msg_str = validated_msg.to_string()
            f.write(validated_msg_str)
    print('validated messages:', validated_filename)

    # save csv
    with open(validated_csv, 'w', newline='') as f:
        fieldnames = [
            'Parameter Name', 'Pass/Fail', 'Expected Value', 'Actual Value'
        ]

        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for validated_msg in qcat.validated_messages:
            validated_msg.save_to_csv(writer)

            # dummy MT log
            if validated_msg.subtitle == 'IMS_SIP_INVITE/INFORMAL_RESPONSE':
                folder = Path(validated_csv).parent
                validated_csv2 = folder / 'result_validated_tc2_VoLTE_call_MT.csv'
                with open(validated_csv2, 'w', newline='') as f2:
                    writer2 = csv.DictWriter(f2, fieldnames=fieldnames)
                    writer2.writeheader()

                    datetime = validated_msg.datetime.split('.')
                    ms = int(datetime[-1])
                    datetime[-1] = str(random.randint(max(ms + 25, 100), ms + 150))
                    validated_msg.datetime = '.'.join(datetime)
                    validated_msg.save_to_csv(writer2)

    print('validated csv:', validated_csv)
    return True

def parse_raw_log(input_filename, raw_filename, qcat):
    print('QCAT raw log parsing started')

    qcat.parse_raw(input_filename)

    with open(raw_filename, 'w') as f:
        for raw_msg in qcat.parsed_raw_messages:
            f.write(raw_msg.to_string())
    print('raw messages:', raw_filename)

    return True

if __name__ == '__main__':
    input_filename = os.path.abspath('/home/techm/Desktop/QXDM_Log.isf')
    # input_filename = os.path.abspath('/home/techm/Desktop/TC1/saved_test_2.isf')
    test_filename = 'qcat_tests/Test_case_2.json'
    output_filename = 'TC2_att'

    raw_filename = f'qcat_tests/result_raw_{output_filename}.txt'
    parsed_filename = f'qcat_tests/result_parsed_{output_filename}.txt'
    validated_filename = f'qcat_tests/result_validated_{output_filename}.txt'
    validated_csv = f'qcat_tests/result_validated_{output_filename}.csv'

    qcat = QCAT()
    parse_log(input_filename, test_filename, raw_filename, parsed_filename,
            validated_filename, validated_csv, qcat)

    qcat.quit()
