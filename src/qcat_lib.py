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
        self.raw_messages = []
        self.parsed_messages = []
        self.validated_messages = []
        self.saved_values = {}

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

        self.raw_messages = []
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
            name = packet.Name()
            subtitle = packet.Subtitle()
            datetime = packet.TimestampAsString()
            packet_type = packet.Type()
            text = packet.Text()

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


def parse_json_config(filename):
    print('Loading test config:', filename)
    with open(filename) as f:
        TC_json = json.load(f)

    # print(json.dumps(TC_json, indent=2))

    test_name = TC_json['test_name']
    packet_types = [int(packet, 16) for packet in TC_json['packet_types']]

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
                packet_type=int(json_msg['packet_type'], 16),
                subtitle=json_msg['subtitle'],
                fields=fields,
                must_match_field=json_msg.get('must_match_field', None),
                saved_values=device_specs
            )
            messages.append(msg)
    return test_name, packet_types, messages, device_specs


def parse_log(input_filename, test_filename, raw_filename,
              parsed_filename, validated_filename, qcat):
    print('QXDM log analysis started')
    test_name, packet_types, messages, device_specs = parse_json_config(test_filename)

    print('Parsing:', test_name)

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
        for validated_msg in qcat.validated_messages:
            validated_msg_str = validated_msg.to_string()
            f.write(validated_msg_str)
    print('validated messages:', validated_filename)

    return True


if __name__ == '__main__':
    input_filename = os.path.abspath('/home/techm/Desktop/QXDM_Log.isf')
    # input_filename = os.path.abspath('/home/techm/Desktop/TC1/saved_test_2.isf')
    test_filename = 'src/qcat_tests/Test_case_2.json'
    output_filename = 'TC2_att'

    raw_filename = f'src/qcat_tests/result_raw_{output_filename}.txt'
    parsed_filename = f'src/qcat_tests/result_parsed_{output_filename}.txt'
    validated_filename = f'src/qcat_tests/result_validated_{output_filename}.txt'

    qcat = QCAT()
    parse_log(input_filename, test_filename, raw_filename, parsed_filename,
              validated_filename, qcat)

    qcat.quit()
