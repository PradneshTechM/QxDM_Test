#!/usr/bin/env python3.7
from pathlib import Path
import random
import os
import json
import sys
import math
import csv
import win32com.client
from pubsub import pub
from typing import List
import traceback

import message
from message import ParsedRawMessage


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

def parse_raw_log_json(input_filename, json_filename, qcat):
    print('QCAT json log parsing started')
    def messages_listener(data):
        messages = data["messages"]
        chunk_num = data["chunk_num"]
        chunk_file = f'{json_filename}.{chunk_num}'
        print(f'chunk: {chunk_file}')
        sys.stdout.flush()
        sys.stderr.flush()
        with open(chunk_file, 'w') as f:
            json_arr = []
            for raw_msg in messages:
                json_arr.append(raw_msg.to_json())
            json.dump(json_arr, f, indent = 2) 
    
    pub.subscribe(messages_listener, 'messages')

    total_count = qcat.parse_raw(input_filename)

    print('JSON file path:', json_filename)

    return total_count

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
