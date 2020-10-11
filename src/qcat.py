from pydbus import SessionBus
import random
import subprocess
import time
import os
import dataclasses
from enum import Enum
import json
import re

from gi.repository import GLib, Gio

'''
For reference, see following files:
 * /opt/qcom/QCAT/Script/QCATDBus.pm - launch app, packet filter, packets
 * /opt/qcom/QCAT/Script/FilterSample.pl - set packet filter
'''


# specifies whether the field is a value or a collection of values
class FieldType(Enum):
    VALUE = 1
    COLLECTION = 2


@dataclasses.dataclass
class Field:
    field_name: str
    regex: str
    field_type: FieldType
    get_value: bool


@dataclasses.dataclass
class Message:
    packet_type: int
    subtitle: str
    fields: [Field]


class QCAT:
    PROCESS_PATH = '/opt/qcom/QCAT/bin/QCAT'  # path to QCAT binary
    RETRY_ATTEMPTS = 10   # number of times to retry getting Dbus object

    QCAT_OBJ = 'com.qcom.QCAT'
    QCAT_INTF = '/QCATDbusServer'
    PACKET_FILTER_OBJ = 'com.qcom.QCATPacketFilter'
    PACKET_FILTER_INTF = '/QCATPacketFilterDbusServer'
    PACKET_OBJ = 'com.qcom.QCATLogPacket'
    PACKET_INTF = '/QCATLogPacketDbusServer'

    def __init__(self):
        self.process = None
        self.bus = None
        self.qcat = None  # QCAT dbus object

        self._launch()

    def _launch(self):
        value = int(random.randint(0, 100))
        process_path = f'{QCAT.PROCESS_PATH} -Automation {value}'
        object_path = f'{QCAT.QCAT_OBJ}-{value}'
        interface = f'{QCAT.QCAT_INTF}_{value}'

        # start QCAT process
        self.process = subprocess.Popen(process_path.split())
        print("QCAT launched")

        self.bus = SessionBus()

        self.qcat = self._get_dbus_obj(object_path, interface)
        if not self.qcat:
            print('ERROR: Unable to get QCAT Dbus object')

    def _get_dbus_obj(self, object_path, interface):
        '''
        Returns the proxy object for the given object path and interface.
        Tries once per second for QCAT.RETRY_ATTEMPTS and returns None if
        unable to get proxy object.

        For more information, see:
        https://github.com/LEW21/pydbus/blob/master/doc/tutorial.rst#id7
        '''
        tries = 0
        dbus_obj = None
        while not dbus_obj and tries < QCAT.RETRY_ATTEMPTS:
            time.sleep(1)
            try:
                dbus_obj = self.bus.get(object_path, interface)
            except GLib.Error:
                pass
            tries += 1
        return dbus_obj

    def parse(self, input, messages):
        parsed_data = []
        print('Opening log file: ' + input)
        self.qcat.OpenLog(input)

        # get the packet
        service_name = self.qcat.FirstPacket_Ref()
        object_path = f'{QCAT.PACKET_OBJ}-{service_name}'
        interface = f'{QCAT.PACKET_INTF}_{service_name}'

        packet = self._get_dbus_obj(object_path, interface)
        if not packet:
            print('ERROR: Unable to get Packet Dbus object')

        print('Loading log packets from log file...')

        count = 0
        while packet:
            for msg in messages:
                # search by subtitle if there is one, otherwise search by packet_type
                if (msg.subtitle and packet.Subtitle() == msg.subtitle) or \
                        (not msg.subtitle and packet.Type() == msg.packet_type):
                    matched = []
                    # for each field of message, apply regex or normal search
                    for field in msg.fields:
                        if field.regex:
                            text = packet.Text()  # for debugging
                            result = re.search(field.regex, packet.Text())
                            if result and len(result.groups()) >= 1:
                                if field.field_type == FieldType.COLLECTION:
                                    matched.append(field.field_name)
                                    # split by '\r\n' and remove whitespace from start and end
                                    elements = [el.strip() for el in result.group(1).split('\r\n')]
                                    # remove empty strings
                                    elements = [el for el in elements if el != '']
                                    # remove ',' at end
                                    elements = [el if el[-1] != ',' else el[:-1] for el in elements]
                                    matched.append(elements)
                                else:
                                    matched.append(result.group(1).strip())
                        else:
                            match = None
                            if field.get_value:
                                for line in packet.Text().split('\r\n'):
                                    if field.field_name in line:
                                        match = line.strip()
                                        break
                            else:
                                if field.field_name in packet.Text():
                                    match = field.field_name
                            if match:
                                matched.append(match)

                    # add parsed data to output
                    parsed_data.append([
                        packet.TimestampAsString(),
                        packet.Name(),
                        packet.Subtitle(),
                        matched,
                    ])
                    count += 1

            if not packet.Next():
                print(count, 'packets loaded.')
                return parsed_data

    def set_packet_filter(self, packet_types):
        # get the filter
        service_name = self.qcat.PacketFilter_Ref()
        object_path = f'{QCAT.PACKET_FILTER_OBJ}-{service_name}'
        interface = f'{QCAT.PACKET_FILTER_INTF}_{service_name}'

        filt = self._get_dbus_obj(object_path, interface)
        if not filt:
            print('ERROR: Unable to get Filter Dbus object')

        # set the filter
        if packet_types is not None:
            filt.SetAll(False)
            for packet in packet_types:
                filt.SetItem(packet, True)
            filt.Commit()

    def quit(self):
        self.qcat.closeFile()
        self.qcat.Exit()
        print('QCAT Quit - QCAT Closed')

    def print_data(self, data):
        print('Type:', data[1])
        print('Name:', data[2])
        print('Subtitle:', data[5])
        print(f'Text:\n{data[6]}')

    def write_data(self, data, f):
        f.write(f'Type: {data[1]}\n')
        f.write(f'Name: {data[2]}\n')
        f.write(f'Subtitle: {data[5]}\n')
        f.write(f'Text:\n{data[6]}\n')

    def write_parsed_data(self, data, f):
        f.write(f'Datetime: {data[0]}\n')
        f.write(f'Name: {data[1]}\n')
        if data[2]:
            f.write(f'Subtitle: {data[2]}\n')
        if data[3]:
            f.write('Matches:\n')
            for match in data[3]:
                if type(match) == list:
                    f.write('\t[\n')
                    f.writelines('\t\t' + '\n\t\t'.join(match))
                    f.write('\n\t]\n')
                else:
                    f.write(f'\t{match}\n')
        f.write('\n')


def parse_json(filename):
    with open(filename) as f:
        TC_json = json.load(f)

    # print(json.dumps(TC_json, indent=2))

    packet_types = [int(packet, 16) for packet in TC_json['packet_types']]
    messages = []
    for json_msg in TC_json['messages']:
        fields = []
        for json_field in json_msg['fields']:
            field = Field(
                field_name=json_field.get('field_name', None),
                regex=json_field.get('regex', None),
                field_type=FieldType[json_field['field_type']],
                get_value=json_field['get_value']
            )
            fields.append(field)

        msg = Message(
            packet_type=int(json_msg['packet_type'], 16),
            subtitle=json_msg['subtitle'],
            fields=fields
        )
        messages.append(msg)
    return packet_types, messages


if __name__ == '__main__':
    input_filename = os.path.abspath('/home/techm/Desktop/QXDM_Log.isf')
    # output_filename = os.path.abspath('/home/techm/Desktop/parsed_QCAT.txt')

    print('QXDM log analysis started')
    qcat = QCAT()

    print('Test case 1 ')
    test_filename = 'src/qcat_tests/test_msg_8.json'
    output_filename = 'src/qcat_tests/result_test_msg_8.txt'
    packet_types, messages = parse_json(test_filename)
    qcat.set_packet_filter(packet_types)
    parsed_data = qcat.parse(input_filename, messages)

    with open(output_filename, 'w') as f:
        for data in parsed_data:
            qcat.write_parsed_data(data, f)

    # print('Test case 2')
    # TC2_packet_types = [0x156E]

    qcat.quit()
