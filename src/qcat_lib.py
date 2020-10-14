from pydbus import SessionBus
import random
import subprocess
import time
import os
import json
from gi.repository import GLib, Gio

import message

'''
For reference, see following files:
 * /opt/qcom/QCAT/Script/QCATDBus.pm - launch app, packet filter, packets
 * /opt/qcom/QCAT/Script/FilterSample.pl - set packet filter
'''


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

        validated_messages, parsed_messages = [], []
        count = 0
        messages_iter = iter(messages)
        msg = None

        while packet:
            if not msg:
                msg = next(messages_iter)
            if msg.is_same_message_type(packet.Subtitle(),
                                        packet.Type(),
                                        packet.Text()):
                parsed_msg = msg.parse(packet.Name(),
                                       packet.TimestampAsString(),
                                       packet.Text())
                parsed_messages.append(parsed_msg)
                # validated_messages.append(parsed_message.validate())
                count += 1
                msg = None
            if not packet.Next():
                break

        print(count, 'packets loaded.')
        return parsed_messages, validated_messages

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
        f.write('\n\n')


def parse_json_config(filename):
    print('Loading test config:', filename)
    with open(filename) as f:
        TC_json = json.load(f)

    # print(json.dumps(TC_json, indent=2))

    test_name = TC_json['test_name']
    packet_types = [int(packet, 16) for packet in TC_json['packet_types']]
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
                    validation_type=json_field.get('validation_type', None)
                )
                fields.append(field)

            msg = message.Message(
                packet_type=int(json_msg['packet_type'], 16),
                subtitle=json_msg['subtitle'],
                fields=fields,
                must_match_field=json_msg.get('must_match_field', None)
            )
            messages.append(msg)
    return test_name, packet_types, messages


def parse_log(input_filename, test_filename, parsed_filename,
              validated_filename, qcat):
    print('QXDM log analysis started')
    test_name, packet_types, messages = parse_json_config(test_filename)

    print('Parsing:', test_name)

    qcat.set_packet_filter(packet_types)
    parsed_messages, validated_messages = qcat.parse(input_filename, messages)

    with open(parsed_filename, 'w') as f:
        for parsed_msg in parsed_messages:
            parsed_msg_str = parsed_msg.to_string()
            f.write(parsed_msg_str)
            # print(parsed_msg_str)

    with open(validated_filename, 'w') as f:
        for data in validated_messages:
            qcat.write_parsed_data(data, f)

    return True


if __name__ == '__main__':
    input_filename = os.path.abspath('/home/techm/Desktop/QXDM_Log.isf')
    test_filename = 'src/qcat_tests/Test_case_2.json'

    filename = (test_filename.split('/')[-1]).split('.')[0]
    parsed_filename = f'src/qcat_tests/parsed_{filename}.txt'
    validated_filename = f'src/qcat_tests/validated_{filename}.txt'

    qcat = QCAT()
    parse_log(input_filename, test_filename, parsed_filename,
              validated_filename, qcat)

    qcat.quit()
