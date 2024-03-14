from enum import Enum, auto
import re
import logging
import sys
import traceback
import json
import os
import datetime
from typing import List, Tuple, Any, Dict
import yaml
from packet_0xB063_processor import Packet_0xB063
from packet_0xB16B_processor import Packet_0xB16B
from packet_0xB126_processor import Packet_0xB126
from packet_0xB130_processor import Packet_0xB130
from packet_0xB132_processor import Packet_0xB132
from packet_0xB14D_processor import Packet_0xB14D
from packet_0xB0EE_processor import Packet_0xB0EE
from packet_0xB808_processor import Packet_0xB808
from packet_0xB809_processor import Packet_0xB809
from packet_0xB0E2_processor import Packet_0xB0E2
from packet_0xB192_processor import Packet_0xB192
from packet_0xB186_processor import Packet_0xB186
from packet_0xB181_processor import Packet_0xB181
from packet_0xB17E_processor import Packet_0xB17E
from packet_0xB179_processor import Packet_0xB179
from packet_0xB176_processor import Packet_0xB176
from packet_0xB173_processor import Packet_0xB173
from packet_0xB88A_processor import Packet_0xB88A
from packet_0xB828_processor import Packet_0xB828
from packet_0xB970_processor import Packet_0xB970
from packet_0xB887_processor import Packet_0xB887
from packet_0xB0F7_processor import Packet_0xB0F7
from packet_0x156A_processor import Packet_0x156A
from packet_0xB800_processor import Packet_0xB800
from packet_0xB80B_processor import Packet_0xB80B
from packet_0xB0C1_processor import Packet_0xB0C1
from packet_0x156E_processor import Packet_0x156E
from packet_0xB0E4_processor import Packet_0xB0E4
from packet_0xB0EC_processor import Packet_0xB0EC
from packet_0x1832_processor import Packet_0x1832
from packet_0xB0C2_processor import Packet_0xB0C2
from packet_0x1830_processor import Packet_0x1830
from packet_0x1831_processor import Packet_0x1831
from packet_0xB167_processor import Packet_0xB167
from packet_0x1569_processor import Packet_0x1569
from packet_0xB8D8_processor import Packet_0xB8D8
from packet_0xB823_processor import Packet_0xB823
from packet_0xB0E5_processor import Packet_0xB0E5
from packet_0xB822_processor import Packet_0xB822
from packet_0xB115_processor import Packet_0xB115
from packet_0xB166_processor import Packet_0xB166
from packet_0xB168_processor import Packet_0xB168
from packet_0xB169_processor import Packet_0xB169
from packet_0xB16A_processor import Packet_0xB16A
from packet_0xB80A_processor import Packet_0xB80A
from packet_0xB801_processor import Packet_0xB801
from packet_0xB825_processor import Packet_0xB825
from packet_0xB97F_processor import Packet_0xB97F
from packet_0xB8A7_processor import Packet_0xB8A7
from packet_0xB827_processor import Packet_0xB827
from packet_0xB18F_processor import Packet_0xB18F
from packet_0xB821_processor import Packet_0xB821
from packet_0xB0C0_processor import Packet_0xB0C0
from packet_0xB113_processor import Packet_0xB113
from packet_0xB171_processor import Packet_0xB171
from packet_0xB18E_processor import Packet_0xB18E
from packet_0xB196_processor import Packet_0xB196
from packet_0xB883_processor import Packet_0xB883
from packet_0xB884_processor import Packet_0xB884
from packet_0xB889_processor import Packet_0xB889
from packet_0x17F2_processor import Packet_0x17F2
from packet_0x1D4D_processor import Packet_0x1D4D
from packet_0xB16F_processor import Packet_0xB16F
from packet_0xB0E3_processor import Packet_0xB0E3
from packet_0xB16E_processor import Packet_0xB16E
from packet_0xB139_processor import Packet_0xB139
from packet_0xB060_processor import Packet_0xB060
from packet_0xB0A5_processor import Packet_0xB0A5
from packet_0xB0A1_processor import Packet_0xB0A1
from packet_0xB06E_processor import Packet_0xB06E
from packet_0xB062_processor import Packet_0xB062
from packet_0xB1DA_processor import Packet_0xB1DA
from packet_0xB081_processor import Packet_0xB081
from packet_0xB13C_processor import Packet_0xB13C
from packet_0xB16C_processor import Packet_0xB16C
from packet_0xB064_processor import Packet_0xB064
from packet_0xB0EF_processor import Packet_0xB0EF
from packet_0xB0B5_processor import Packet_0xB0B5
from packet_0xB0B4_processor import Packet_0xB0B4
from packet_0xB0B1_processor import Packet_0xB0B1
from packet_0x1568_processor import Packet_0x1568
from packet_0xB061_processor import Packet_0xB061

# Enum: Custom data type that contains fixed set of unique values
# Enum basically represents a list of different ways to check if something is correct
# auto: automatically assigns default unique values
# ValidationType: Enum that represents different ways to validate something
class ValidationType(Enum):
    FIRST_WORD_EXACT = auto()
    FIRST_WORD_ONE_OF = auto()  # TODO: prepend "one of: " to output for clarity
    FOUND_MATCH = auto()
    ANY_SUBSTRING = auto()
    FIRST_SAVE = auto()
    CHECK_SAVED = auto()
    CONCAT_AND_COMPARE = auto()
    COLLECTION = auto()  # TODO: prepend "contains all: " to output for clarity
    NUMBER_COMPARISON = auto()  # TODO: prepend how comparison is done to output for clarity
    DOES_NOT_CONTAIN = auto()
    STRING_MATCH_ONE_OF = auto()  # TODO: Figure out how to display mismatch


# Enum that contains different entries for result of field validation
class FieldResult(Enum):
    VALUE_MATCH = auto()
    VALUE_MISMATCH = auto()
    COLLECTION_MISMATCH = auto()
    FIELD_MISSING = auto()


# Enum that specifies whether the field is a value or a collection of values
class FieldType(Enum):
    VALUE = auto()
    COLLECTION = auto()


# Field is a class that represents a field to be validated.
# Contains attributes like field_name, regex, etc that are parameters to be validated.
class Field:
    def __init__(self, field_name: str, regex: str,
                 search_2: str, field_type: FieldType, get_value: str,
                 validation_type: ValidationType, expected_value: str,
                 validation_regex: str):
        self.field_name = field_name
        self.regex = regex
        self.search_2 = search_2
        self.field_type = field_type
        self.get_value = get_value
        self.expected_value = expected_value
        self.validation_type = validation_type
        self.validation_regex = validation_regex


# Class: Represents a field that has been parsed during validation.
# Contains attributes similar to Field class.
# New parameter: value - represents the parsed value
# found - bool that represents whether the field was found during parsing.
class ParsedField:
    def __init__(self, field: Field, value: str, found: bool = True):
        self.field_name = field.field_name
        self.field_type = field.field_type
        self.get_value = field.get_value
        self.expected_value = field.expected_value
        self.validation_type = field.validation_type
        self.validation_regex = field.validation_regex
        self.value = value
        self.found = found

    def __str__(self):
        return 'field_name: ' + self.field_name + '\nvalue: ' + self.value \
            + '\nfound: ' + str(self.found)


# This class represents the field after validation
# contains attribute result - result after validation
class ValidatedField:
    def __init__(self, field: ParsedField, value: str,
                 result: FieldResult):
        self.field_name = field.field_name
        self.field_type = field.field_type
        self.get_value = field.get_value
        self.expected_value = field.expected_value
        self.validation_type = field.validation_type
        self.original_value = field.value
        self.field_value = value
        self.result = result

    def __str__(self):
        return 'field_name: ' + self.field_name + '\nvalue: ' + self.value \
            + '\nfound: ' + str(self.found)


# represents the validated message.
# attributes included in message: description, name, subtitle,etc.
class ValidatedMessage:
    def __init__(self, description: str, name: str, subtitle: str,
                 datetime: str):
        self.description = description
        self.name = name
        self.subtitle = subtitle
        self.datetime = datetime
        self.fields = []

    # method that adds the field after validation
    def add_validated_field(self, field: ValidatedField):
        self.fields.append(field)

    # method that generates a string representation of the validated message
    def to_string(self):
        lines = []
        not_matching_fields = list(filter(
            lambda x: x.result == FieldResult.VALUE_MISMATCH or
                      x.result == FieldResult.COLLECTION_MISMATCH, self.fields))
        missing_fields = list(filter(
            lambda x: x.result == FieldResult.FIELD_MISSING, self.fields))

        lines.append('\n--------------------------------------------------------------------------------\n\n')
        lines.append('\n'.join(self.description) + '\n\n')
        if not (not_matching_fields or missing_fields):
            lines.append('PASS: All fields and expected values found\n')
        else:
            lines.append('FAIL:\n')
            if missing_fields:
                lines.append('\tFields missing:\n')
                for field in missing_fields:
                    lines.append(f'\t\t{field.field_name}\n')
            if not_matching_fields:
                lines.append('\tValues mismatch:\n')
                for field in not_matching_fields:
                    lines.append(f'\t\t{field.field_name}\n')
                    lines.append(f'\t\t\texpected: {field.expected_value}\n')
                    if field.field_type == FieldType.COLLECTION or \
                            type(field.field_value) == list:
                        lines.append(f'\t\t\tactual:   {field.field_value}\n')
                    else:
                        lines.append(f'\t\t\tactual:   {field.field_value}\n')

        lines.append(f'\nDatetime: {self.datetime}\n')
        lines.append(f'Name: {self.name}\n')
        if self.subtitle:
            lines.append(f'Subtitle: {self.subtitle}\n')
        if self.fields:
            lines.append('Fields:\n')
            # split fields into found and not found to process separately
            for field in self.fields:
                if field.result == FieldResult.FIELD_MISSING:
                    continue
                if field.field_type == FieldType.COLLECTION:
                    lines.append(f'\t{field.field_name}\n')
                    if len(field.field_value) > 1:
                        lines.append('\t[\n')
                        lines.append('\t\t' + '\n\t\t'.join(field.field_value))
                        lines.append('\n\t]\n')
                    else:
                        lines.append(f'\t\t{field.field_value[0]}\n')
                elif not field.get_value:
                    lines.append(f'\t{field.field_name}\n')
                elif type(field.field_value) == list:
                    lines.append('\t' + '\n\t'.join(field.original_value) + '\n')
                else:
                    lines.append(f'\t{field.original_value}\n')
        return ''.join(lines)

    def save_to_csv(self, writer):
        '''Saves processed messages to a CSV file.'''

        passing = list(filter(
            lambda x: x.result == FieldResult.VALUE_MATCH, self.fields))
        pass_fail = 'PASS' if len(passing) == len(self.fields) else 'FAIL'

        # write validation criteria
        writer.writerow({
            'Parameter Name': '\n'.join(self.description),
            'Pass/Fail': pass_fail,
            'Expected Value': '',
            'Actual Value': '',
        })

        # write message heading
        message_heading = f'Datetime: {self.datetime}\nName: {self.name}'
        if self.subtitle:
            message_heading += f'\nSubtitle: {self.subtitle}'
        writer.writerow({
            'Parameter Name': message_heading,
            'Pass/Fail': '',
            'Expected Value': '',
            'Actual Value': ''
        })

        # write fields
        for field in self.fields:
            if field.result == FieldResult.VALUE_MATCH:
                pass_fail = 'PASS'
            else:
                pass_fail = 'FAIL'

            expected, actual = field.expected_value, field.field_value

            if type(field.expected_value) == list:
                expected = '\n'.join(field.expected_value)
            if type(field.field_value) == list:
                actual = '\n'.join(field.field_value)

            if field.result == FieldResult.FIELD_MISSING:
                writer.writerow({
                    'Parameter Name': field.field_name,
                    'Pass/Fail': pass_fail,
                    'Expected Value': expected,
                    'Actual Value': '<Parameter missing>',
                })
            elif field.field_type == FieldType.COLLECTION:
                writer.writerow({
                    'Parameter Name': field.field_name,
                    'Pass/Fail': pass_fail,
                    'Expected Value': expected,
                    'Actual Value': actual,
                })
            elif not field.get_value:
                writer.writerow({
                    'Parameter Name': field.field_name,
                    'Pass/Fail': pass_fail,
                    'Expected Value': field.field_name,
                    'Actual Value': field.field_name,
                })
            else:
                writer.writerow({
                    'Parameter Name': field.field_name,
                    'Pass/Fail': pass_fail,
                    'Expected Value': expected,
                    'Actual Value': actual,
                })

        # write blank row
        writer.writerow({
            'Parameter Name': '',
            'Pass/Fail': '',
            'Expected Value': '',
            'Actual Value': ''
        })


def remove_prefix(s, prefix):
    '''Removes the prefix from the string if present, else returns string unchanged.'''
    return s[len(prefix):] if s.startswith(prefix) else s


def remove_space_equals_prefix(s):
    '''Remove spaces and equals signs from strings for data processing'''
    return re.sub('^(\\s|=)*', '', s)


def remove_parens(s):
    ''' Removes parantheses from strings for data processing'''
    return re.sub('\\(|\\)', '', s)


class ParsedMessage:
    '''defines the constructor method __init__ for ParsedMessage class

    contains attributes like description, name, subtitle, etc.

    Empty list fields: hold the parsed fields after parsing

    '''

    def __init__(self, description: str, name: str, subtitle: str,
                 datetime: str, saved_values: dict):
        self.description = description
        self.name = name
        self.subtitle = subtitle
        self.datetime = datetime
        self.fields = []
        self.saved_values = saved_values

    def add_parsed_field(self, field: ParsedField):
        '''Add the parsed fields to the list fields of the ParsedMessage object'''
        self.fields.append(field)

    def validate(self) -> ValidatedMessage:
        '''validates the message and returns a ValidatedMessage'''
        # compare each ParsedField against the validation rules for that field
        validated_message = ValidatedMessage(self.description, self.name,
                                             self.subtitle, self.datetime)

        for field in self.fields:
            validated_field, value, result = None, None, None
            if not field.found:
                result = FieldResult.FIELD_MISSING
            elif field.validation_type == ValidationType.FIRST_WORD_EXACT:
                value = remove_prefix(field.value, field.field_name)
                value = remove_space_equals_prefix(value)
                if value.split(' ')[0] == field.expected_value:
                    result = FieldResult.VALUE_MATCH
                else:
                    result = FieldResult.VALUE_MISMATCH
            elif field.validation_type == ValidationType.FIRST_WORD_ONE_OF:
                value = remove_prefix(field.value, field.field_name)
                value = remove_space_equals_prefix(value)
                if value.split(' ')[0] in field.expected_value:
                    result = FieldResult.VALUE_MATCH
                else:
                    result = FieldResult.VALUE_MISMATCH
            elif field.validation_type == ValidationType.ANY_SUBSTRING:
                value = remove_prefix(field.value, field.field_name)
                value = remove_space_equals_prefix(value)
                if field.expected_value in field.value:
                    result = FieldResult.VALUE_MATCH
                else:
                    result = FieldResult.VALUE_MISMATCH
            elif field.validation_type == ValidationType.FOUND_MATCH:
                if field.field_name in field.value:
                    result = FieldResult.VALUE_MATCH
                else:
                    result = FieldResult.FIELD_MISSING
                value = field.expected_value
            elif field.validation_type == ValidationType.FIRST_SAVE:
                value = remove_prefix(field.value, field.field_name)
                value = remove_space_equals_prefix(value)
                value = value.split(' ')[0]
                if field.field_name in self.saved_values:
                    result = FieldResult.VALUE_MISMATCH
                else:
                    self.saved_values[field.field_name] = value
                    result = FieldResult.VALUE_MATCH
                field.expected_value = '<Refer to later>'
            elif field.validation_type == ValidationType.CHECK_SAVED:
                value = remove_prefix(field.value, field.field_name)
                value = remove_space_equals_prefix(value)
                value = value.split(' ')[0]
                saved_value = self.saved_values.get(field.field_name, None)
                if saved_value and value == saved_value:
                    result = FieldResult.VALUE_MATCH
                else:
                    result = FieldResult.VALUE_MISMATCH
                field.expected_value = saved_value
            elif field.validation_type == ValidationType.CONCAT_AND_COMPARE:
                match = re.findall(field.validation_regex, ''.join(field.value))
                words = []
                word = []
                for i in range(len(match) + 1):
                    if i == len(match) or match[i] == '':
                        if word:
                            words.append(''.join(word))
                        word = []
                    else:
                        word.append(match[i])
                if words:
                    if field.expected_value in words:
                        result = FieldResult.VALUE_MATCH
                    else:
                        result = FieldResult.VALUE_MISMATCH
                    value = words
                else:
                    result = FieldResult.VALUE_MISMATCH
            elif field.validation_type == ValidationType.COLLECTION:
                value_lower = list(map(lambda x: x.lower(), field.value))
                for expected_value in field.expected_value:
                    if expected_value.lower() not in value_lower:
                        result = FieldResult.COLLECTION_MISMATCH
                        break
                else:
                    result = FieldResult.VALUE_MATCH
                value = field.value
            elif field.validation_type == ValidationType.NUMBER_COMPARISON:
                # actual value <= expected value
                value = remove_prefix(field.value, field.field_name)
                value = remove_space_equals_prefix(value)
                if int(value) <= int(field.expected_value):
                    result = FieldResult.VALUE_MATCH
                else:
                    result = FieldResult.VALUE_MISMATCH
            elif field.validation_type == ValidationType.STRING_MATCH_ONE_OF:
                match = re.findall(field.expected_value, ''.join(field.value))
                if match:
                    value = [el for el in match[0] if el != '']
                    # expected value should match actual value for demo
                    field.expected_value = value
                    result = FieldResult.VALUE_MATCH
                else:
                    # hardcoded validation if values do not match
                    result = FieldResult.VALUE_MISMATCH
                    if 'EVS' in field.value[0]:
                        evs = re.findall('EVS.*', field.value[0])[0]
                        br = re.findall('br=[0-9.-]*', field.value[1])[0]
                        bw = re.findall('bw=[a-zA-Z-]*', field.value[1])[0]
                        field.expected_value = ['EVS', 'br=5.9-24.4', 'bw=nb-swb']
                        value = [evs, br, bw]
                    else:
                        # check AMR-WB and AMR-NB used
                        amr_wb = re.findall('AMR-WB.*', field.value[0])[0]
                        amr_nb = re.findall('AMR-NB.*', field.value[1])[0]
                        field.expected_value = ['AMR-WB', 'AMR-NB']
                        value = [amr_wb, amr_nb]
            elif field.validation_type == ValidationType.DOES_NOT_CONTAIN:
                value = remove_prefix(field.value, field.field_name)
                value = remove_space_equals_prefix(value)
                if field.expected_value in remove_parens(value).split(' '):
                    result = FieldResult.VALUE_MISMATCH
                    field.expected_value = '(not) ' + field.expected_value
                else:
                    result = FieldResult.VALUE_MATCH
            else:
                raise ValueError('validation_type is unspecified:',
                                 field.validation_type)

            validated_field = ValidatedField(field, value, result)
            validated_message.add_validated_field(validated_field)

        if not self.fields:
            # message was found but it has no fields TC1.4
            pass

        return validated_message

    def to_string(self):
        lines = []
        lines.append(f'Datetime: {self.datetime}\n')
        lines.append(f'Name: {self.name}\n')
        if self.subtitle:
            lines.append(f'Subtitle: {self.subtitle}\n')
        if self.fields:
            lines.append('Fields:\n')
            # split fields into found and not found to process separately
            for field in sorted(self.fields, key=lambda f: not f.found):
                # print(field)
                if not field.found:
                    lines.append(f'**MISSING** {field.field_name}\n')
                elif field.field_type == FieldType.COLLECTION:
                    lines.append(f'\t{field.field_name}\n')
                    lines.append('\t[\n')
                    lines.append('\t\t' + '\n\t\t'.join(field.value))
                    lines.append('\n\t]\n')
                elif not field.get_value:
                    lines.append(f'\t{field.field_name}\n')
                elif type(field.value) == list:
                    lines.append('\t' + '\n\t'.join(field.value) + '\n')
                else:
                    lines.append(f'\t{field.value}\n')
        lines.append('\n')
        return ''.join(lines)

    def write_to_file():
        pass

    def __str__(self):
        return self.subtitle


class RawMessage:
    def __init__(self, name: str, subtitle: str, datetime: str,
                 packet_text: str):
        self.name = name
        self.subtitle = subtitle
        self.datetime = datetime
        self.packet_text = packet_text

    def to_string(self):
        lines = []
        lines.append(f'Datetime: {self.datetime}\n')
        lines.append(f'Name: {self.name}\n')
        if self.subtitle:
            lines.append(f'Subtitle: {self.subtitle}\n')
        lines.append('Text:\n')
        lines.append(self.packet_text)
        lines.append('\n')
        return ''.join(lines)


class ParsedRawMessage:
    VERSION = 2

    INT_REGEX = r'^[-+]?\d+$'
    FLOAT_REGEX = r'^[-+]?[0-9]*\.[0-9]+([eE][-+]?[0-9]+)?$'

    packet_config = None

    def __init__(self, index: int, packet_type: Any, packet_length: int, name: str, subtitle: str, datetime: str,
                 packet_text: str):
        self.index = index
        if isinstance(packet_type, int):
            self.packet_type = packet_type
            self.packet_type_hex = hex(self.packet_type)
        else:
            self.packet_type_hex = packet_type
            self.packet_type = int(self.packet_type_hex, 16)
        self.packet_length = packet_length
        self.name = name
        self.subtitle = subtitle
        self.datetime = datetime
        self.packet_text = packet_text

    def to_string(self):
        lines = []
        lines.append(f'Index: {self.index}\n')
        lines.append(f'Packet type: {self.packet_type}\n')
        lines.append(f'Name: {self.name}\n')
        lines.append(f'Datetime: {self.datetime}\n')
        lines.append(f'Length: {self.packet_length}\n')
        if self.subtitle:
            lines.append(f'Subtitle: {self.subtitle}\n')
        lines.append('Text:\n')
        lines.append(self.packet_text)
        lines.append('\n')
        return ''.join(lines)

    def test(self):
        data = self.parse_payload()
        return data

    def to_json(self):
        try:
            data = self.parse_payload()
        except:
            traceback.print_exc()
            logging.info(self.index)
            sys.stdout.flush()
            sys.stderr.flush()
            parsedPayload = {}
            flags = {}
        return parsedPayload, {
            "_index": self.index,
            "_packetType": hex(int(self.packet_type)),
            "_packetTypeInt": int(self.packet_type),
            "_name": self.name,
            "_datetime": self.datetime,
            "_length": self.packet_length,
            "_subtitle": self.subtitle if self.subtitle else "",
            "_rawPayload": self.packet_text,
            "_parserVersion": ParsedRawMessage.VERSION,
            "_flags": flags,
        }

    def parse_payload(self):
        class TYPE_FLAGS(str, Enum):
            SINGLE_ROW_TABLE = "SINGLE_ROW_TABLE"
            MULTI_ROW_TABLE = "MULTI_ROW_TABLE"

        TABLE_PACKET_TYPES = [
            "0xB825",
            "0xb97f",
            "0xb0c0",
            "0xb0ed",
            "0xb0ec",
            "0xb0e2",
            "0xb0e3",
            "0xb821",
            "0xb814",
            "0xb80b",
            "0xb809",
            "0xb808",
            "0xb80a",
            "0xb801",
            "0xb800",
            "0xb14d",
            "0xb8a7",
            "0xb193",
            "0xb173",
            "0xb887",
            "0xb825",
        ]

        payload = {}

        #################################
        # HELPER METHODS
        #################################

        # remove extra whitespaces
        def _clean(val: str):
            val = re.sub(r'[^\S\n]+', ' ', val).strip()
            return val

        def _clean_key_val(_key: str, _val: str):
            key = _clean(_key)
            val = _clean(_val)
            val = _parse_val_primitive(val)
            return key, val

        # clean and parse values into primitives, turn duplicate keys to contain array of values
        def _insert_cleaned(_obj: dict, _key: str, _val: str):
            key = _clean(_key)
            val = _clean(_val)
            val = _parse_val_primitive(val)

            if key not in _obj:
                _obj[key] = val
            else:
                if isinstance(_obj[key], list):
                    _obj[key] = [*_obj[key], val]
                else:
                    _obj[key] = [_obj[key], val]

        # parse primitive data types if any
        def _parse_val_primitive(val: str):
            if (val.lower() == 'true'):
                return True
            elif (val.lower() == 'false'):
                return False
            elif (re.match(ParsedRawMessage.INT_REGEX, val)):
                int_val = int(val)
                if int_val < -9223372036854775808 or int_val > 9223372036854775807:
                    print(f'Huge {self.index}: {val}')
                    return val
                return int_val
            elif (re.match(ParsedRawMessage.FLOAT_REGEX, val)):
                return float(val)
            else:
                return val

        # find the first occurance of an assignment symbol (equals, colon)
        # to split line on that to key-value pair
        def _find_splitter(line: str):
            symbols = [":", "="]
            indices = [line.find(symbol) for symbol in symbols]

            if not any(indices):
                return None

            filtered_indices = list(filter(lambda x: x >= 0, indices))
            if not any(filtered_indices):
                return None

            first_symbol = symbols[indices.index(min(filtered_indices))]

            return first_symbol

        def _is_struct_end(line: str):
            line = line.strip()
            return line.endswith('}') and '{' not in line

        def _is_struct_start(line: str):
            line = line.strip()
            return line.endswith('{')

        #####

        def _try_parse_multiline(lines: list[str], _obj: dict):
            i = 0
            while i < len(lines):
                if i + 1 < len(lines):
                    j = i + 1
                    key_splitter = _find_splitter(lines[i])
                    splitter = _find_splitter(lines[j])
                    if splitter is None:
                        # multiline array-like data
                        # walk each line until the next splitable line is encountered
                        # parse everything inbetween as a multiline value
                        while splitter is None and j < len(lines):
                            j += 1
                            if j < len(lines):
                                splitter = _find_splitter(lines[j])
                        multiline_val = _multiline_parse(lines[i:j], _obj)
                        if isinstance(multiline_val, list):
                            generic_start_key = lines[i].split(key_splitter)
                            _obj[generic_start_key] = multiline_val
                        i = j
                        continue
                    else:
                        _key_value_parse([lines[i]], _obj)
                else:
                    _key_value_parse([lines[i]], _obj)

                i += 1

        #################################
        # PARSERS
        #################################

        # generic key-value pair parsing
        def _key_value_parse(lines: list[str], _obj: dict):
            for line in lines:
                generic_splitter = _find_splitter(line)
                if generic_splitter == None:
                    if "," in line:
                        arr = [_parse_val_primitive(_clean(entry)) for entry in line.split(",")]
                        return arr
                    else:
                        _insert_cleaned(_obj, line, "")
                else:
                    key, val = line.split(generic_splitter, 1)
                    # split { ... } type values into array
                    if val.strip().startswith('{') and val.strip().endswith('}'):
                        val = [_parse_val_primitive(_clean(entry)) for entry in val.strip()[1:-1].strip().split(',')]
                        _obj[_parse_val_primitive(_clean(key))] = val
                    else:
                        _insert_cleaned(_obj, key, val)

        # multiline value parsing
        def _multiline_parse(lines: list[str], _obj: dict):
            # split first line
            splitter = _find_splitter(lines[0])

            # if array type
            if splitter is None:
                block = " ".join(lines)
                return [_parse_val_primitive(_clean(entry)) for entry in block.split(",")]
            else:
                # else join lines by \n character
                key, val = lines[0].split(splitter, 1)

                key = _clean(key)
                val = val + "\n" + "\n".join(lines[1:])
                val = _parse_val_primitive(_clean(val))
                _obj[key] = val

        def _QtraceMessage(lines: list[str], _obj: dict):
            #

            if len(lines) > 0:
                i = 0
                while i < len(lines):
                    line = lines[i].strip()
                    if 'ENL2UL   |' in line:
                        self.subtitle = 'ENL2UL'
                        _obj['Technology'] = 'NR'
                    elif 'ENL2DL   |' in line:
                        self.subtitle = 'ENL2DL'
                        _obj['Technology'] = 'NR'
                    elif 'NR5GMAC  |' in line:
                        self.subtitle = 'NR5GMAC'
                        _obj['Technology'] = 'NR'
                    else:
                        return False
                    rows = line.split('|')
                    j = 0
                    while j < len(rows):
                        rowdata = rows[j]
                        if j == 0:
                            if 'Sub-ID:1' in rowdata:
                                _obj['Subscription ID'] = 1
                            elif 'Sub-ID:0' in rowdata:
                                _obj['Subscription ID'] = 0
                        elif j < 3:
                            if ':' in rowdata:
                                key_value = rowdata.split(':')
                                key = key_value[0].strip().replace('{', '')

                                value = ':'.join(key_value[1:]).strip().replace('}', '')
                                _obj[key] = value
                                if key == 'tput.kbps':
                                    _obj['Sub-Type'] = key
                                    valueArr = value.replace('[', '').replace(']', '').split(';')
                                    k = 0
                                    while k < len(valueArr):
                                        valueLine = valueArr[k]
                                        if ':' in valueLine:
                                            key_value = valueLine.split(':')
                                            keyChild = key_value[0].strip()
                                            valueChild = ':'.join(key_value[1:]).strip().replace('}', '')
                                            _obj[keyChild] = valueChild
                                        k += 1


                            else:
                                if rowdata != ' NR ':
                                    _obj['Sub-Type'] = rowdata.strip()
                        else:
                            if ':' in rowdata:
                                key_value = rowdata.split(':')
                                key = key_value[0].strip()
                                value = ':'.join(key_value[1:]).strip()
                                _obj[key] = value
                        j += 1
                    i += 1
                return True
            else:
                return False

        def _QtraceEvent(lines: list[str], _obj: dict):
            if len(lines) > 0:
                i = 0
                while i < len(lines):
                    line = lines[i].strip()
                    if 'QEvent 0x' in line:
                        _obj['Sub-Type'] = line.split('|')[1].strip()

                        _obj['QEvent'] = '0x' + line.split('QEvent 0x')[1].split(' ')[0].strip()
                        if self.subtitle == 'QEVENT 87 - 10' or self.subtitle == 'QEVENT 84 - 41' or self.subtitle == 'QEVENT 13 - 77':
                            _obj['eventInfo'] = line.split('|')[3].strip()
                        rows = line.split('|')
                        j = 0
                        while j < len(rows):
                            rowdata = rows[j]
                            if j == 0:
                                if 'Sub-ID:1' in rowdata:
                                    _obj['Subscription ID'] = 1
                                elif 'Sub-ID:0' in rowdata:
                                    _obj['Subscription ID'] = 0
                                if 'Misc-ID:1' in rowdata:
                                    _obj['Misc ID'] = 1
                                elif 'Misc-ID:0' in rowdata:
                                    _obj['Misc ID'] = 0
                            else:
                                if '=' in rowdata:
                                    key_value = rowdata.split('=')
                                    key = key_value[0].strip()
                                    if '=' in key_value[1]:
                                        otherData = '='.join(key_value[1:]).strip()
                                        otherRows = otherData.split(' ')
                                        rows += otherRows[1:]
                                    else:
                                        value = key_value[1].strip()
                                elif ':' in rowdata:
                                    if '[' in rowdata:
                                        if ']' not in rowdata:
                                            j += 1
                                            rowdata = rowdata + ',' + rows[j]
                                    key_value = rowdata.split(':')
                                    key = key_value[0].strip()
                                    value = ':'.join(key_value[1:]).strip()
                                    _obj[key] = value
                            j += 1

                    i += 1
                return True
            else:
                return False

        def _struct_or_generic_parse(lines: list[str], _obj: dict):
            try:
                has_structs = False

                def _obj_to_arr(stack: List[Tuple[str, Any]], val):
                    # convert the tuple to a list,
                    # change the 2nd index (object) to the resulting array
                    # and convert the list back to a tuple
                    last_entry = list(stack.pop())
                    last_entry[1] = val
                    stack.append((last_entry[0], last_entry[1]))

                # do deep parsing of class/struct type data
                def _deep(lines: list[str]):
                    stack: List[Tuple[str, Any]] = []
                    i = 0
                    while i < len(lines):
                        parse_value = None
                        line = lines[i]
                        line = line.strip()
                        if line.endswith('{'):
                            # push parent key and new empty object to top of the stack
                            key = line[:-1].strip().replace(':', "").replace('=', "").strip()
                            stack.append((key, {}))
                        elif _is_struct_end(line):
                            # found end of parent object, pop the last element
                            # and assign its key and value to the previous (parent) object
                            deep_key, deep_obj = stack.pop()
                            if any(stack):
                                stack[-1][1][deep_key] = deep_obj
                            # if stack is empty, we are done deep parsing
                            else:
                                return deep_key, deep_obj
                        else:
                            # Process key-value pairs
                            if i + 1 < len(lines):
                                j = i + 1
                                if not _is_struct_end(lines[j]):
                                    splitter = _find_splitter(lines[j])
                                    if splitter is None:
                                        # multiline array-like data
                                        while splitter is None and j < len(lines):
                                            if lines[j].endswith('{') or _is_struct_end(lines[j]):
                                                break
                                            j += 1
                                            splitter = _find_splitter(lines[j])
                                        multiline_val = _multiline_parse(lines[i:j], stack[-1][1])
                                        if isinstance(multiline_val, list):
                                            _obj_to_arr(stack, multiline_val)
                                        i = j
                                        continue

                                    else:
                                        parse_value = _key_value_parse([line], stack[-1][1])
                                else:
                                    parse_value = _key_value_parse([line], stack[-1][1])
                            else:
                                parse_value = _key_value_parse([line], stack[-1][1])

                        if parse_value is not None:
                            _obj_to_arr(stack, parse_value)
                        i += 1

                    deep_key, deep_obj = stack.pop()
                    return deep_key, deep_obj

                if len(lines) > 0:
                    i = 0
                    generic_start = 0
                    brackets = 0

                    # loop over payload to find struct {} blocks
                    while i < len(lines):
                        line = lines[i].strip()
                        if line.endswith("{"):
                            brackets += 1
                            j = i + 1
                            # find and contain the parent struct block
                            while j < len(lines) and brackets > 0:
                                if _is_struct_end(lines[j]):
                                    brackets -= 1
                                if brackets == 0: break
                                if lines[j].strip().endswith("{"):
                                    brackets += 1
                                j += 1

                            # found start and end of struct block,
                            # do deep parsing
                            key, content = _deep(lines[i:j + 1])

                            # if we have generic key-value pairs in between struct blocks,
                            # add them to the parent object before assigning the deep-parsed obj
                            if i > generic_start:
                                _key_value_parse(lines[generic_start:i], _obj)

                            _obj[key] = content

                            i = j
                            generic_start = j + 1
                            has_structs = True
                        i += 1

                    # parse the remainder of generic lines
                    if i > generic_start and not _is_struct_end(lines[i - 1]):
                        _try_parse_multiline(lines[generic_start:i], _obj)

                return has_structs

            except:
                # catch any faulty block parsing
                pass
                # traceback.print_exc()
                # logging.info(self.index)
                # sys.stdout.flush()
                # sys.stderr.flush()

        # parse payloads that are encoded in hex
        def _hex_payload(lines: list[str]):
            if len(lines) > 0 and lines[0] == "Payload:":
                payload["Payload"] = " ".join(lines[1:]) if len(lines[1:]) > 0 else ""
                return True
            return False

        def _tables(lines: list[str], _obj: dict):
            TABLE_BOUNDARIES_REGEX = r'^-+$'
            TABLE_VERTICAL_BOUNDARY_REGEX = r'^\|'
            TABLE_VERTICAL_BOUNDARY = "|"
            print(lines)
            flags = {}
            # find a table start and end
            table_name = "TABLE"
            table_start = 0
            table_cols_start: int = None
            table_cols_end: int = None
            table_rows_start: int = None
            table_rows_end: int = None
            generic_parse_done = False
            first_table_start = None

            def _parse_table(lines: list[str], _obj: dict):
                # find the max number of columns in the table
                max_col_number = lines[table_cols_end].count(TABLE_VERTICAL_BOUNDARY) - 1

                # parse column structure as a tree, eg:
                # """
                #                |Bit Width
                #  SB Result     |   |  |       |   |PMI |PMI|  |PMI
                #     |SB|SB |SB |   |  |Zero   |WB |WB  |WB |  |SB
                #  #  |ID|CQI|PMI|CRI|RI|Padding|CQI|X1  |X2 |LI|X2
                # """
                def _parse_cols(lines: list[str]) -> list[list[str]]:
                    cols: list[str] = []
                    print("lines before  getting reversed", lines)
                    lines.reverse()
                    bottom_most_names_and_len: list[(str, int)] = []
                    for r_index, row in enumerate(lines):
                        row = row.strip()
                        row = row[1:len(row) - 1]
                        split_row = row.split(TABLE_VERTICAL_BOUNDARY)
                        skipped_bottom_cols = 0
                        for c_index, col_name in enumerate(split_row):
                            if r_index > 0:
                                len_of_current = len(col_name)
                                index = c_index + skipped_bottom_cols
                                while len_of_current > 0:
                                    len_of_bottom_most_col = bottom_most_names_and_len[index][
                                                                 1] + 1  # add 1 to compensate for removed TABLE_BOUNDARY character
                                    stripped_col_name = col_name.strip()
                                    if len(stripped_col_name) > 0:
                                        cols[index] = stripped_col_name + " " + cols[index]
                                    index += 1
                                    if index > max_col_number - 1:
                                        break
                                    len_of_current -= len_of_bottom_most_col
                                    if len_of_current > 0:
                                        skipped_bottom_cols += 1
                            else:
                                bottom_most_names_and_len.append((col_name, len(col_name)))
                                cols.append(col_name.strip())

                    return cols

                columns = _parse_cols(lines[table_cols_start:table_cols_end + 1])

                all_parsed_rows: List[Dict[str, Any]] = []

                # parse table data rows into arrays of objects with key-val
                for i in range(table_rows_start, table_rows_end):
                    row = lines[i].strip()
                    row = row[1:len(row) - 1]
                    data = row.split(TABLE_VERTICAL_BOUNDARY)
                    parsed_row_data: Dict[str, Any] = {}
                    for j, field in enumerate(data):
                        _insert_cleaned(parsed_row_data, columns[j], field)
                    all_parsed_rows.append(parsed_row_data)

                _obj[table_name] = all_parsed_rows

            for i in range(len(lines)):
                line = lines[i].strip()
                # table columns start, aka ---------------
                if not table_cols_start and re.match(TABLE_BOUNDARIES_REGEX, line):
                    table_cols_start = i + 1
                    table_start = i - 1 if i > 0 else i
                    if not first_table_start:
                        first_table_start = table_start
                    table_name = lines[table_start].strip()  # the previous line is the table name
                    continue

                # table columns end, aka ---------------
                if not table_cols_end and re.match(TABLE_BOUNDARIES_REGEX, line):
                    table_cols_end = i - 1
                    table_rows_start = i + 1
                    table_rows_end = table_rows_start + 1
                    while table_rows_end < len(lines) and re.match(TABLE_VERTICAL_BOUNDARY_REGEX,
                                                                   lines[table_rows_end].strip()):
                        table_rows_end += 1

                if table_cols_start and table_cols_end and table_rows_start and table_rows_end:
                    if not generic_parse_done:
                        # parse the rest of the payload (non-table data)
                        # _struct_or_generic_parse(lines[0:first_table_start], _obj)
                        _parse_indented_structure(lines[0:first_table_start], _obj)
                        generic_parse_done = True
                    if table_rows_end - table_rows_start >= 2:
                        flags[table_name] = TYPE_FLAGS.MULTI_ROW_TABLE
                    else:
                        flags[table_name] = TYPE_FLAGS.SINGLE_ROW_TABLE
                    _parse_table(lines, _obj)
                    table_name = "TABLE"
                    table_start = 0
                    table_cols_start: int = None
                    table_cols_end: int = None
                    table_rows_start: int = None
                    table_rows_end: int = None

            if not generic_parse_done:
                # parse the rest of the payload (non-table data) if not already parsed
                # _struct_or_generic_parse(lines[0:first_table_start], _obj)
                _parse_indented_structure(lines[0:first_table_start], _obj)

            return flags

        def _parse_indented_structure(lines: list[str], _obj: dict):
            stack = [_obj]

            # count number of spaces per indentation
            num_spaces = 0
            for line in lines:
                if line.startswith(' '):
                    for ic, char in enumerate(line):
                        if char != ' ':
                            num_spaces = line[:ic].count(" ")
                            break
                    break

            # handle commas
            new_lines: list[str] = []
            for line in lines:
                if "," in line and ("=" in line or ":" in line):
                    split_lines = line.split(',')
                    first_line = split_lines[0].rstrip()
                    new_lines += [first_line, *[split_line.strip() for split_line in split_lines[1:]]]
                else:
                    new_lines.append(line)

            for line in new_lines:
                if not line.strip():
                    continue

                indent_level = line.count(' ' * num_spaces)

                if ':' in line:
                    key_value = line.strip().split(':')
                elif '=' in line:
                    key_value = line.strip().split('=')
                else:
                    key_value = line.strip().split(',')

                if len(key_value) == 1:
                    key = key_value[0].strip()
                    value = None
                else:
                    key = key_value[0].strip()
                    value = [item.strip() for item in key_value[1:]]

                while indent_level < len(stack) - 1:
                    stack.pop()

                current_dict = stack[-1]
                if value is not None:
                    current_dict[key] = value if len(value) > 1 else value[0]
                else:
                    current_dict[key] = {}
                    stack.append(current_dict[key])

        def _apply_parsing_config(_obj: dict, _flags: dict) -> dict:
            packet_type_hex = "0x" + self.packet_type_hex[2:].upper()
            packet_type = (
                packet_type_hex + " -- " + self.subtitle
                if self.subtitle and len(self.subtitle) > 0
                else packet_type_hex
            )
            output = {}
            if packet_type in self.packet_config:
                parsing_config_type = self.packet_config[packet_type]
                for key, value in parsing_config_type["fields"].items():
                    if isinstance(value, list):
                        if key in _flags:
                            if _flags[key] == TYPE_FLAGS.MULTI_ROW_TABLE:
                                arr = []
                                for entry in _obj[key]:
                                    new_entry = {**output}
                                    for record in value:
                                        k_record = list(record.keys())[0]
                                        new_entry[k_record] = entry[k_record]
                                    arr.append(new_entry)
                                if len(arr) > 0:
                                    output = arr
                            else:
                                for record in value:
                                    k_record = list(record.keys())[0]
                                    if k_record in _obj[key][0]:
                                        output[k_record] = _obj[key][0][k_record]
                        else:
                            continue

                    elif key in _obj:
                        output[key] = _obj[key]
                    elif "." in key:
                        key_parts = key.split(".")
                        curr_obj = _obj
                        final_key_part = ""
                        for key_part in key_parts:
                            if key_part in curr_obj:
                                curr_obj = curr_obj[key_part]
                                final_key_part = key_part
                        if key_parts[-1:][0] == final_key_part:
                            output[final_key_part] = curr_obj

                _obj.clear()
                if isinstance(output, list):
                    _obj["TABLE"] = output
                else:
                    _obj.update(output)
            else:
                _obj.clear()

        # START PARSING
        def _PARSE(packet_name, packet_text, entry):
            with open('input.json') as f:
                config = json.load(f)
            with open('P2.json') as f:
                config2 = json.load(f)
            with open('P3.json') as f:
                config3 = json.load(f)
            if packet_name == '0xB0E5':
                print("0xB0E5")
                return Packet_0xB0E5.extract_info(packet_text, config['0xB0E5 -- LTE -- NAS'], entry)
            elif packet_name == "0x156E":
                print("0x156E")
                return Packet_0x156E.extract_info(packet_text, config['0x156E -- IMS -- IMS_SIP_INVITE'],entry)
            elif packet_name == "0x156A":
                print("0x156A")
                return Packet_0x156A.extract_info(packet_text, config['0x156A -- IMS'],entry)
            elif packet_name == "0xB0C1":
                print("0xB0C1")
                return Packet_0xB0C1.extract_info(packet_text, config['0xB0C1 -- LTE-- RRC'],entry)
            elif packet_name == "0xB0F7":
                print("0xB0F7")
                return Packet_0xB0F7.extract_info(packet_text, config['0xB0F7 -- LTE'],entry)
            elif packet_name == "0xB80B":
                print("0xB80B")
                return Packet_0xB80B.extract_info(packet_text, config['0xB80B -- NR5G -- Packet Subtitle'],entry)
            elif packet_name == "0xB800":
                print("0xB800")
                return Packet_0xB800.extract_info(packet_text, config['0xB800 -- NR5G -- PDU session release req'],entry)
            elif packet_name =="0xB0EC":
                print("0xB0EC")
                return Packet_0xB0EC.extract_info(packet_text, config["0xB0EC -- LTE -- msg_type"],entry)
            elif packet_name =="0xB0E4":
                print("0xB0E4")
                return Packet_0xB0E4.extract_info(packet_text, config["0xB0E4 -- LTE -- NAS"],entry)
            elif packet_name =="0xB0C2":
                print("0xB0C2")
                return Packet_0xB0C2.extract_info(packet_text, config["0xB0C2 -- Cell -- Cell Info"],entry)
            elif packet_name == "0x1832":
                print("0x1832")
                return Packet_0x1832.extract_info(packet_text, config["0x1832 -- IMS -- IMS_SIP_REGISTER/INFORMAL_RESPONSE"],entry)
            elif packet_name == '0xB822':
                print("0xB822")
                return Packet_0xB822.extract_info(packet_text, config['0xB822  -- NR5G'], entry)
            elif packet_name == '0xB115':
                print("0xB115")
                return Packet_0xB115(packet_text, config['0xB115'], entry).extract_info()
            elif packet_name == "0x1831":
                print("0x1831")
                return Packet_0x1831.extract_info(packet_text, config["0x1831 -- IMS -- Direction"],entry)
            elif packet_name == "0x1830":
                print("0x1830")
                return Packet_0x1830.extract_info(packet_text, config["0x1830 -- IMS -- Direction"],entry)
            elif packet_name == '0xB166':
                print("0xB166")
                return Packet_0xB166.extract_info(packet_text, config['0xB166 -- Pcell -- PRACH'], entry)
            elif packet_name == '0xB168':
                print("0xB168")
                return Packet_0xB168.extract_info(packet_text, config['0xB168 -- PCC'], entry)
            elif packet_name == '0xB169':
                print("0xB169")
                return Packet_0xB169.extract_info(packet_text, config['0xB169 -- PCC'], entry)
            elif packet_name == '0xB16A':
                print("0xB16A")
                return Packet_0xB16A.extract_info(packet_text, config['0xB16A'], entry)
            elif packet_name == '0xB8D8':
                print("0xB8D8")
                return Packet_0xB8D8.extract_info(packet_text, config['0xB8D8 -- PCC -- Reference Signal = SSB'],entry)
            elif packet_name == '0xB167':
                print("0xB167")
                return Packet_0xB167.extract_info(packet_text, config["0xB167"],entry)
            elif packet_name == "0x1569":
                print("0x1569")
                return Packet_0x1569.extract_info(packet_text, config['0x1569 -- IMS'], entry)
            elif packet_name == '0xB823':
                print("0xB823")
                return Packet_0xB823.extract_info(packet_text, config['0xB823 -- NR5G'], entry)
            elif packet_name == '0xB887':
                print('0xB887')
                return Packet_0xB887(packet_text, config['0xB887 -- PCC -- PDSCH'], entry).extract_info()
            elif packet_name == '0xB801':
                print('0xB801')
                return Packet_0xB801.extract_info(packet_text, config["0xB801 -- NR5G -- Packet Subtitle"], entry)
            elif packet_name == '0xB80A':
                print('0xB80A')
                return Packet_0xB80A.extract_info(packet_text, config["0xB80A -- NR5G -- Packet Subtitle"], entry)
            elif packet_name == '0xB825':
                print('0xB825')
                return Packet_0xB825.extract_info(packet_text, config["0xB825 -- PCC -- NSA"], entry)
            elif packet_name == "0xB97F":
                print("0xB97F")
                return Packet_0xB97F(packet_text, config['0xB97F -- PCC'], entry).extract_info()
                # entry,table_lines = Packet_0xB825.extract_info(packet_text, config["0xB825 -- PCC -- NSA"], entry)
                # return _tables(table_lines, entry)
            elif packet_name == '0xB8A7':
                print('0xB8A7')
                return Packet_0xB8A7(packet_text, config['0xB8A7 -- PCC'], entry).extract_info()
            elif packet_name == '0xB827':
                print('0xB827')
                return Packet_0xB827(packet_text, config['0xB827 -- NR5G'], entry).extract_info()
            elif packet_name == '0xB18F':
                print('0xB18F')
                return Packet_0xB18F(packet_text, config['0xB18F -- LTE'], entry).extract_info()
            elif packet_name == '0xB821':
                print('0xB821')
                return Packet_0xB821.extract_info(packet_text, config['0xB821 -- NR5G -- Packet Subtitle'], entry)
            elif packet_name == '0xB0C0':
                print('0xB0C0')
                return Packet_0xB0C0.extract_info(packet_text, config['0xB0C0 -- LTE -- Packet Subtitle'], entry)
            elif packet_name == '0xB113':
                print('0xB113')
                return Packet_0xB113(packet_text, config['0xB113 -- LTE'], entry).extract_info()
            elif packet_name == '0xB171':
                print('0xB171')
                return Packet_0xB171(packet_text, config['0xB171 -- PCC -- SRS'], entry).extract_info()
            elif packet_name == '0xB18E':
                print('0xB18E')
                return Packet_0xB18E(packet_text, config['0xB18E -- PCell/SCelln'], entry).extract_info()
            elif packet_name == '0xB196':
                print('0xB196')
                return Packet_0xB196(packet_text, config['0xB196 -- PCell/SCelln'], entry).extract_info()
            elif packet_name == '0xB88A':
                print('0xB88A')
                return Packet_0xB88A.extract_info(packet_text, config2['0xB88A'], entry)
            elif packet_name == '0xB828':
                print('0xB828')
                return Packet_0xB828(packet_text, config2['0xB828  NR5G RRC PLMN Search Response'], entry).extract_info()
            elif packet_name == '0xB970':
                print('0xB970')
                return Packet_0xB970.extract_info(packet_text, config2['0xB970  NR5G ML1 Searcher Idle S Criteria'], entry)
            elif packet_name == '0xB883':
                print('0xB883')
                return Packet_0xB883(packet_text, config2['0xB883  NR5G MAC UL Physical Channel Schedule Report'], entry).extract_info()
            elif packet_name == '0xB884':
                print('0xB884')
                return Packet_0xB884(packet_text, config2['0xB884  NR5G MAC UL Physical Channel Power Control'], entry).extract_info()
            elif packet_name == '0xB889':
                print('0xB889')
                return Packet_0xB889(packet_text, config2['0xB889  NR5G MAC RACH Trigger'], entry).extract_info()
            elif packet_name == '0xB173':
                print('0xB173')
                return Packet_0xB173(packet_text, config2['0xB173 LTE PDSCH Stat Indication'], entry).extract_info()
            elif packet_name == '0xB176':
                print('0xB176')
                return Packet_0xB176.extract_info(packet_text, config2['0xB176  LTE Initial Acquisition Results'], entry)
            elif packet_name == '0xB179':
                print('0xB179')
                return Packet_0xB179.extract_info(packet_text, config2['0xB179  LTE ML1 Connected Mode LTE Intra-Freq Meas Results'], entry)
            elif packet_name == '0xB17E':
                print('0xB17E')
                return Packet_0xB17E.extract_info(packet_text, config2['0xB17E  LTE ML1 UE Mobility State change'], entry)
            elif packet_name == '0xB181':
                print('0xB181')
                return Packet_0xB181.extract_info(packet_text, config2['0xB181  LTE ML1 Intra Frequency Cell Reselection'], entry)
            elif packet_name == '0xB186':
                print('0xB186')
                return Packet_0xB186.extract_info(packet_text, config2['0xB186  LTE ML1 Reselection Candidates'], entry)
            elif packet_name == '0xB192':
                print('0xB192')
                return Packet_0xB192(packet_text, config2['0xB192  LTE ML1 Neighbor Cell Meas Request/Response'], entry).extract_info()
            elif packet_name == '0x17F2':
                print('0x17F2')
                return Packet_0x17F2.extract_info(packet_text, config2['0x17F2  IMS Voice Call Statistics'], entry)
            elif packet_name == '0x1D4D':
                print('0x1D4D')
                return Packet_0x1D4D.extract_info(packet_text, config2['0x1D4D  IMS CALL SUMMARY STATS'], entry)
            elif packet_name == '0xB16F':
                print('0xB16F')
                return Packet_0xB16F(packet_text, config2['0xB16F  LTE PUCCH Power Control'], entry).extract_info()
            elif packet_name == '0xB0E3':
                print('0xB0E3')
                return Packet_0xB0E3.extract_info(packet_text, config2['0xB0E3  LTE NAS ESM Plain OTA Outgoing Message'], entry)
            elif packet_name == '0xB0E2':
                print('0xB0E2')
                return Packet_0xB0E2.extract_info(packet_text, config2['0xB0E2  LTE NAS ESM Plain OTA Incoming Message'], entry)
            elif packet_name == '0xB808':
                print('0xB808')
                return Packet_0xB808.extract_info(packet_text, config2['0xB808'], entry)
            elif packet_name == '0xB809':
                print('0xB809')
                return Packet_0xB809.extract_info(packet_text, config2['0xB809'], entry)
            elif packet_name == '0xB16E':
                print('0xB16E')
                return Packet_0xB16E(packet_text, config2['0xB16E  LTE PUSCH Power Control'], entry).extract_info()
            elif packet_name == '0xB139':
                print('0xB139')
                return Packet_0xB139(packet_text, config2['0xB139  LTE LL1 PUSCH Tx Report'], entry).extract_info()
            elif packet_name == '0xB060':
                print('0xB060')
                return Packet_0xB060(packet_text, config2['0xB060  LTE MAC Configuration'], entry).extract_info()
            elif packet_name == '0xB0EE':
                print('0xB0EE')
                return Packet_0xB0EE.extract_info(packet_text, config3['0xB0EE  LTE NAS EMM State'], entry)
            elif packet_name == '0xB14D':
                print('0xB14D')
                return Packet_0xB14D.extract_info(packet_text, config3['0xB14D  LTE LL1 PUCCH CSF'], entry)
            elif packet_name == '0xB132':
                print('0xB132')
                return Packet_0xB132(packet_text, config3['0xB132  LTE LL1 PDSCH Decoding Results'], entry).extract_info()
            elif packet_name == '0xB130':
                print('0xB130')
                return Packet_0xB130(packet_text, config3['0xB130  LTE LL1 PDCCH Decoding Result'], entry).extract_info()
            elif packet_name == '0xB126':
                print('0xB126')
                return Packet_0xB126(packet_text, config3['0xB126  LTE LL1 PDSCH Demapper Configuration'], entry).extract_info()
            elif packet_name == '0xB16B':
                print('0xB16B')
                return Packet_0xB16B(packet_text, config3['0xB16B  LTE PDCCH-PHICH Indication Report'], entry).extract_info()
            elif packet_name == '0xB063':
                print('0xB063')
                return Packet_0xB063(packet_text, config3['0xB063  LTE MAC DL Transport Block'], entry).extract_info()
            elif packet_name == '0xB0A5':
                print('0xB0A5')
                return Packet_0xB0A5(packet_text, config3['0xB0A5  LTE PDCP DL SRB Integrity Data PDU'], entry).extract_info()
            elif packet_name == '0xB0A1':
                print('0xB0A1')
                return Packet_0xB0A1(packet_text, config3['0xB0A1  LTE PDCP DL Data PDU'], entry).extract_info()
            elif packet_name == '0xB06E':
                print('0xB06E')
                return Packet_0xB06E(packet_text, config3['0xB06E  LTE MAC DL RAR Transport Block'], entry).extract_info()
            elif packet_name == '0xB062':
                print('0xB062')
                return Packet_0xB062.extract_info(packet_text, config3['0xB062  LTE MAC Rach Attempt'], entry)
            elif packet_name == '0xB1DA':
                print('0xB1DA')
                return Packet_0xB1DA(packet_text, config3['0xB1DA  LTE ML1 Antenna Switch Diversity'], entry).extract_info()
            elif packet_name == '0xB081':
                print('0xB081')
                return Packet_0xB081(packet_text, config3['0xB081  LTE RLC DL Config Log packet'], entry).extract_info()
            elif packet_name == '0xB13C':
                print('0xB13C')
                return Packet_0xB13C(packet_text, config3['0xB13C  LTE LL1 PUCCH Tx Report'], entry).extract_info()
            elif packet_name == '0xB16C':
                print('0xB16C')
                return Packet_0xB16C(packet_text, config3['0xB16C  LTE DCI Information Report'], entry).extract_info()
            elif packet_name == '0xB064':
                print('0xB064')
                return Packet_0xB064(packet_text, config3['0xB064  LTE MAC UL Transport Block'], entry).extract_info()
            elif packet_name == '0xB0EF':
                print('0xB0EF')
                return Packet_0xB0EF.extract_info(packet_text, config3['0xB0EF  LTE NAS EMM USIM card mode'], entry)
            elif packet_name == '0xB0B5':
                print('0xB0B5')
                return Packet_0xB0B5(packet_text, config3['0xB0B5  LTE PDCP UL SRB Integrity Data PDU'], entry).extract_info()
            elif packet_name == '0xB0B4':
                print('0xB0B4')
                return Packet_0xB0B4(packet_text, config3['0xB0B4  LTE PDCP UL Statistics Pkt'], entry).extract_info()
            elif packet_name == '0xB0B1':
                print('0xB0B1')
                return Packet_0xB0B1(packet_text, config3['0xB0B1  LTE PDCP UL Data PDU'], entry).extract_info()
            elif packet_name == '0x1568':
                print('0x1568')
                return Packet_0x1568.extract_info(packet_text, config3['0x1568  IMS RTP SN and Payload'], entry)
            elif packet_name == '0xB061':
                print('0xB061')
                return Packet_0xB061.extract_info(packet_text, config3['0xB061  LTE MAC Rach Trigger'], entry)
        # start here

        # remove empty (only whitespace) lines

        # parse payload
        # skip first line, because first line content is main content
        # (packet type, length, etc), and is already parsed
        # entry = {"Time": self.datetime, "Source": "QxDM", "Subtitle": self.subtitle}
        packet_name = None
        # if self.subtitle:

        if self.subtitle == "" or self.subtitle == " ":
            packet_name = self.packet_type_hex + ' '+ self.name
        else:
            packet_name = self.packet_type_hex + ' '+ self.name + ' -- ' + self.subtitle

        entry = {"Time": self.datetime, "Source": "QxDM", "Packet Name": packet_name}

        data = _PARSE(self.packet_type_hex, self.packet_text, entry)
        print(data)
        return data


class Message:
    def __init__(self, description: str, packet_type: str, subtitle: str,
                 fields: List[Field], must_match_field: bool, saved_values: dict):
        '''
        must_match_field: boolean used to indicate that a message MUST contain
            the first field, otherwise, message should not be added. Used to
            handle cases like 'LTE NAS EMM State' message which should have
            specific field and value: 'EMM state = EMM_REGISTERED_INITIATED'
        '''
        self.description = description
        self.packet_type = packet_type
        self.subtitle = subtitle
        self.fields = fields
        self.must_match_field = must_match_field
        self.saved_values = saved_values

    def is_same_message_type(self, subtitle: str, packet_type: str,
                             packet_text: str) -> bool:
        if self.packet_type == packet_type and self.must_match_field:
            for line in packet_text.split('\r\n'):
                if self.fields[0].field_name == line:
                    return True
            return False
        else:
            return self.subtitle and subtitle == self.subtitle

    def get_contents(self, name: str, datetime: str,
                     packet_text: str) -> RawMessage:
        return RawMessage(name, self.subtitle, datetime, packet_text)

    def parse(self, name: str, datetime: str,
              packet_text: str) -> ParsedMessage:
        '''parses the message and returns a ParsedMessage'''
        parsed_message = ParsedMessage(self.description, name, self.subtitle,
                                       datetime, self.saved_values)

        # for each field of message, apply regex or normal search
        for field in self.fields:
            parsed_field = None
            if field.regex:
                match = re.findall(field.regex, packet_text)
                if not match:
                    parsed_field = ParsedField(field, None, found=False)
                elif field.field_type == FieldType.COLLECTION:
                    # split by '\r\n' and remove whitespace from start and end
                    vals = [v.strip() for v in match[0].split('\r\n')]
                    # remove empty strings
                    vals = [v for v in vals if v != '']
                    # remove ',' at end
                    vals = [v if v[-1] != ',' else v[:-1] for v in vals]
                    # perform additional parsing using search_2
                    if field.search_2:
                        vals = [v.strip() for v in vals if field.search_2 in v]
                    parsed_field = ParsedField(field, vals)
                else:
                    if type(match[0]) == str:
                        val = match[0].strip()
                        parsed_field = ParsedField(field, val)
                    else:  # match[0] contains a tuple of strings
                        vals = [v.strip() for v in match[0]]
                        vals = [v for v in vals if v != '']
                        parsed_field = ParsedField(field, vals)
            else:
                for line in packet_text.split('\r\n'):
                    # case-insensitive search for non-regex
                    if field.field_name.lower() in line.lower():
                        val = line.strip()
                        val = val if val[-1] != ',' else val[:-1]
                        parsed_field = ParsedField(field, val)
                        break
                else:
                    parsed_field = ParsedField(field, None, found=False)

            parsed_message.add_parsed_field(parsed_field)

        return parsed_message


# MANUAL PARSING TEST
def test_parsing():
    def parse_config(config_file):
        print('look hereeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee')
        print(config_file)
        packet_config = {}
        with open(config_file, 'r') as f:
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
                    # self.packet_frequency[val["packet_type"]]=60000/value['__event_frequency']
                    val['packet_frequency'] = 60000 / value['__event_frequency']
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
                packet_config[key] = val
        return packet_config

    def test_table_parsing():
        messages: List[ParsedRawMessage] = []
        msg = ParsedRawMessage(index=0, packet_type="0xB063", packet_length=100,
                               name="LTE MAC DL Transport Block",
                               subtitle="", datetime="2024 Jan 15  07:15:51.030",
                               packet_text=
                               """2024 Jan 15  07:15:51.030  [03]  0xB063  LTE MAC DL Transport Block
Subscription ID = 1
Version = 50
TB Log Buff
   Config Info
      Num Tb = 1
      Reason = 0
   TB Info[0]
      TB Common Info[0]
         -----------------------------------------------------------------------------------------
         |   |           |           |     |        |       |               |  |    |Num|        |
         |   |           |Num Pad    |     |        |Reparse|               |CC|HARQ|MAC|MAC Hdr |
         |#  |TB Size    |Bytes      |Frame|SubFrame|Flag   |RNTI Type      |ID|ID  |Sdu|Len     |
         -----------------------------------------------------------------------------------------
         |  0|         18|         13|  638|       0|      1|         C_RNTI| 0|   2|  1|       3|

      MAC Sdu Info[0]
         MAC Sdu Info Table[0]
            --------------------------------------------------------------------------------------------------------------
            |   |                                  |SDU CE Info                                          |               |
            |   |                                  |RLC PDCP Info                                |       |               |
            |   |MAC Common Info                   |       |  | |  | |  |   |       |Num |       |       |Dynamic Log    |
            |   |Is |                      |       |       |  | |  | |  |   |       |PDCP|Num    |Mac CE |Info           |
            |#  |MCE|LCID                  |Sdu Len|SN     |DC|P|RF|E|FI|LSF|SO     |Grp |NLOs   |Payload|Li Num|Li Len  |
            --------------------------------------------------------------------------------------------------------------
            |  0|  0|                     2|      2|      0| 0|0| 0|0| 0|  0|      0|   0|      0|       |      |        |


""")
        messages.append(msg)
        msg = ParsedRawMessage(index=0, packet_type="0xB16B", packet_length=100,
                               name="LTE PDCCH-PHICH Indication Report",
                               subtitle="", datetime="2024 Jan 15  07:15:35.491",
                               packet_text=
                               """2024 Jan 15  07:15:35.491  [C2]  0xB16B  LTE PDCCH-PHICH Indication Report
Subscription ID = 1
Version = 49
Duplex Mode = FDD
Number of Records = 25
Info Records
   --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
   |   |       |       |      |      |Force|PHICH                    |PDCCH Info                                                                                                    |        |            |
   |   |Num    |Num    |PDCCH |PDCCH |Send |     |       |     |PHICH|Serv |              |PDCCH  |           |      |          |     |      |       |      |     |     |     |     |Dl      |            |
   |   |PDCCH  |PHICH  |Timing|Timing|PDCCH|Cell |PHICH  |PHICH|1    |Cell |              |Payload|Aggregation|Search|SPS Grant |New  |Num DL|Is Ul  |Interf|S0   |S1   |S2   |S3   |Subframe|Full Mode   |
   |#  |Results|Results|SFN   |Sub-fn|Ind  |Index|Present|Value|Value|Index|RNTI Type     |Size   |Level      |Space |Type      |DL Tx|Trblks|Dropped|Active|Index|Index|Index|Index|Count   |Events Mask |
   --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
   |  0|      1|      1|   107|     0|    0|    0|    Yes|  ACK|     |    0|        C_RNTI|     43|       Agg2|    UE|          |    0|     0|      0|     0|    0|    0|    0|    0|  373936|      0x0000|
   |  1|      0|      1|   107|     1|    0|    0|    Yes|  ACK|     |     |              |       |           |      |          |     |      |       |      |     |     |     |     |  373937|      0x0000|
   |  2|      1|      1|   107|     2|    0|    0|    Yes|  ACK|     |    0|        C_RNTI|     43|       Agg2|    UE|          |    0|     0|      0|     0|    0|    0|    0|    0|  373938|      0x0000|
   |  3|      1|      1|   107|     3|    0|    0|    Yes|  ACK|     |    0|        C_RNTI|     43|       Agg2|    UE|          |    0|     0|      0|     0|    0|    0|    0|    0|  373939|      0x0000|
   |  4|      1|      1|   107|     4|    0|    0|    Yes|  ACK|     |    0|        C_RNTI|     43|       Agg2|    UE|          |    0|     0|      0|     0|    0|    0|    0|    0|  373940|      0x0000|
   |  5|      1|      0|   107|     5|    0|     |       |     |     |    0|        C_RNTI|     43|       Agg2|    UE|          |    0|     0|      0|     0|    0|    0|    0|    0|  373941|      0x0000|
   |  6|      1|      1|   107|     6|    0|    0|    Yes|  ACK|     |    0|        C_RNTI|     43|       Agg2|    UE|          |    0|     0|      0|     0|    0|    0|    0|    0|  373942|      0x0000|
   |  7|      1|      1|   107|     7|    0|    0|    Yes|  ACK|     |    0|        C_RNTI|     43|       Agg2|    UE|          |    0|     0|      0|     0|    0|    0|    0|    0|  373943|      0x0000|
   |  8|      0|      1|   107|     8|    0|    0|    Yes|  ACK|     |     |              |       |           |      |          |     |      |       |      |     |     |     |     |  373944|      0x0000|
   |  9|      1|      0|   107|     9|    0|     |       |     |     |    0|        C_RNTI|     43|       Agg2|    UE|          |    0|     0|      0|     0|    0|    0|    0|    0|  373945|      0x0000|
   | 10|      1|      1|   108|     0|    0|    0|    Yes|  ACK|     |    0|        C_RNTI|     43|       Agg1|    UE|          |    0|     0|      0|     0|    0|    0|    0|    0|  373946|      0x0000|
   | 11|      1|      1|   108|     1|    0|    0|    Yes|  ACK|     |    0|        C_RNTI|     43|       Agg2|    UE|          |    0|     0|      0|     0|    0|    0|    0|    0|  373947|      0x0000|
   | 12|      0|      1|   108|     2|    0|    0|    Yes|  NAK|     |     |              |       |           |      |          |     |      |       |      |     |     |     |     |  373948|      0x0000|
   | 13|      1|      1|   108|     3|    0|    0|    Yes|  ACK|     |    0|        C_RNTI|     43|       Agg2|    UE|          |    0|     0|      0|     0|    0|    0|    0|    0|  373949|      0x0000|
   | 14|      1|      1|   108|     4|    0|    0|    Yes|  ACK|     |    0|        C_RNTI|     43|       Agg2|    UE|          |    0|     0|      0|     0|    0|    0|    0|    0|  373950|      0x0000|
   | 15|      0|      1|   108|     5|    0|    0|    Yes|  ACK|     |     |              |       |           |      |          |     |      |       |      |     |     |     |     |  373951|      0x0000|
   | 16|      1|      0|   108|     6|    0|     |       |     |     |    0|        C_RNTI|     43|       Agg2|    UE|          |    0|     0|      0|     0|    0|    0|    0|    0|  373952|      0x0000|
   | 17|      0|      1|   108|     7|    0|    0|    Yes|  ACK|     |     |              |       |           |      |          |     |      |       |      |     |     |     |     |  373953|      0x0000|
   | 18|      1|      1|   108|     8|    0|    0|    Yes|  ACK|     |    0|        C_RNTI|     43|       Agg2|    UE|          |    0|     0|      0|     0|    0|    0|    0|    0|  373954|      0x0000|
   | 19|      1|      1|   108|     9|    0|    0|    Yes|  ACK|     |    0|        C_RNTI|     43|       Agg2|    UE|          |    0|     0|      0|     0|    0|    0|    0|    0|  373955|      0x0000|
   | 20|      1|      1|   109|     0|    0|    0|    Yes|  ACK|     |    0|        C_RNTI|     43|       Agg2|    UE|          |    0|     0|      0|     0|    0|    0|    0|    0|  373956|      0x0000|
   | 21|      1|      1|   109|     1|    0|    0|    Yes|  ACK|     |    0|        C_RNTI|     43|       Agg2|    UE|          |    0|     0|      0|     0|    0|    0|    0|    0|  373957|      0x0000|
   | 22|      1|      1|   109|     2|    0|    0|    Yes|  ACK|     |    0|        C_RNTI|     43|       Agg2|    UE|          |    0|     0|      0|     0|    0|    0|    0|    0|  373958|      0x0000|
   | 23|      1|      0|   109|     3|    0|     |       |     |     |    0|        C_RNTI|     43|       Agg2|    UE|          |    0|     0|      0|     0|    0|    0|    0|    0|  373959|      0x0000|
   | 24|      0|      1|   109|     4|    0|    0|    Yes|  ACK|     |     |              |       |           |      |          |     |      |       |      |     |     |     |     |  373960|      0x0000|


""")
        messages.append(msg)
        msg = ParsedRawMessage(index=0, packet_type="0xB126", packet_length=100,
                               name="LTE LL1 PDSCH Demapper Configuration",
                               subtitle="", datetime="2024 Jan 15  07:15:36.201",
                               packet_text=
                               """2024 Jan 15  07:15:36.201  [1A]  0xB126  LTE LL1 PDSCH Demapper Configuration
Subscription ID = 1
Version = 163
Carrier Index = PCC
Num of Records = 20
Records
   ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
   |   |Sub-frame |System Frame|                |Number of Tx|Number of Rx|Spatial|Frequency    |PMI  |                                |                    |                    |                  |                  |
   |#  |Number    |Number      |PDSCH RNTI Type |Antennas (M)|Antennas (N)|Rank   |Selective PMI|Index|Transmission Scheme             |RB Allocation Slot 0|RB Allocation Slot 1|UERS Port Enabled |QICE Skip Reason  |
   ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
   |  0|         0|         178|          C-RNTI|           4|           4|      1|     Wideband|    4|Closed-loop spatial multiplexing|  0x0000FC00001FFFF8|  0x0000FC00001FFFF8|          Reserved|        SW Disable|
   |   |          |            |                |            |            |       |             |     |                                |  0x0000000000000000|  0x0000000000000000|                  |                  |
   |  1|         2|         178|          C-RNTI|           4|           4|      1|     Wideband|    4|Closed-loop spatial multiplexing|  0x00001C00001FFFFF|  0x00001C00001FFFFF|          Reserved|        SW Disable|
   |   |          |            |                |            |            |       |             |     |                                |  0x0000000000000000|  0x0000000000000000|                  |                  |
   |  2|         3|         178|          C-RNTI|           4|           4|      1|     Wideband|    4|Closed-loop spatial multiplexing|  0x0003FFFFC7FFFFFF|  0x0003FFFFC7FFFFFF|          Reserved|        SW Disable|
   |   |          |            |                |            |            |       |             |     |                                |  0x0000000000000000|  0x0000000000000000|                  |                  |
   |  3|         4|         178|          C-RNTI|           4|           4|      1|     Wideband|    4|Closed-loop spatial multiplexing|  0x0003FFFFFFFFFFFF|  0x0003FFFFFFFFFFFF|          Reserved|        SW Disable|
   |   |          |            |                |            |            |       |             |     |                                |  0x0000000000000000|  0x0000000000000000|                  |                  |
   |  4|         5|         178|          C-RNTI|           4|           4|      1|     Wideband|    4|Closed-loop spatial multiplexing|  0x0003000038FFFFC0|  0x0003000038FFFFC0|          Reserved|        SW Disable|
   |   |          |            |                |            |            |       |             |     |                                |  0x0000000000000000|  0x0000000000000000|                  |                  |
   |  5|         8|         178|          C-RNTI|           4|           4|      1|     Wideband|    4|Closed-loop spatial multiplexing|  0x0003FFFFC7FFFFFF|  0x0003FFFFC7FFFFFF|          Reserved|        SW Disable|
   |   |          |            |                |            |            |       |             |     |                                |  0x0000000000000000|  0x0000000000000000|                  |                  |
   |  6|         9|         178|          C-RNTI|           4|           4|      1|     Wideband|    4|Closed-loop spatial multiplexing|  0x0003FFFFFFFFFFFF|  0x0003FFFFFFFFFFFF|          Reserved|        SW Disable|
   |   |          |            |                |            |            |       |             |     |                                |  0x0000000000000000|  0x0000000000000000|                  |                  |
   |  7|         0|         179|          C-RNTI|           4|           4|      1|     Wideband|    4|Closed-loop spatial multiplexing|  0x0003FFFFFFFFFFFF|  0x0003FFFFFFFFFFFF|          Reserved|        SW Disable|
   |   |          |            |                |            |            |       |             |     |                                |  0x0000000000000000|  0x0000000000000000|                  |                  |
   |  8|         1|         179|          C-RNTI|           4|           4|      1|     Wideband|    4|Closed-loop spatial multiplexing|  0x0003FFFFFFFFFFFF|  0x0003FFFFFFFFFFFF|          Reserved|        SW Disable|
   |   |          |            |                |            |            |       |             |     |                                |  0x0000000000000000|  0x0000000000000000|                  |                  |
   |  9|         2|         179|          C-RNTI|           4|           4|      1|     Wideband|    4|Closed-loop spatial multiplexing|  0x0003FFFFFFFFFFFF|  0x0003FFFFFFFFFFFF|          Reserved|        SW Disable|
   |   |          |            |                |            |            |       |             |     |                                |  0x0000000000000000|  0x0000000000000000|                  |                  |
   | 10|         3|         179|          C-RNTI|           4|           4|      1|     Wideband|    4|Closed-loop spatial multiplexing|  0x0003FFFFFFFFFFFF|  0x0003FFFFFFFFFFFF|          Reserved|        SW Disable|
   |   |          |            |                |            |            |       |             |     |                                |  0x0000000000000000|  0x0000000000000000|                  |                  |
   | 11|         4|         179|          C-RNTI|           4|           4|      1|     Wideband|    4|Closed-loop spatial multiplexing|  0x0003FFFFFFFFFFFF|  0x0003FFFFFFFFFFFF|          Reserved|        SW Disable|
   |   |          |            |                |            |            |       |             |     |                                |  0x0000000000000000|  0x0000000000000000|                  |                  |
   | 12|         5|         179|          C-RNTI|           4|           4|      1|     Wideband|    4|Closed-loop spatial multiplexing|  0x0003FFFFFFFFFFFF|  0x0003FFFFFFFFFFFF|          Reserved|        SW Disable|
   |   |          |            |                |            |            |       |             |     |                                |  0x0000000000000000|  0x0000000000000000|                  |                  |
   | 13|         7|         179|          C-RNTI|           4|           4|      1|     Wideband|    4|Closed-loop spatial multiplexing|  0x0003FFFFFFFFFFFF|  0x0003FFFFFFFFFFFF|          Reserved|        SW Disable|
   |   |          |            |                |            |            |       |             |     |                                |  0x0000000000000000|  0x0000000000000000|                  |                  |
   | 14|         8|         179|          C-RNTI|           4|           4|      1|     Wideband|    4|Closed-loop spatial multiplexing|  0x0003FFFFFFFFFFFF|  0x0003FFFFFFFFFFFF|          Reserved|        SW Disable|
   |   |          |            |                |            |            |       |             |     |                                |  0x0000000000000000|  0x0000000000000000|                  |                  |
   | 15|         9|         179|          C-RNTI|           4|           4|      1|     Wideband|    4|Closed-loop spatial multiplexing|  0x0003FFFFFFFFFFFF|  0x0003FFFFFFFFFFFF|          Reserved|        SW Disable|
   |   |          |            |                |            |            |       |             |     |                                |  0x0000000000000000|  0x0000000000000000|                  |                  |
   | 16|         0|         180|          C-RNTI|           4|           4|      1|     Wideband|    4|Closed-loop spatial multiplexing|  0x0003FFFFFFFFFFFF|  0x0003FFFFFFFFFFFF|          Reserved|        SW Disable|
   |   |          |            |                |            |            |       |             |     |                                |  0x0000000000000000|  0x0000000000000000|                  |                  |
   | 17|         2|         180|          C-RNTI|           4|           4|      1|     Wideband|    4|Closed-loop spatial multiplexing|  0x0003FFFFFFFFFFFF|  0x0003FFFFFFFFFFFF|          Reserved|        SW Disable|
   |   |          |            |                |            |            |       |             |     |                                |  0x0000000000000000|  0x0000000000000000|                  |                  |
   | 18|         3|         180|          C-RNTI|           4|           4|      1|     Wideband|    4|Closed-loop spatial multiplexing|  0x0003FFFFFFFFFFFF|  0x0003FFFFFFFFFFFF|          Reserved|        SW Disable|
   |   |          |            |                |            |            |       |             |     |                                |  0x0000000000000000|  0x0000000000000000|                  |                  |
   | 19|         4|         180|          C-RNTI|           4|           4|      1|     Wideband|    4|Closed-loop spatial multiplexing|  0x0003FFFFFFFFFFFF|  0x0003FFFFFFFFFFFF|          Reserved|        SW Disable|
   |   |          |            |                |            |            |       |             |     |                                |  0x0000000000000000|  0x0000000000000000|                  |                  |

""")
        messages.append(msg)
        msg = ParsedRawMessage(index=0, packet_type="0xB130", packet_length=100,
                               name="LTE LL1 PDCCH Decoding Result",
                               subtitle="", datetime="2024 Jan 15  07:15:35.477",
                               packet_text=
                               """2024 Jan 15  07:15:35.477  [89]  0xB130  LTE LL1 PDCCH Decoding Result
Subscription ID = 1
Version = 163
Carrier Index = SCC
Number of Records = 11
Hypothesis
   -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
   |   |         |      |       |          |          |          |                    |        |        |   |   |                  |           |         |      |          |              |       |        |       |     |                                        |          |        |      |Non Zero|Non  |      |
   |   |         |System|       |          |Two bits  |Aperiodic |                    |        |        |   |CA |                  |           |         |Search|          |              |       |        |       |     |                                        |Norm      |Symbol  |      |Symbol  |Zero |      |
   |   |Sub-frame|Frame |Band   |CIF       |CSI       |SRS       |                    |Num eNB |        |   |FDD|                  |Aggregation|         |Space |          |              |Payload|Tail    |Alt TBS|Start|                                        |Energy    |Error   |Energy|Mismatch|Llr  |      |
   |#  |Number   |Number|Width  |Configured|Configured|configured|Frame Structure     |Antennas|DL CP   |SSC|TDD|Payload           |Level      |Candidate|Type  |DCI Format|Decode Status |Size   |Match   |Enabled|CCE  |Prune Status                            |Metric    |Rate    |Metric|Count   |Count|Normal|
   -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
   |  0|        0|   107| 10 MHz|     false|     false|     false|                 FDD|       4|  NORMAL|  0|  0|0x260C080000000000|       Agg2|        0|  User|         0|        C_RNTI|     43|   Match|      0|   18|                            SUCCESS_DCI0|    0.9810|0.015503|  3412|       2|  129|  3478|
   |  1|        2|   107| 10 MHz|     false|     false|     false|                 FDD|       4|  NORMAL|  0|  0|0x260BC88000000000|       Agg2|        3|  User|         0|        C_RNTI|     43|   Match|      0|    6|                            SUCCESS_DCI0|    0.9922|0.007751|  3586|       1|  129|  3614|
   |  2|        3|   107| 10 MHz|     false|     false|     false|                 FDD|       4|  NORMAL|  0|  0|0x1E5B690000000000|       Agg2|        5|  User|         0|        C_RNTI|     43|   Match|      0|   14|                            SUCCESS_DCI0|    1.0000|0.000000|  3620|       0|  129|  3620|
   |  3|        4|   107| 10 MHz|     false|     false|     false|                 FDD|       4|  NORMAL|  0|  0|0x260B880000000000|       Agg1|        4|  User|         0|        C_RNTI|     43|   Match|      0|   10|                    FAIL_SURVIVOR_SELECT|    0.9961|0.013885|  1738|       1|   72|  1744|
   |  4|        4|   107| 10 MHz|     false|     false|     false|                 FDD|       4|  NORMAL|  0|  0|0x260B880000000000|       Agg2|        3|  User|         0|        C_RNTI|     43|   Match|      0|   10|                            SUCCESS_DCI0|    0.9980|0.007751|  3341|       1|  129|  3347|
   |  5|        5|   107| 10 MHz|     false|     false|     false|                 FDD|       4|  NORMAL|  0|  0|0x1E3FA88000000000|       Agg2|        3|  User|         0|        C_RNTI|     43|   Match|      0|   18|                            SUCCESS_DCI0|    0.9785|0.015503|  3427|       2|  129|  3501|
   |  6|        6|   107| 10 MHz|     false|     false|     false|                 FDD|       4|  NORMAL|  0|  0|0x260B880000000000|       Agg4|        3|Common|         0|        C_RNTI|     43|   Match|      0|   12|                    FAIL_SURVIVOR_SELECT|    1.0000|0.000000|  3461|       0|  129|  3461|
   |  7|        6|   107| 10 MHz|     false|     false|     false|                 FDD|       4|  NORMAL|  0|  0|0x260B880000000000|       Agg2|        5|  User|         0|        C_RNTI|     43|   Match|      0|   12|                            SUCCESS_DCI0|    1.0000|0.000000|  3818|       0|  129|  3818|
   |  8|        7|   107| 10 MHz|     false|     false|     false|                 FDD|       4|  NORMAL|  0|  0|0x1B1BE80000000000|       Agg2|        0|  User|         0|        C_RNTI|     43|   Match|      0|   14|                            SUCCESS_DCI0|    0.9575|0.023438|  3398|       3|  128|  3548|
   |  9|        9|   107| 10 MHz|     false|     false|     false|                 FDD|       4|  NORMAL|  0|  0|0x1E3BA88000000000|       Agg1|        0|  User|         0|        C_RNTI|     43|   Match|      0|    8|                    FAIL_SURVIVOR_SELECT|    0.9136|0.055541|  1777|       4|   72|  1945|
   | 10|        9|   107| 10 MHz|     false|     false|     false|                 FDD|       4|  NORMAL|  0|  0|0x1E3BA88000000000|       Agg2|        1|  User|         0|        C_RNTI|     43|   Match|      0|    8|                            SUCCESS_DCI0|    0.9321|0.054260|  3263|       7|  129|  3499|


""")
        messages.append(msg)
        msg = ParsedRawMessage(index=0, packet_type="0xB132", packet_length=100,
                               name="LTE LL1 PDSCH Decoding Results",
                               subtitle="", datetime="2024 Jan 15  07:16:08.265",
                               packet_text=
                               """2024 Jan 15  07:16:08.265  [31]  0xB132  LTE LL1 PDSCH Decoding Results
Subscription ID = 1
Version = 168
Length = 160
Drop Cnt = 0
Num Records = 1
Common Static Config
   Context = LTE
   Variant Id = 0
   CxN Index = 0
   Cell Id = 147
   EARFCN = 5780
   Carrier Index = 0
   Variant Carrier Index = 0
   System BW = 10
   NIR = 114192
   Num HARQ = 8
   UE Category = 20
   TX Mode = TM4_CL_SM
   Num eNb Tx Ant = 4
   Four_Layer_Capability = false
TB Info Record[0]
   TB Top
      -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
      |     |     |     |    |       |      |    |    |     |    |      |         |        |         |           |         |    |    |     |    |Harq|     |   |   |     |      |      |      |
      |     |     |MVC  |    |       |      |    |    |     |    |      |         |        |         |           |         |    |IO  |     |Harq|IO  |Num  |   |   |     |      |      |      |
      |     |     |Clock|    |       |Bypass|    |Num |Start|QREN|RX01  |CB Bundle|TB DMA  |         |           |         |IO  |ST  |Num  |IO  |ST  |Harq |RP |SF |RB   |SC    |TB Ext|CB    |
      |Frame|SubFN|(MHz)|Rank|LLR BW |Decode|ITER|RX  |CB ID|BMSK|poolID|Size     |Budget  |Onld Size|Offld Size |L2 Mode  |Fail|Fail|IOVec|Fail|Fail|Iovec|Idx|Gap|Start|Index |Enable|Enable|
      -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
      |  312|    4|  192|  R1|     6B|     0|   1| 2RX|    0|   2|     1|        1|    3778|        0|        408|   HEADER|   0|   0|    1|   0|   0|    1|  0|  0|    0|     0|  TRUE|  TRUE|

   TB Config
      ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
      |          |    |      |     |      |   |      |        |     |    |        |               |         |      |Num     |  |      |        |        |Force  |      |Alt|Hi  |    |Excess  |      |Max|        |     |    |
      |          |HARQ|TB    |CW   |      |Num|      |        |     |Num |NCB     |               |         |      |Channel |  |CB    |        |DMA TO  |HARQ   |Bypass|MCS|MGMT|Max |HI Init |Hi    |HI |TX      |NDI  |Code|
      |RNTI      |ID  |Index |Index|Num CB|Lay|MCS   |MOD     |ReTx |ReTx|Prime   |Discard Mode   |QED Mode |Num RB|Bits    |RV|Size  |TB Size |Dur     |Offload|HARQ  |En |En  |Iter|State   |Base  |Low|Scheme  |Value|Rate|
      ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
      |         C|   3|     0|    0|     1| 1L|    27|   64QAM|  1st|   0|   17292|     NO_DISCARD|   NO_QED|     9|    7344| 0|   720|     717|2.1e+002|  FALSE| FALSE|  0|   0|17HI|       0|     0|  0|   CL_SP|    1|0.784|

   TB
      ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
      |TB Onload                                                        |TB Offload                                                       |                                                              |
      |Excess    |          |            |                              |Excess    |          |            |                              |TB Decode                                                     |
      |Time      |TB Pass HD|TB Pass HARQ|CB Timeout Status             |Time      |TB Pass HD|TB Pass HARQ|CB Timeout Status             |CB CRC Pass Bmsk         |Excess HI State |TB CRC     |TB Pass|
      ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
      |        50|      0xFF|        0xFF|            0x0000000000000000|        50|      0xFF|        0xFF|            0x0000000000000000|       0x0000000000000001|               0|   0x000000|      1|

   TB Log Extend
      -------------------------------------------------------------------------------------------------------------------------------------------------------------
      |TB Ext 0   |TB Ext 1   |TB Ext 2   |TB Ext 3   |TB Ext 4   |TB Ext 5   |TB Ext 6   |TB Ext 7   |TB Ext 8   |TB Ext 9   |TB Ext 10  |TB Ext 11  |TB Ext 12  |
      -------------------------------------------------------------------------------------------------------------------------------------------------------------
      | 0x02D10F83| 0x004004C8| 0x840804C8| 0xB676D400| 0x40600F00| 0x00000000| 0x00000000| 0x00000000| 0x00000000| 0x702D0201| 0x07C2E004| 0x00034898| 0x00000000|

   CB
      --------------------------------------------------------------------------------------------------------------------------------------------------------------
      |   |                                      |                                          |CB Decode                                                             |
      |   |CB Onload                             |CB Offload                                |             |  |       |   |      |  |    |       |       |Skip  |DHB|
      |#  |On Dur|On Extract|On Time Remain|ON TO|Off Dur|Off Extract|Off Time Remain|Off TO|Energy Metric|ET|Min LLR|CRC|Num HI|HD|HARQ|CB Disc|CB Pass|Decode|IDX|
      --------------------------------------------------------------------------------------------------------------------------------------------------------------
      |  0|     0|         0|            50|    0|      1|          0|             50|     0|       152567| 1|     36|  1|   3HI| 1|   0|      0|      1|     0|  0|
""")
        messages.append(msg)
        msg = ParsedRawMessage(index=0, packet_type="0xB0EE", packet_length=100,
                               name="LTE NAS EMM State",
                               subtitle="", datetime="2024 Jan 15  07:18:07.713",
                               packet_text=
                               """2024 Jan 15  07:18:07.713  [18]  0xB0EE  LTE NAS EMM State
Subscription ID = 1
Version = 2
EMM state = EMM_DEREGISTERED
EMM sub-state = EMM_DEREGISTERED_NO_CELL_AVAILABLE
PLMN_ID:
   MCC digit 1 = 3
   MCC digit 2 = 1
   MCC digit 3 = 3
   MNC digit 3 = 0
   MNC digit 1 = 3
   MNC digit 2 = 4
Guti valid = False
""")
        messages.append(msg)
        msg = ParsedRawMessage(index=0, packet_type="0xB14D", packet_length=100,
                               name="LTE LL1 PUCCH CSF",
                               subtitle="", datetime="2024 Jan 15  07:15:35.518",
                               packet_text=
                               """2024 Jan 15  07:15:35.518  [26]  0xB14D  LTE LL1 PUCCH CSF
Subscription ID = 1
Version = 163
Start System Sub-frame Number = 0
Start System Frame Number = 112
Carrier Index = PCC
Scell Index = 0
PUCCH Reporting Mode = MODE_1_1
PUCCH Report Type = Type 3, RI
Number of SubBands = 9
CSF Tx Mode = TM_CL_SM
Alt Cqi Table = 1
Num Csirs Ports = 0
Csi Meas Set Index = CSI0
Rank Index = Rank 2
CRI = 0
UL Frame Number = 112
UL Channel Type = 0
UL Subframe Number = 4
UL Payload Length = 0
W1 I11 FDMIMO = 0
W1 I12 FDMIMO = 0
""")
        messages.append(msg)
        msg = ParsedRawMessage(index=0, packet_type="0xB809", packet_length=100,
                               name="NR5G NAS MM5G Security Protected OTA Outgoing Msg",
                               subtitle="", datetime="2024 Jan 15  07:17:09.244",
                               packet_text=
                               """2024 Jan 15  07:17:09.244  [A9]  0xB809  NR5G NAS MM5G Security Protected OTA Outgoing Msg
Subscription ID = 1
Misc ID         = 0
Version = 1
Std Version = 15
Std Major Version = 4
Std Minor Version = 0
Outgoing OTA Raw Data = { 
   126, 4, 94, 156, 187, 109, 0, 241, 
   205, 9, 232, 63, 245, 122, 13, 31, 
   91, 80, 114, 108, 105, 33, 175, 214, 
   143, 44, 136, 120, 50, 135, 168, 52, 
   206, 236, 162, 153, 79, 147, 221, 67, 
   165, 72, 35, 24, 177, 121, 33, 8, 
   131, 20, 92, 248, 195, 157, 250, 29, 
   105, 13, 204, 103, 97, 131, 61, 37, 
   21, 106, 115, 114, 152, 246, 70, 8, 
   106, 242, 14, 9, 241, 144, 57, 1, 
   211, 233, 114, 140, 68, 112, 42, 189, 
   11, 1, 2, 195, 95, 20, 129, 0, 
   225, 31, 82, 120, 72, 172, 247, 28, 
   239, 41, 5, 9, 39, 180, 57, 19, 
   180, 0, 197, 49, 214, 31, 106, 13, 
   123
}
""")
        messages.append(msg)
        msg = ParsedRawMessage(index=0, packet_type="0xB808", packet_length=100,
                               name="NR5G NAS MM5G Security Protected OTA Incoming Msg",
                               subtitle="", datetime="2024 Jan 15  07:17:09.243",
                               packet_text=
                               """2024 Jan 15  07:17:09.243  [3D]  0xB808  NR5G NAS MM5G Security Protected OTA Incoming Msg
Subscription ID = 1
Misc ID         = 0
Version = 1
Std Version = 15
Std Major Version = 4
Std Minor Version = 0
Incoming OTA Raw Data = { 
   126, 3, 97, 165, 249, 151, 0, 126, 
   0, 93, 51, 9, 4, 240, 112, 240, 
   112, 225, 87, 34, 54, 1, 2, 25, 
   4, 240, 112, 192, 64
}
""")
        messages.append(msg)
        msg = ParsedRawMessage(index=0, packet_type="0xB0E2", packet_length=100,
                               name="LTE NAS ESM Plain OTA Incoming Message",
                               subtitle="ESM information request Msg", datetime="2024 Jan 15  07:16:06.121", packet_text=
                               """2024 Jan 15  07:16:06.121  [62]  0xB0E2  LTE NAS ESM Plain OTA Incoming Message  --  ESM information request Msg
Subscription ID = 1
pkt_version = 1 (0x1)
rel_number = 9 (0x9)
rel_version_major = 5 (0x5)
rel_version_minor = 0 (0x0)
eps_bearer_id_or_skip_id = 0 (0x0)
prot_disc = 2 (0x2) (EPS session management messages)
trans_id = 9 (0x9)
msg_type = 217 (0xd9) (ESM information request)
lte_esm_msg
""")
        messages.append(msg)
        msg = ParsedRawMessage(index=0, packet_type="0xB192", packet_length=100,
                               name="LTE ML1 Neighbor Cell Meas Request/Response",
                               subtitle="", datetime="2024 Jan 15  07:17:28.048", packet_text=
                               """2024 Jan 15  07:17:28.048  [C6]  0xB192  LTE ML1 Neighbor Cell Meas Request/Response
Subscription ID = 1
Version = 1
Number of SubPackets = 2
SubPacket ID = 26
Idle Mode Neighbor Cell Measurement Request
   Version = 2
   SubPacket Size = 28 bytes
   E-ARFCN = 700
   Num Cells = 1
   Num Rx Ant = 2
   Dupexing Mode = FDD
   Neighbor Cells
      ------------------------------------------------
      |   |    |              |Enabled |      |      |
      |   |Cell|              |Tx      |TTL   |FTL   |
      |#  |ID  |CP Type       |Antennas|Enable|Enable|
      ------------------------------------------------
      |  0| 459|        Normal|       2| false| false|

SubPacket ID = 27
Neighbor Cell Meas Result
   Version = 56
   SubPacket Size = 64 bytes
   E-ARFCN = 700
   Num Cells = 1
   Duplexing Mode = FDD
   Serving Cell Index = PCell
   Neighbor Cells
      ------------------------------------------------------------------------------------------------------------
      |   |        |           |        |Inst   |Inst   |Inst    |Inst   |Inst   |       |Inst   |Inst   |       |
      |   |        |FTL        |        |RSRP   |RSRP   |Measured|RSRQ   |RSRQ   |Inst   |RSSI   |RSSI   |Inst   |
      |   |Physical|Cumulative |        |Rx[0]  |Rx[1]  |RSRP    |Rx[0]  |Rx[1]  |RSRQ   |Rx[0]  |Rx[1]  |RSSI   |
      |#  |Cell ID |Freq Offset|Bad CER |(dBm)  |(dBm)  |(dBm)   |(dBm)  |(dBm)  |(dBm)  |(dBm)  |(dBm)  |(dBm)  |
      ------------------------------------------------------------------------------------------------------------
      |  0|     459|          0|   FALSE|-103.63|-100.88| -100.88| -27.06| -25.81| -25.81| -67.56| -66.06| -66.06|
      |  0|     459|          0|    TRUE|-103.63|-100.88| -100.88| -27.06| -25.81| -25.81| -67.56| -66.06| -76.06|

""")
        messages.append(msg)
        msg = ParsedRawMessage(index=0, packet_type="0xB186", packet_length=100,
                               name="LTE ML1 Reselection Candidates",
                               subtitle="", datetime="2024 Jan 15  07:17:24.246", packet_text=
                               """2024 Jan 15  07:17:24.246  [64]  0xB186  LTE ML1 Reselection Candidates
Subscription ID = 1
Version = 41
Serving E-ARFCN = 5780
Serving Cell ID = 147
Num Reselection Candidates = 2
Candidates[0]
   Candidate Priority = 3.0
   RAT Type = EUTRAN
   LTE Candidate
      E-ARFCN = 700
      Cell ID = 147
Candidates[1]
   Candidate Priority = 3.0
   RAT Type = EUTRAN
   LTE Candidate
      E-ARFCN = 66986
      Cell ID = 147
}
""")
        messages.append(msg)
        msg = ParsedRawMessage(index=0, packet_type="0xB181", packet_length=100,
                               name="LTE ML1 Intra Frequency Cell Reselection",
                               subtitle="", datetime="2024 Jan 15  07:15:49.491", packet_text=
                               """2024 Jan 15  07:15:49.491  [E3]  0xB181  LTE ML1 Intra Frequency Cell Reselection
Subscription ID = 1
Version = 1
Number of SubPackets = 3
SubPacket ID = 10
Idle Mode Reselection Measurements Common
   Version = 56
   SubPacket Size = 12 bytes
   Serving Cell E-ARFCN = 66986
   Serving Cell Physical Cell ID = 147
   Current UE Mobility State = Normal Mobility
   Priority Categories Evaluated = NONE
SubPacket ID = 5
Idle Meas Serving Frequency Resel Info
   Version = 25
   SubPacket Size = 16 bytes
   Standards Version = Release 9
   Serving Cell Priority = 3
   S Non-Intra Search = 4
   Thresh Serving Low = 4
   S Non Intra Search Q = 0 dB
   Thres Serving Low Q = 0 dB
SubPacket ID = 11
Idle Mode Reselection Measurements LTE Frequency
   Version = 58
   SubPacket Size = 88 bytes
   Instance = 0
   Number of Layers = 5
   Treselection = 0 s
   Layer[0]
      E-ARFCN = 66986
      Treselection = 2 s
      Q Offset Frequency = 0 dB
      Number of Cells = 1
      Thresh X High = 0
      Thresh X Low = 4
      Priority = 3
      Neighbor Cells
         -----------------------------------------------------------------------------------------------------
         |   |        |      |RSSI   |      |RSRP   |RSRP   |RSRQ   |RSRQ   |            |        |          |
         |   |Physical|Srxlev|Inst   |Q     |Average|Inst   |Average|Inst   |            |Rank    |Rank      |
         |#  |ID      |(dB)  |(dBm)  |Offset|(dBm)  |(dBm)  |(dBm)  |(dBm)  |TReSelection|Interger|Fractional|
         -----------------------------------------------------------------------------------------------------
         |  0|     147|    37| -58.00|  0 dB| -88.75| -88.75| -13.25| -13.75|       65535|      79|     0.258|

   Layer[1]
      E-ARFCN = 9820
      Treselection = 2 s
      Q Offset Frequency = 0 dB
      Number of Cells = 0
      Thresh X High = 8
      Thresh X Low = 0
      Priority = 4
   Layer[2]
      E-ARFCN = 700
      Treselection = 2 s
      Q Offset Frequency = 0 dB
      Number of Cells = 0
      Thresh X High = 0
      Thresh X Low = 0
      Priority = 3
   Layer[3]
      E-ARFCN = 5780
      Treselection = 2 s
      Q Offset Frequency = 0 dB
      Number of Cells = 0
      Thresh X High = 0
      Thresh X Low = 0
      Priority = 2
   Layer[4]
      E-ARFCN = 5330
      Treselection = 2 s
      Q Offset Frequency = 0 dB
      Number of Cells = 0
      Thresh X High = 10
      Thresh X Low = 62
      Priority = 0
""")
        messages.append(msg)
        msg = ParsedRawMessage(index=0, packet_type="0xB17E", packet_length=100,
                               name="LTE ML1 UE Mobility State change",
                               subtitle="", datetime="2024 Jan 15  07:16:06.698", packet_text=
                               """2024 Jan 15  07:16:06.698  [53]  0xB17E  LTE ML1 UE Mobility State change 
Subscription ID = 1
Version = 56
Version 56 {
   E-ARFCN = 5780
   Physical Cell ID = 147
   Previous UE Mobility State = Normal Mobility
   Current UE Mobility State = Normal Mobility
   Camp Time = 978611309 ms
   Current Time = 978612085 ms
   High State End Time = Invalid
   Medium State End Time = Invalid
   t_cr_max = 30s
   t_cr_max_hyst = 30s
   n_cr_medium = 6
   n_cr_high = 11
   Number Of Cell Switches = 0
}
""")
        messages.append(msg)
        msg = ParsedRawMessage(index=0, packet_type="0xB179", packet_length=100,
                               name="LTE ML1 Connected Mode LTE Intra-Freq Meas Results",
                               subtitle="", datetime="2024 Jan 15  07:16:06.024", packet_text=
                               """2024 Jan 15  07:16:06.024  [0C]  0xB179  LTE ML1 Connected Mode LTE Intra-Freq Meas Results
Subscription ID = 1
Version = 56
Serving Cell Index = PCell
FW Serving Cell Index = PCell
E-ARFCN = 5780
Serving Physical Cell ID = 147
Sub-frame Number = 908
Serving Filtered RSRP = -76.56 dBm
Serving Filtered RSRQ = -12.19 dB
Number of Neighbor Cells = 1
Number of Detected Cells = 0
Neighbor Cells
   --------------------------------
   |   |        |Filtered|Filtered|
   |   |Physical|RSRP    |RSRQ    |
   |#  |Cell ID |(dBm)   |(dB)    |
   --------------------------------
   |  0|      53|  -84.81|  -18.75|
""")
        messages.append(msg)
        msg = ParsedRawMessage(index=0, packet_type="0xB176", packet_length=100,
                               name="LTE Initial Acquisition Results",
                               subtitle="", datetime="2024 Jan 15  07:16:05.831", packet_text=
                               """2024 Jan 15  07:16:05.831  [47]  0xB176  LTE Initial Acquisition Results
Subscription ID = 1
Version = 32
E-ARFCN = 5780
Band = 17
Duplex Mode = FDD
Result = Success
Min Search Half Frames = 1
Min Search Half Frames Early Abort = 1
Max Search Half Frames = 4
Max PBCH Frames = 20
Number of Blocked Cells = 0
Number PBCH Decode Attemp Cells = 1
Number of Search Results = 3
Search Results
   ----------------------------------------------------------------------
   |   |       |      |        |        |Frequency|PSS        |         |
   |   |Frame  |Sample|Physical|        |Offset   |Correlation|SSS Power|
   |#  |Offset |Offset|Cell ID |CP      |(Hz)     |Result     |Value    |
   ----------------------------------------------------------------------
   |  0|Unknown|168914|     147|  Normal|      293|          0| 0.000806|
   |  1|Unknown| 15330|      53|  Normal|      293|          0| 0.000092|
   |  2|Unknown|168914|     295|  Normal|      293|          0| 0.000044|

PBCH Decode Attempt Cells
   ----------------------------------------------------------------------------
   |   |       |      |          |Updated  |        |Number  |       |        |
   |   |       |      |          |Frequency|        |of      |       |Number  |
   |   |Frame  |Sample|MIB       |Offset   |Physical|Decode  |Decode |of Tx   |
   |#  |Offset |Offset|Payload   |(Hz)     |Cell ID |Attempts|Result |Antennas|
   ----------------------------------------------------------------------------
   |  0|Unknown|168914|0x6044E000|        0|     147|       1|Success|       4|
""")
        messages.append(msg)
        msg = ParsedRawMessage(index=0, packet_type="0xB173", packet_length=100,
                               name="LTE PDSCH Stat Indication",
                               subtitle="", datetime="2024 Jan 15  07:15:35.731", packet_text=
                               """2024 Jan 15  07:15:35.731  [84]  0xB173  LTE PDSCH Stat Indication
Subscription ID = 1
Version = 48
Num Records = 3
Records
   ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
   |   |        |     |   |      |Num      |       |Transport Blocks                                                                                                                |    |    |     |       |
   |   |        |     |   |      |Transport|Serving|    |  |   |      |         |     |Discarded|                                   |           |       |   |   |          |        |    |    |Alt  |       |
   |   |Subframe|Frame|Num|Num   |Blocks   |Cell   |HARQ|  |   |CRC   |         |TB   |reTx     |                                   |Did        |TB Size|   |Num|Modulation|ACK/NACK|PMCH|Area|TBS  |Alt MCS|
   |#  |Num     |Num  |RBs|Layers|Present  |Index  |ID  |RV|NDI|Result|RNTI Type|Index|Present  |Discarded ReTx                     |Recombining|(bytes)|MCS|RBs|Type      |Decision|ID  |ID  |Index|Enabled|
   ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
   |  0|       0|  105|  3|     1|        1|  PCELL|   1| 0|  0|  Pass|        C|    0|     None|                         NO_DISCARD|         No|     18|  1|  3|      QPSK|     ACK|    |    | NONE|  false|
   |  1|       7|  113|  3|     1|        1|  PCELL|   4| 0|  1|  Pass|        C|    0|     None|                         NO_DISCARD|         No|     18|  1|  3|      QPSK|     ACK|    |    | NONE|  false|
   |  2|       5|  120|  3|     1|        1|  PCELL|   6| 0|  1|  Pass|        C|    0|     None|                         NO_DISCARD|         No|     18|  1|  3|      QPSK|     ACK|    |    | NONE|  fals
""")
        messages.append(msg)
        msg = ParsedRawMessage(index=0, packet_type="0xB970", packet_length=100,
                               name="NR5G ML1 Searcher Idle S Criteria",
                               subtitle="", datetime="2024 Jan 15  07:18:07.523 ", packet_text=
                               """2024 Jan 15  07:18:07.523  [80]  0xB970  NR5G ML1 Searcher Idle S Criteria
Subscription ID = 1
Misc ID         = 0
Major.Minor Version = 2. 4
System Time
   Slot Number = 0
   SubFrame Number = 6
   System Frame Number = 976
   SCS = 15KHZ
NR ARFCN = 129370
Phy Cell ID = 70
Serving SSB Index = 3
Q Rx Level Min = -124 dBm
Q RX Level Min Offset = NP
P Max = 23 dBm
Max UE TX Power = 23 dBm
Qoffset Temp = 0 dB
Cell Quality RSRP = -100.45 dBm
S Rx Level = 24 dB
Q Qual Min Present = 0
Q Qual Min = NA
Q Qualmin Offset = NA
S Qual = NA
Cell Quality RSRQ = -18.41 dBm
Result = SUCCESS
""")
        messages.append(msg)
        msg = ParsedRawMessage(index=0, packet_type="0xB828", packet_length=100,
                               name="NR5G RRC PLMN Search Response",
                               subtitle="", datetime="2024 Jan 15  07:18:06.923", packet_text=
                               """2024 Jan 15  07:18:06.923  [03]  0xB828  NR5G RRC PLMN Search Response
Subscription ID = 1
Misc ID         = 0
Version = 6
PLMN Search Response
   Source RAT = LTE
   Current Search RAT = NR5G
   Network Search Status = COMPLETED
   Num PLMNs = 1
   PLMN List
      -----------------------------------------------------------------------------
      |   |      |     |     |     |          |munual|          |        |        |
      |   |      |Plmn |Plmn |Plmn |          |CAG   |          |        |        |
      |#  |RAT   |byte0|byte1|byte2|CAG ID    |sel   |ARFCN     |SCS     |Band    |
      -----------------------------------------------------------------------------
      |  0|  NR5G|   13|   03|   43|        NA|    NA|    401050|   15KHZ|      70|
""")
        messages.append(msg)
        msg = ParsedRawMessage(index=0, packet_type="0xB88A", packet_length=100,
                               name="NR5G MAC RACH Attempte",
                               subtitle="", datetime="2024 Jan 15  07:17:09.147", packet_text=
                               """2024 Jan 15  07:17:09.147  [49]  0xB88A  NR5G MAC RACH Attempt
Subscription ID = 1
Misc ID         = 0
Major.Minor = 3. 10
RACH Attempt
Num Attempts = 1
Power Ramping Count = 1
SSB ID = 0
CSI-RS ID = 0
Carrier ID = 0
RACH Result = SUCCESS
Contention Type = DL_MCE
RACH MSG Bitmask = F
Msg1 SCS = 1.25KHZ
Msg2 SCS = 15KHZ
UL BWP SCS = 15KHZ
Power Limited = 0
RACH Msg1
  -------------------------------------------------------------------------------------------------------------------------------------------
  |                   |      |          |      |     |    |   |Cyclic|    |       |        |                   |                   |Backoff |
  |System Time        |Symbol|Preamble  |PRACH |     |    |   |Shift |    |       |Regular |RAR Window Start   |RAR Window End     |Duration|
  |Frame|SubFrame|Slot|Start |Format    |Config|Uroot|RAID|FDM|V.    |N_CS|RA_RNTI|Pathloss|Frame|SubFrame|Slot|Frame|SubFrame|Slot|(usec)  |
  -------------------------------------------------------------------------------------------------------------------------------------------
  |  257|       4|   0|     0|  FORMAT_0|    13|  160|  20|  0|     0| 167|     57|      99|  257|       5|   0|  258|       5|   0|       0|

RACH Msg2
  --------------------------------------------------------------------
  |                   |Max     |      |     |               |        |
  |System Time        |Backoff |      |TA   |               |RAID    |
  |Frame|SubFrame|Slot|Duration|T_RNTI|Value|Result         |Received|
  --------------------------------------------------------------------
  |  257|       8|   0|       0| 11852|   12|    RAPID_MATCH|      20|

RACH Msg3
  --------------------------------------------------------------------------------------------------------------------
  |System Time        |Msg3 Grant|Msg3 Grant|HARQ|      |                                                            |
  |Frame|SubFrame|Slot|Raw       |Bytes     |ID  |C_RNTI|MAC PDU                                                     |
  --------------------------------------------------------------------------------------------------------------------
  |  258|       2|   0|   11A00C0|         0|   0|    NA|   1E   15   6D   9C   87   66    0    0    0    0    0    0|

RACH Msg4
  --------------------------------------------------------------------
  |                   |Contention         |Contention         |      |
  |System Time        |Resolution Start   |Resolution End     |      |
  |Frame|SubFrame|Slot|Frame|SubFrame|Slot|Frame|SubFrame|Slot|C_RNTI|
  --------------------------------------------------------------------
  |  258|       9|   0|  258|       2|   0|  264|       6|   0| 11852|
""")
        messages.append(msg)
        msg = ParsedRawMessage(index=0, packet_type="0xB0F7", packet_length=100,
                               name="LTE NAS EMM RRC Service Request",
                               subtitle="", datetime="2024 Jan 15  07:16:05.535", packet_text=
                               '''2024 Jan 15  07:16:05.535  [DA]  0xB0F7  LTE NAS EMM RRC Service Request
Subscription ID = 1
Version = 32
AS ID = 0
Trans Id = 16973831
Network Select Mode = SYS_NETWORK_SELECTION_MODE_AUTOMATIC
Is Req Plmn Valid = true
Req Plmn[0] {
   MCC_digit_1 = 3
   MCC_digit_2 = 1
   MCC_digit_3 = 0
   MNC_digit_3 = 0
   MNC_digit_1 = 4
   MNC_digit_2 = 1
}
Is Rplmn Valid = true
Rplmn[0] {
   MCC_digit_1 = 3
   MCC_digit_2 = 1
   MCC_digit_3 = 0
   MNC_digit_3 = 0
   MNC_digit_1 = 4
   MNC_digit_2 = 1
}
Is Hplmn Valid = false
Ehplmn List {
   Number of Plmns = 2
   Plmn[0] {
      MCC_digit_1 = 3
      MCC_digit_2 = 1
      MCC_digit_3 = 3
      MNC_digit_3 = 0
      MNC_digit_1 = 3
      MNC_digit_2 = 4
   }
   Plmn[1] {
      MCC_digit_1 = 3
      MCC_digit_2 = 1
      MCC_digit_3 = 3
      MNC_digit_3 = 0
      MNC_digit_1 = 3
      MNC_digit_2 = 5
   }
}
Eplmn List {
   Number of Plmns = 0
}
Scan Is New = true
Use Timer = false
Lte Scan Time = 0
Req Type = 0
Csg Id = 0xFFFFFFFF
TRM Timeout = 0xFFFFFFFF
Ehplmn Camping Allowed = true
Scan Scope = SYS_SCAN_SCOPE_ACQ_DB
Emc Srv Pending = false
Rat Priority List {
   Num Items = 4
   Next Acq Sys Index = 0
   Priority List Info[0] {
      Acq Sys Mode = SYS_SYS_MODE_MAX
      Band Cap {
         Chgwt Band Cap = 0
      }
      Bst Rat Acq Required = false
      Acq Sys Time Interval = 0
   }
   Priority List Info[1] {
      Acq Sys Mode = SYS_SYS_MODE_LTE
      Band Cap {
         Lte Band Cap[0] {
            bits_1_64 = 0xA140330B389F
            bits_65_128 = 0x42
            bits_129_192 = 0x0
            bits_193_256 = 0x0
         }
      }
      Bst Rat Acq Required = true
      Bst Band Cap[0] {
         Lte Band Cap[0] {
            bits_1_64 = 0xA140330B389F
            bits_65_128 = 0x42
            bits_129_192 = 0x0
            bits_193_256 = 0x0
         }
      }
      Acq Sys Time Interval = 0
   }
   Priority List Info[2] {
      Acq Sys Mode = SYS_SYS_MODE_WCDMA
      Band Cap {
         Chgwt Band Cap = 562950069289344
      }
      Bst Rat Acq Required = true
      Bst Band Cap[0] {
         Chgwt Band Cap = 562950069289344
      }
      Acq Sys Time Interval = 0
   }
   Priority List Info[3] {
      Acq Sys Mode = SYS_SYS_MODE_GSM
      Band Cap {
         Chgwt Band Cap = 562950069289344
      }
      Bst Rat Acq Required = true
      Bst Band Cap[0] {
         Chgwt Band Cap = 562950069289344
      }
      Acq Sys Time Interval = 0
   }
   Scan Type {
      New Scan = false
      Use Timer = false
   }
}''')
        messages.append(msg)
        msg = ParsedRawMessage(index=0, packet_type="0xB887", packet_length=100,
                               name="LTE NAS ESM Bearer Context State",
                               subtitle="", datetime="2024 Jan 15  07:15:16.754", packet_text=
                               """2024 Jan 15  07:15:35.471  [55]  0xB887  NR5G MAC PDSCH Status
Subscription ID = 1
Misc ID         = 0
Major.Minor = 3. 6
Num Records = 2
Records
   ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
   |   |                     |      |PDSCH Status Info                                                                                                                                                                                                                                                                                                  |
   |   |                     |      |       |    |      |    |         |    |       |        |        |     |        |   |   |   |  |HARQ |              |    |   |      |         |        |      |    |   |       |      |      |    |       |       |       |       |      |     |        |     |        |          |          |          |          |
   |   |                     |      |       |    |      |    |         |    |       |        |        |     |        |   |   |   |  |Or   |              |K1  |   |      |         |        |      |    |   |       |      |      |    |       |       |       |       |      |     |        |     |        |          |          |          |          |
   |   |                     |Num   |       |    |      |    |         |    |       |        |        |     |        |   |   |   |  |MBSFN|              |Or  |   |      |         |        |      |New |   |       |      |      |    |HD     |HARQ   |HD     |HARQ   |      |Is   |        |High |        |          |          |          |          |
   |   |System Time          |PDSCH |Carrier|Tech|      |Conn|         |Band|Variant|Physical|        |TB   |        |SCS|   |Num|  |Area |              |PMCH|   |Num   |Iteration|CRC     |CRC   |Tx  |   |Discard|Bypass|Bypass|Num |Onload |Onload |Offload|Offload|Did   |IOVec|        |Clock|        |Rx Antenna|Rx Antenna|Rx Antenna|Rx Antenna|
   |#  |Slot|Numerology|Frame|Status|ID     |Id  |Opcode|ID  |Bandwidth|Type|Id     |Cell ID |EARFCN  |Index|TB Size |MU |MCS|Rbs|RV|Id   |RNTI Type     |ID  |TCI|Layers|Index    |State   |Status|Flag|NDI|Mode   |Decode|HARQ  |ReTx|Timeout|Timeout|Timeout|Timeout|Recomb|Valid|Mod Type|Mode |Num RX  |Mapping 0 |Mapping 1 |Mapping 2 |Mapping 3 |
   ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
   |  0|   0|     30KHZ|  107|     1|      0|   1|     0|   0|       10|   0|      0|     700|  660768|    0|     123|  1|  0| 16| 0|   10|        C RNTI|   5|  0|     2|        0|    PASS|  PASS|   1|  0|      0|     0|     0|   0|      0|      0|      0|      0|     0| TRUE|    QPSK|    0|2X2_MIMO|         0|         0|         0|         0|
   |  1|   6|     30KHZ|  107|     1|      0|   1|     0|   0|       10|   0|      0|     700|  660768|    0|     123|  1|  0| 16| 0|   11|       C RNTI2|   8|  0|     2|        0|    PASS|  PASS|   1|  0|      0|     0|     0|   0|      0|      0|      0|      0|     0| TRUE|    QPSK|    0|2X2_MIMO|         0|         0|         0|         0|
""")
        messages.append(msg)
        msg = ParsedRawMessage(index=0, packet_type="0x156A", packet_length=100,
                               name="0x156A  IMS RTCP",
                               subtitle="", datetime="2024 Jan 15  07:14:51.652", packet_text=
                               '''2024 Jan 15  07:14:51.652  [4F]  0x156A  IMS RTCP
Subscription ID = 1
Version = 10
Direction = UE_TO_NETWORK
Rat Type = LTE
Type = SENDER_REPORT
Codec Type = AMR-WB
SenderReport {
   P = 0
   Rc = 1
   Packet Type = 200
   length = 28
   ssrc = 4255989150
   Ntp timestamp Hi = 978536
   Ntp timestamp Lo = 3826815860
   Rtp TimeStamp = 77984
   Sender Packet Cnt = 37
   Sender octent cnt = 1081
   Report Sender Block[0] {
      Ssrc = 424995790
      Fraction Lost = 0
      Packet Lost = 0
      High Seq Num Recv = 119
      Inter Jitter = 140
      SR = 1508474911
      DLSR = 167313
      Rdtrip Time = 0
      padding = 3
      SC = 1
      Packet Type = 202
      Length = 0
      SdesItem[0] {
         Ssrc = 4255989150
         Cname = 1
         Cname Length = 12
         CName Str = 10.55.196.81
      }
   }
}''')
        messages.append(msg)
        msg = ParsedRawMessage(index=0, packet_type="0xB800", packet_length=100,
                               name="NR5G NAS SM5G Plain OTA Incoming Msg",
                               subtitle="PDU session establishment accept", datetime="2024 Jan 15  07:18:10.187",
                               packet_text=
                               '''2024 Jan 15  07:18:10.187  [93]  0xB800  NR5G NAS SM5G Plain OTA Incoming Msg  --  PDU session establishment accept
Subscription ID = 1
Misc ID         = 0
pkt_version = 1 (0x1)
rel_number = 15 (0xf)
rel_version_major = 4 (0x4)
rel_version_minor = 0 (0x0)
prot_disc_type = 14 (0xe)
ext_protocol_disc = 46 (0x2e)
pdu_session_id = 2 (0x2)
proc_trans_id = 111 (0x6f)
msg_type = 194 (0xc2) (PDU session establishment accept)
nr5g_smm_msg
  pdu_session_estab_accept
    ssc_mode
      ssc_mode_val = 1 (0x1)
    pdu_session_type
      pdu_session_type = 1 (0x1) (IPv4)
    authorized_qos_rules
      num_recs = 1 (0x1)
      Qos_rule[0]
        qos_rule_id = 1 (0x1)
        rule_opcode = 1 (0x1) (Create new QoS rule)
        DQR = 1 (0x1)
        num_pkt_filter = 1 (0x1)
        pkt_filters[0]
          change_rule
            pkt_filter_dir = 3 (0x3) (bidirectional)
            pkt_filter_id = 1 (0x1)
            num_comps = 1 (0x1)
            pkt_filters_comp_list[0]
              comp_type_id = 1 (0x1) (Match-all)
        rule_precedene_present = 1 (0x1)
        qos_rule_precedence = 254 (0xfe)
        qfi_present = 1 (0x1)
        segregation = 0 (0x0)
        qfi = 1 (0x1)
    session_ambr
      length = 6 (0x6)
      session_ambr_dl_unit = 11 (0xb) (inc in multiple of 1 Gbps)
      session_ambr_dl = 2 (0x2)
      session_ambr_ul_unit = 11 (0xb) (inc in multiple of 1 Gbps)
      session_ambr_ul = 1 (0x1)
    _5gsm_cause_incl = 1 (0x1)
    _5gsm_cause
      cause = 50 (0x32) (PDU session type IPv4 only allowed)
    pdu_addr_incl = 1 (0x1)
    pdu_addr
      length = 5 (0x5)
      si6lla = 0 (0x0)
      pdu_session_type = 1 (0x1)
      ipv4_addr[0] = 10 (0xa)
      ipv4_addr[1] = 2 (0x2)
      ipv4_addr[2] = 254 (0xfe)
      ipv4_addr[3] = 122 (0x7a)
    rq_timer_incl = 0 (0x0)
    s_nssai_incl = 1 (0x1)
    s_nssai
      s_nssai_len = 1 (0x1)
      sst = 1 (0x1)
    always_on_pdu_session_ind_incl = 0 (0x0)
    mapped_eps_bearer_context_inc = 1 (0x1)
    mapped_eps_bearer_context
      num_bearer_context = 1 (0x1)
      bearer_context[0]
        eps_bearer_id = 6 (0x6)
        opcode = 1 (0x1) (Create new EPS bearer)
        E_bit = 1 (0x1)
        num_eps_params = 2 (0x2)
        eps_params[0]
          eps_params_id = 1 (0x1)
          bearer_context_params
            eps_qos
              qci = 9 (0x9) (QC9)
              oct4_incl = 0 (0x0)
              oct5_incl = 0 (0x0)
              oct6_incl = 0 (0x0)
              oct7_incl = 0 (0x0)
              oct8_incl = 0 (0x0)
              oct9_incl = 0 (0x0)
              oct10_incl = 0 (0x0)
              oct11_incl = 0 (0x0)
              oct12_incl = 0 (0x0)
              oct13_incl = 0 (0x0)
              oct14_incl = 0 (0x0)
              oct15_incl = 0 (0x0)
        eps_params[1]
          eps_params_id = 4 (0x4)
          bearer_context_params
            apn_ambr
              apn_ambr_dl = 254 (0xfe) (8640 kbps)
              apn_ambr_ul = 254 (0xfe) (8640 kbps)
              oct5_incl = 1 (0x1)
              apn_ambr_dl_ext = 226 (0xe2) (208 Mbps)
              oct6_incl = 1 (0x1)
              apn_ambr_ul_ext = 238 (0xee) (232 Mbps)
              oct7_incl = 1 (0x1)
              apn_ambr_dl_ext2 = 7 (0x7) (2000.000000 Mbps)
              oct8_incl = 1 (0x1)
              apn_ambr_ul_ext2 = 3 (0x3) (1000.000000 Mbps)
    eap_msg_incl = 0 (0x0)
    auth_qos_flow_desc_incl = 1 (0x1)
    qos_flow_desc
      num_qos_flow_desc = 1 (0x1)
      qos_flow_description[0]
        qfi = 1 (0x1)
        opcode = 1 (0x1) (Create new QoS flow description)
        e_bit = 1 (0x1)
        num_parameters = 2 (0x2)
        params[0]
          params_id = 1 (0x1)
          length = 1 (0x1)
          qos_flow_desc_params
            _5qi
              _5qi_value = 9 (0x9)
        params[1]
          params_id = 7 (0x7)
          length = 1 (0x1)
          qos_flow_desc_params
            eps_bearer_id
              id = 6 (0x6)
    ext_prot_config_incl = 1 (0x1)
    ext_prot_config
      ext = 1 (0x1)
      conf_prot = 0 (0x0)
      num_recs = 6 (0x6)
      prot_or_container[0]
        id = 32801 (0x8021) (IPCP)
        prot_or_container
          prot_len = 16 (0x10)
          ipcp_prot
            ipcp_prot_id = 3 (0x3) (CONF_NAK)
            identifier = 0 (0x0)
            rfc1332_conf_nak
              num_options = 2 (0x2)
              conf_options[0]
                type = 129 (0x81)
                rfc1877_primary_dns_server_add
                  length = 6 (0x6)
                  ip_addr = 182411276 (0xadf600c) (10.223.96.12)
              conf_options[1]
                type = 131 (0x83)
                rfc1877_sec_dns_server_add
                  length = 6 (0x6)
                  ip_addr = 182411291 (0xadf601b) (10.223.96.27)
      prot_or_container[1]
        id = 3 (0x3) (DNS Server IPv6 Address)
        prot_or_container
          prot_len = 16 (0x10)
          address
            addr = 0x2605c540884000000000000000000100 (2605:c540:8840:0:0:0:0:100)
      prot_or_container[2]
        id = 3 (0x3) (DNS Server IPv6 Address)
        prot_or_container
          prot_len = 16 (0x10)
          address
            addr = 0x2605c540884000000000000000000101 (2605:c540:8840:0:0:0:0:101)
      prot_or_container[3]
        id = 13 (0xd) (DNS Server IPv4 Address)
        prot_or_container
          prot_len = 4 (0x4)
          container
            container_contents[0] = 10 (0xa)
            container_contents[1] = 223 (0xdf)
            container_contents[2] = 96 (0x60)
            container_contents[3] = 12 (0xc)
      prot_or_container[4]
        id = 13 (0xd) (DNS Server IPv4 Address)
        prot_or_container
          prot_len = 4 (0x4)
          container
            container_contents[0] = 10 (0xa)
            container_contents[1] = 223 (0xdf)
            container_contents[2] = 96 (0x60)
            container_contents[3] = 27 (0x1b)
      prot_or_container[5]
        id = 5 (0x5) (Selected Bearer Control Mode)
        prot_or_container
          prot_len = 1 (0x1)
          container
            container_contents[0] = 1 (0x1)
    dnn_incl = 1 (0x1)
    dnn
      dnn_len = 9 (0x9)
      dnn_val[0] = 8 (0x8) (length)
      dnn_val[1] = 105 (0x69) (i)
      dnn_val[2] = 110 (0x6e) (n)
      dnn_val[3] = 116 (0x74) (t)
      dnn_val[4] = 101 (0x65) (e)
      dnn_val[5] = 114 (0x72) (r)
      dnn_val[6] = 110 (0x6e) (n)
      dnn_val[7] = 101 (0x65) (e)
      dnn_val[8] = 116 (0x74) (t)
    _5gsm_nwk_feature_support_incl = 0 (0x0)
    srv_plmn_rate_ctrl_incl = 0 (0x0)
    at_sss_container_incl = 0 (0x0)
    ctrl_plane_only_ind_incl = 0 (0x0)
    ip_hc_config_incl = 0 (0x0)
    ethernet_hc_config_incl = 0 (0x0)
    serv_level_aa_incl = 0 (0x0)
    recv_msb_container_incl = 0 (0x0)''')
        messages.append(msg)
        msg = ParsedRawMessage(index=0, packet_type="0xB80B", packet_length=100,
                               name="NR5G NAS MM5G Plain OTA Outgoing Msg",
                               subtitle="Security mode complete", datetime="2024 Jan 15  07:17:09.243", packet_text=
                               '''2024 Jan 15  07:17:09.243  [47]  0xB80B  NR5G NAS MM5G Plain OTA Outgoing Msg  --  Security mode complete
Subscription ID = 1
Misc ID         = 0
pkt_version = 1 (0x1)
rel_number = 15 (0xf)
rel_version_major = 4 (0x4)
rel_version_minor = 0 (0x0)
prot_disc_type = 14 (0xe)
ext_protocol_disc = 126 (0x7e)
security_header = 0 (0x0)
msg_type = 94 (0x5e) (Security mode complete)
nr5g_mm_msg
  security_mode_complete
    imeisv_inc = 1 (0x1)
    imeisv
      ident_type = 5 (0x5) (IMEI_SV)
      odd_even_ind = 0 (0x0)
      num_ident = 17 (0x11)
      ident[0] = 3 (0x3)
      ident[1] = 5 (0x5)
      ident[2] = 9 (0x9)
      ident[3] = 3 (0x3)
      ident[4] = 0 (0x0)
      ident[5] = 8 (0x8)
      ident[6] = 7 (0x7)
      ident[7] = 9 (0x9)
      ident[8] = 0 (0x0)
      ident[9] = 8 (0x8)
      ident[10] = 6 (0x6)
      ident[11] = 8 (0x8)
      ident[12] = 3 (0x3)
      ident[13] = 1 (0x1)
      ident[14] = 0 (0x0)
      ident[15] = 5 (0x5)
      ident[16] = 15 (0xf)
    nas_msg_container_inc = 1 (0x1)
    nas_msg_container
      num_nas_msg_container = 96 (0x60)
      nas_msg_container[0] = 126 (0x7e)
      nas_msg_container[1] = 0 (0x0)
      nas_msg_container[2] = 65 (0x41)
      nas_msg_container[3] = 10 (0xa)
      nas_msg_container[4] = 0 (0x0)
      nas_msg_container[5] = 11 (0xb)
      nas_msg_container[6] = 242 (0xf2)
      nas_msg_container[7] = 19 (0x13)
      nas_msg_container[8] = 0 (0x0)
      nas_msg_container[9] = 20 (0x14)
      nas_msg_container[10] = 255 (0xff)
      nas_msg_container[11] = 73 (0x49)
      nas_msg_container[12] = 177 (0xb1)
      nas_msg_container[13] = 208 (0xd0)
      nas_msg_container[14] = 142 (0x8e)
      nas_msg_container[15] = 0 (0x0)
      nas_msg_container[16] = 58 (0x3a)
      nas_msg_container[17] = 16 (0x10)
      nas_msg_container[18] = 1 (0x1)
      nas_msg_container[19] = 7 (0x7)
      nas_msg_container[20] = 46 (0x2e)
      nas_msg_container[21] = 4 (0x4)
      nas_msg_container[22] = 240 (0xf0)
      nas_msg_container[23] = 112 (0x70)
      nas_msg_container[24] = 240 (0xf0)
      nas_msg_container[25] = 112 (0x70)
      nas_msg_container[26] = 82 (0x52)
      nas_msg_container[27] = 19 (0x13)
      nas_msg_container[28] = 3 (0x3)
      nas_msg_container[29] = 67 (0x43)
      nas_msg_container[30] = 1 (0x1)
      nas_msg_container[31] = 86 (0x56)
      nas_msg_container[32] = 145 (0x91)
      nas_msg_container[33] = 23 (0x17)
      nas_msg_container[34] = 7 (0x7)
      nas_msg_container[35] = 240 (0xf0)
      nas_msg_container[36] = 112 (0x70)
      nas_msg_container[37] = 192 (0xc0)
      nas_msg_container[38] = 64 (0x40)
      nas_msg_container[39] = 24 (0x18)
      nas_msg_container[40] = 128 (0x80)
      nas_msg_container[41] = 176 (0xb0)
      nas_msg_container[42] = 80 (0x50)
      nas_msg_container[43] = 2 (0x2)
      nas_msg_container[44] = 0 (0x0)
      nas_msg_container[45] = 0 (0x0)
      nas_msg_container[46] = 43 (0x2b)
      nas_msg_container[47] = 1 (0x1)
      nas_msg_container[48] = 3 (0x3)
      nas_msg_container[49] = 119 (0x77)
      nas_msg_container[50] = 0 (0x0)
      nas_msg_container[51] = 11 (0xb)
      nas_msg_container[52] = 242 (0xf2)
      nas_msg_container[53] = 19 (0x13)
      nas_msg_container[54] = 3 (0x3)
      nas_msg_container[55] = 67 (0x43)
      nas_msg_container[56] = 100 (0x64)
      nas_msg_container[57] = 64 (0x40)
      nas_msg_container[58] = 1 (0x1)
      nas_msg_container[59] = 196 (0xc4)
      nas_msg_container[60] = 33 (0x21)
      nas_msg_container[61] = 67 (0x43)
      nas_msg_container[62] = 27 (0x1b)
      nas_msg_container[63] = 24 (0x18)
      nas_msg_container[64] = 1 (0x1)
      nas_msg_container[65] = 0 (0x0)
      nas_msg_container[66] = 112 (0x70)
      nas_msg_container[67] = 0 (0x0)
      nas_msg_container[68] = 21 (0x15)
      nas_msg_container[69] = 23 (0x17)
      nas_msg_container[70] = 108 (0x6c)
      nas_msg_container[71] = 194 (0xc2)
      nas_msg_container[72] = 138 (0x8a)
      nas_msg_container[73] = 242 (0xf2)
      nas_msg_container[74] = 26 (0x1a)
      nas_msg_container[75] = 7 (0x7)
      nas_msg_container[76] = 72 (0x48)
      nas_msg_container[77] = 16 (0x10)
      nas_msg_container[78] = 11 (0xb)
      nas_msg_container[79] = 246 (0xf6)
      nas_msg_container[80] = 19 (0x13)
      nas_msg_container[81] = 0 (0x0)
      nas_msg_container[82] = 20 (0x14)
      nas_msg_container[83] = 255 (0xff)
      nas_msg_container[84] = 73 (0x49)
      nas_msg_container[85] = 177 (0xb1)
      nas_msg_container[86] = 208 (0xd0)
      nas_msg_container[87] = 142 (0x8e)
      nas_msg_container[88] = 0 (0x0)
      nas_msg_container[89] = 58 (0x3a)
      nas_msg_container[90] = 116 (0x74)
      nas_msg_container[91] = 0 (0x0)
      nas_msg_container[92] = 0 (0x0)
      nas_msg_container[93] = 83 (0x53)
      nas_msg_container[94] = 1 (0x1)
      nas_msg_container[95] = 3 (0x3)
    non_IMEISV_PEI_inc = 0 (0x0)''')
        messages.append(msg)
        msg = ParsedRawMessage(index=0, packet_type="0xB0C1", packet_length=100,
                               name="LTE RRC MIB Message Log Packet",
                               subtitle="", datetime="2024 Jan 19  21:46:03.829", packet_text=
                               '''2024 Jan 19  21:46:03.829  [E7]  0xB0C1  LTE RRC MIB Message Log Packet
Subscription ID = 1
Version = 2
Physical cell ID = 147
FREQ = 5780
SFN = 563
Number of TX Antennas = 4
DL Bandwidth = 10 MHz (50)''')
        messages.append(msg)
        msg = ParsedRawMessage(index=0, packet_type="0x156E", packet_length=100,
                               name="IMS SIP Message",
                               subtitle="IMS_SIP_BYE/INFORMAL_RESPONSE", datetime="2024 Jan 15  07:15:24.613",
                               packet_text=
                               '''2024 Jan 15  07:15:24.613  [87]  0x156E  IMS SIP Message  --  IMS_SIP_BYE/INFORMAL_RESPONSE
Subscription ID = 1
Version = 1
Direction = UE_TO_NETWORK
SDP Presence = 0
SIP Call ID Length = 35
SIP Message Length = 1042
SIP Message Logged Bytes = 1043
Message ID = IMS_SIP_BYE
Response Code = INFORMAL_RESPONSE (0)
CM Call ID = 532
SIP Call ID = 2063678468_2676265992@10.55.196.81
Sip Message = BYE sip:lucentNGFS-043632@10.228.38.176:6000;x-skey=00006e5e2f4500320003;x-afi=5;encoded-parm=QbkRBthOEgsTXgkTBA0HHiUrKz1CQEVBRUdHNhkTVBgiMXN0dCVqPTo9eS03fyFgYCJieSY.J3YwN0IcXlpWBQMIF11NTVJTUEpWARcYBw8fGwIcBF4eABROQEZBSA__ SIP/2.0
To: <tel:4256153170;phone-context=ims.mnc340.mcc313.3gppnetwork.org>;tag=64d20eb0-65a4db832c99ecc2-gm-po-lucentPCSF-111786
From: <sip:+13526739015@ims.mnc340.mcc313.3gppnetwork.org>;tag=2063678473
Call-ID: 2063678468_2676265992@10.55.196.81
CSeq: 989936647 BYE
Via: SIP/2.0/TCP 10.55.196.81:44901;branch=z9hG4bK1625500643
Max-Forwards: 70
P-Access-Network-Info: 3GPP-E-UTRAN-FDD;utran-cell-id-3gpp=310410910D67BBF16
Security-Verify: ipsec-3gpp; q=0.1; alg=hmac-md5-96; ealg=null; spi-c=4289143273; spi-s=4289143272; port-c=65485; port-s=6000
Content-Length: 0
P-Preferred-Identity: <sip:+13526739015@ims.mnc340.mcc313.3gppnetwork.org>
Reason: RELEASE_CAUSE ;cause=1 ;text="User ends call"
User-Agent: motorola_motorola edge plus 2023_T1TR33.43-48-21
Require: sec-agree
Proxy-Require: sec-agree''')
        messages.append(msg)
        msg = ParsedRawMessage(index=0, packet_type="0xB0EC", packet_length=100,
                               name="LTE NAS EMM Plain OTA Incoming Message",
                               subtitle="Identity request Msg", datetime="2024 Jan 15  07:16:06.069", packet_text=
                               """2024 Jan 15  07:16:06.069  [64]  0xB0EC  LTE NAS EMM Plain OTA Incoming Message  --  Identity request Msg
Subscription ID = 1
pkt_version = 1 (0x1)
rel_number = 9 (0x9)
rel_version_major = 5 (0x5)
rel_version_minor = 0 (0x0)
security_header_or_skip_ind = 0 (0x0)
prot_disc = 7 (0x7) (EPS mobility management messages)
msg_type = 85 (0x55) (Identity request)
lte_emm_msg
  emm_id_req
    identity_type_2
      type_of_identity = 3 (0x3)
""")
        messages.append(msg)
        msg = ParsedRawMessage(index=0, packet_type="0xB0E4", packet_length=100,
                               name="LTE NAS ESM Bearer Context State",
                               subtitle="", datetime="2024 Jan 15  07:15:16.754", packet_text=
                               """2024 Jan 15  07:15:16.754  [24]  0xB0E4  LTE NAS ESM Bearer Context State 
Subscription ID = 1
Version = 1
Bearer ID = 7
Bearer State = ACTIVE_PENDING
Connection ID = 6
""")
        messages.append(msg)
        msg = ParsedRawMessage(index=0, packet_type="0xB0C2", packet_length=100,
                               name="LTE RRC Serving Cell Info Log Pkt",
                               subtitle="", datetime="2024 Jan 15  07:15:48.079", packet_text=
                               """2024 Jan 15  07:15:48.079  [1A]  0xB0C2  LTE RRC Serving Cell Info Log Pkt
Subscription ID = 1
Version = 3
Physical cell ID = 147
DL FREQ = 66986
UL FREQ = 132522
DL Bandwidth = 10 MHz
UL Bandwidth = 10 MHz
Cell Identity = 108773142
Tracking area code = 37133
Freq Band Indicator = 66
MCC = 310
Number of MNC digits = 3
MNC = 410
Allowed Access = Full
""")
        messages.append(msg)
        msg = ParsedRawMessage(index=0, packet_type="0x1832", packet_length=100,
                               name="IMS Registration",
                               subtitle="", datetime="2024 Jan 15  07:15:50.978", packet_text=
                               """2024 Jan 15  07:15:50.978  [7A]  0x1832  IMS Registration
Subscription ID = 1
Version = 1
Registration Type = De-Registration
Call Id Length = 35
Call Id = 2063326930_2676030104@10.55.196.81
Request Uri Length = 38
Request Uri = sip:ims.mnc340.mcc313.3gppnetwork.org
To Length = 56
To = <sip:313340200597860@ims.mnc340.mcc313.3gppnetwork.org>
Result = OK
""")
        messages.append(msg)
        msg = ParsedRawMessage(index=0, packet_type="0x1831", packet_length=100,
                               name="IMS VoLTE Session End",
                               subtitle="", datetime="2024 Jan 15  07:15:24.609", packet_text=
                               """2024 Jan 15  07:15:24.609  [53]  0x1831  IMS VoLTE Session End
Subscription ID = 1
Version = 6
Dialled String Length = 62
Dialled String = tel:4256153170;phone-context=ims.mnc340.mcc313.3gppnetwork.org
Direction = MO
CallID Len = 34
CallID = 2063678468_2676265992@10.55.196.81
Type = 0
Originating Uri Length = 50
Originating Uri = sip:+13526739015@ims.mnc340.mcc313.3gppnetwork.org
Terminating Uri Length = 62
Terminating Uri = tel:4256153170;phone-context=ims.mnc340.mcc313.3gppnetwork.org
End Cause = MO INITIATED
Call Setup Delay = 2024
RAT = DCM_RAT_LTE
Client End Cause = CLIENT_END_CAUSE_NONE
""")
        messages.append(msg)
        msg = ParsedRawMessage(index=0, packet_type="0xB167", packet_length=100,
                               name="LTE Random Access Request (MSG1) Report",
                               subtitle="", datetime="2024 Jan 25  21:03:52.627", packet_text=
                               """2024 Jan 25  21:03:52.627  [4C]  0xB167  LTE Random Access Request (MSG1) Report
Subscription ID = 1
Version = 40
Cell Index = 0
PRACH Config Index = 4
Preamble Sequence = 48
Physical Root Index = 181
Cyclic Shift = 552
PRACH Tx Power = 33 dBm
Beta PRACH = 1731
PRACH Frequency Offset = 4
Preamble Format = 0
Duplex Mode = FDD
Density Per 10 ms = 0.5
PRACH Timing SFN = 370
PRACH Timing Sub-fn = 4
PRACH Window Start SFN = 370
RACH Window Start Sub-fn = 7
PRACH Window End SFN = 371
PRACH Window End Sub-fn = 7
RA RNTI = 5
PRACH Actual Tx Power = 22
PRACH RX Freq Error = 3596
""")
        messages.append(msg)
        msg = ParsedRawMessage(index=0, packet_type="0x1569", packet_length=100,
                               name="IMS RTP Packet Loss",
                               subtitle="", datetime="2024 Jan 15  07:15:24.614", packet_text=
                               """2024 Jan 15  07:15:24.614  [99]  0x1569  IMS RTP Packet Loss
Subscription ID = 1
Version = 11
Number Lost = 0
Sequence Number = 152
SSRC = 2821336237
codecType = AMR-WB
LossType = RTP NETWORK LOSS
Num of Frame = 0
Total Lost = 0
Total Packets Count = 146
""")
        messages.append(msg)

        msg = ParsedRawMessage(index=0, packet_type="0x1830", packet_length=100,
                               name="IMS VoLTE Session Setup",
                               subtitle="", datetime="2024 Jan 15  07:15:21.813", packet_text=
                               """2024 Jan 15  07:15:21.813  [97]  0x1830  IMS VoLTE Session Setup
Subscription ID = 1
Version = 4
Dialled String Length = 62
Dialled String = tel:4256153170;phone-context=ims.mnc340.mcc313.3gppnetwork.org
Direction = MO
CallID Len = 34
CallID = 2063678468_2676265992@10.55.196.81
Type = 0
Originating Uri Length = 50
Originating Uri = sip:+13526739015@ims.mnc340.mcc313.3gppnetwork.org
Terminating Uri Length = 62
Terminating Uri = tel:4256153170;phone-context=ims.mnc340.mcc313.3gppnetwork.org
Result = OK
Call Setup Delay = 2024
RAT = DCM_RAT_LTE
""")
        messages.append(msg)
        msg = ParsedRawMessage(index=0, packet_type="0xB822", packet_length=100, name="RRC MIB Info",
                               subtitle="", datetime="2024 Jan 15  07:17:08.975", packet_text=
                               '''
2024 Jan 15  07:17:08.975  [39]  0xB822  NR5G RRC MIB Info
Subscription ID = 1
Misc ID         = 0
Major.Minor Version = 2. 0
Mib Info
   Physical Cell ID = 354
   DL Frequency = 174770
   SFN = 0
   Block Index = 0
   Half Number = 0
   Intra Freq Reselection = ALLOWED
   Cell Barred = NOT_BARRED
   PDCCH Config SIB1 = 100
   DMRS TypeA Position = POS3
   SSB Subcarrier Offset = 2
   MSB for k_ssb = 0
   Subcarrier Spacing Common = SCSC15
        ''')
        messages.append(msg)
        msg = ParsedRawMessage(index=0, packet_type="0xB823", packet_length=100, name="RRC Serving Cell Info",
                               subtitle="", datetime="2024 Jan 15  07:18:07.534", packet_text=
                               '''
2024 Jan 15  07:18:07.534  [9B]  0xB823  NR5G RRC Serving Cell Info
Subscription ID = 1
Misc ID         = 0
Major.Minor Version = 3. 2
Serving Cell Info
   Standby Mode = SINGLE STANDBY
   DDS sub = true
   HST mode = false
   Physical Cell ID = 70
   NR Cell Global Identity = 0x01303430D59FE0C3
   DL Frequency = 129370
   UL Frequency = 137664
   DL Bandwidth = 10
   UL Bandwidth = 10
   Cell Id = 0xD59FE0C3
   Selected PLMN MCC = 313
   Num MNC Digits = 3
   Selected PLMN MNC = 340
   Allowed Access = 0
   TAC = 87697
   Freq Band Indicator = 71


        ''')
        messages.append(msg)
        msg = ParsedRawMessage(index=0, packet_type="0xB8D8", packet_length=100, name="NR5G LL1 LOG SERVING SNR",
                               subtitle="", datetime="2024 Jan 15  07:14:41.128", packet_text=
                               '''
2024 Jan 15  07:14:22.238  [49]  0xB8D8  NR5G LL1 LOG SERVING SNR
Subscription ID = 1
Misc ID         = 0
Major Version = 3
Minor Version = 2
Starting SFN = 976
Sub FN = 0
Cell Id = 700
Carrier Index = 0
Reference Signal = SSB
RX[0]
   SNR = 13.74 dB
RX[1]
   SNR = 18.63 dB
RX[2]
   SNR = 10.17 dB
RX[3]
   SNR = 9.57 dB


        ''')
        messages.append(msg)

        msg = ParsedRawMessage(index=0, packet_type="0xB16A", packet_length=100, name="LTE UE Identification Message",
                               subtitle="", datetime="2024 Jan 25  21:03:52.637", packet_text=
                               '''
2024 Jan 25  21:03:52.685  [F8]  0xB16A  LTE Contention Resolution Message (MSG4) Report
Subscription ID = 1
Version = 1
SFN = 0
Sub-fn = 15
Contention Result = Pass
UL ACK Timing SFN = 0
UL ACK Timing Sub-fn = 15

        ''')
        messages.append(msg)
        msg = ParsedRawMessage(index=0, packet_type="0xB169", packet_length=100, name="LTE UE Identification Message",
                               subtitle="", datetime="2024 Jan 25  21:03:52.637", packet_text=
                               '''
2024 Jan 25  21:03:52.637  [9C]  0xB169  LTE UE Identification Message (MSG3) Report
Subscription ID = 1
Version = 40
Modulation Type = QPSK
Cell Index = 0
TPC = 5
MCS = 5
RIV = 122
CQI = Disabled
UL Delay = Don't Delay
SFN = 371
Sub-fn = 5
Hopping Flag = Disabled
Starting Resource Block = 47
Num Resource Blocks = 2
Transport Block Size Index = TBS_INDEX_5
Redundancy Version Index = 0
HARQ ID = 3

        ''')
        messages.append(msg)
        msg = ParsedRawMessage(index=0, packet_type="0xB168", packet_length=100, name="LTE Random Access Response",
                               subtitle="", datetime="2024 Jan 25  21:03:52.637", packet_text=
                               '''
2024 Jan 25  21:03:52.637  [62]  0xB168  LTE Random Access Response (MSG2) Report
Subscription ID = 1
Version = 24
Cell Index = 0
RACH Procedure Type = Contention Free
RACH Procedure Mode = Initial Access
RNTI Type = C_RNTI
RNTI Value = 0
Timing Advance Included = Included
SFN = 370
Sub-fn = 9
Timing Advance = 10

        ''')
        messages.append(msg)
        msg = ParsedRawMessage(index=0, packet_type="0xB166", packet_length=100, name="LTE PRACH Configuration",
                               subtitle="", datetime="2024 Jan 25  20:55:19.030", packet_text=
                               '''
2024 Jan 25  20:55:19.030  [F6]  0xB166  LTE PRACH Configuration
Subscription ID = 1
Version = 40
Cell Index = 0
Logical Root Seq Index = 116
PRACH Config = 5
Preamble Format = 0
Duplex Mode = FDD
High Speed Flag = 0
PRACH Frequency Offset = 4
Max Transmissions MSG3 = 5
Cyclic Shift Zone Length = 8
RA Response Window Size = 10
        ''')
        messages.append(msg)
        msg = ParsedRawMessage(index=0, packet_type="0xB115", packet_length=100, name="LTE LL1 SSS Results",
                               subtitle="", datetime="2023 Nov 21  12:26:00.958", packet_text=
                               '''
2023 Nov 21  12:26:00.958  [D6]  0xB115  LTE LL1 SSS Results
Subscription ID = 1
Version = 122
Number of Barred Cells    = 0
Number of Detected Cells  = 1
Number of IC Cells        = 0
EARFCN                    = 66986
Detected Cells
   ---------------------------------------------------------------------------
   |   |SSS  |    |        |          |Frequency|     |    |        |Frame   |
   |   |Peak |Cell|        |Half Frame|Offset   |     |LNA |Frame   |Boundary|
   |#  |Value|ID  |CP      |Hypothesis|(Hz)     |Index|Gain|Boundary|Range   |
   ---------------------------------------------------------------------------
   |  0|12227| 147|  Normal|       Mid|        0|  Rx0| N/A|  122844|      16|
   |   |     |    |        |          |         |  Rx1| N/A|        |        |
        ''')
        messages.append(msg)
        msg = ParsedRawMessage(index=0, packet_type="0xB0E5", packet_length=100, name="LTE NAS ESM Bearer Context Info",
                               subtitle="",
                               datetime="2024 Jan 25  21:03:44.144", packet_text=
                               '''
        2024 Jan 25  21:03:44.144  [EC]  0xB0E5  LTE NAS ESM Bearer Context Info
Subscription ID = 1
Log version = 1
Context Type = Default
Bearer ID = 5
Bearer State = ACTIVE
Connection ID = 4
SDF ID = 0
LBI_VALID = FALSE
RB ID = 5
EPS_QOS
  eps_qos_length = 1 (0x1)
  qos_content
    qci = 6 (0x6) (QC6)
        ''')
        messages.append(msg)
        msg = ParsedRawMessage(index=0, packet_type="0xB825", packet_length=100, name="NR5G RRC Configuration Info",
                               subtitle="",
                               datetime="2024 Jan 15  07:17:09.173", packet_text=
                               '''2024 Jan 15  07:17:09.173  [DD]  0xB825  NR5G RRC Configuration Info
Subscription ID = 1
Misc ID         = 0
Major.Minor Version = 3. 4
Conn Config Info
   NR Cell Global Identity = 0x0130014457237C31
   State = CONNECTED
   Config Status = true
   Connectivity Mode = SA
   Standby Mode = SINGLE STANDBY
   Num Active SRB = 1
   Num Active DRB = 0
   MN MCG DRB IDs = NONE
   SN MCG DRB IDs = NONE
   MN SCG DRB IDs = NONE
   SN SCG DRB IDs = NONE
   MN Split DRB IDs = NONE
   SN Split DRB IDs = NONE
   LTE Serving Cell Info {
      Num Bands = 0
      LTE Bands = { 
         0, 0, 0, 0, 0, 0, 0, 0, 
         0, 0, 0, 0
      }
   }
   Num Contiguous CC Groups = 1
   Num Active CC = 1
   Num Active RB = 1
   Contiguous CC Info
      --------------------
      |Band  |DL BW|UL BW|
      |Number|Class|Class|
      --------------------
      |     5|    A|    A|

   NR5G Serving Cell Info
      -------------------------------------------------------------------------------------------
      |  |    |          |          |          |    |    |DL       |UL       |        |DL  |UL  |
      |CC|Cell|          |          |          |    |Band|Carrier  |Carrier  |        |Max |Max |
      |Id|Id  |DL Arfcn  |UL Arfcn  |SSB Arfcn |Band|Type|Bandwidth|Bandwidth|SCS     |MIMO|MIMO|
      -------------------------------------------------------------------------------------------
      | 0| 354|    174800|    165800|    174770|   5|SUB6|    10MHZ|    10MHZ|  15 kHz|   1|   1|

   Radio Bearer Info
      ------------------------------------------------------------------------------------------------------------------------------------------------------------------
      |  |           |          |              |       |            |            |UL  |              |          |       |            |            |UL PDCP  |UL Data   |
      |RB|Termination|          |              |DL ROHC|DL Cipher   |DL Integrity|RB  |              |UL Primary|UL ROHC|UL Cipher   |UL Integrity|Dup      |Split     |
      |ID|Point      |DL RB Type|DL RB Path    |Enabled|Algo        |Algo        |Type|UL RB Path    |Path      |Enabled|Algo        |Algo        |Activated|Threshold |
      ------------------------------------------------------------------------------------------------------------------------------------------------------------------
      | 1|         MN|       SRB|            NR|  false|          NA|          NA| SRB|            NR|         0|  false|          NA|          NA|    false|        NA|
        ''')
        messages.append(msg)
        msg = ParsedRawMessage(index=0, packet_type="0xB825", packet_length=100, name="NR5G RRC Configuration Info",
                               subtitle="",
                               datetime="2024 Jan 15  07:15:48.068", packet_text=
                               '''2024 Jan 15  07:15:48.068  [28]  0xB825  NR5G RRC Configuration Info
Subscription ID = 1
Misc ID         = 0
Major.Minor Version = 3. 4
Conn Config Info
   NR Cell Global Identity = 0x0000000000000000
   State = IDLE
   Config Status = true
   Connectivity Mode = NSA
   Standby Mode = SINGLE STANDBY
   Num Active SRB = 0
   Num Active DRB = 0
   MN MCG DRB IDs = NONE
   SN MCG DRB IDs = NONE
   MN SCG DRB IDs = NONE
   SN SCG DRB IDs = NONE
   MN Split DRB IDs = NONE
   SN Split DRB IDs = NONE
   LTE Serving Cell Info {
      Num Bands = 1
      LTE Bands = { 
         66, 0, 0, 0, 0, 0, 0, 0, 
         0, 0, 0, 0
      }
   }
   Num Contiguous CC Groups = 0
   Num Active CC = 0
   Num Active RB = 0
        ''')
        messages.append(msg)

        msg = ParsedRawMessage(index=0, packet_type="0xB825", packet_length=100, name="NR5G RRC Configuration Info",
                               subtitle="",
                               datetime="2024 Jan 15  07:17:10.501", packet_text=
                               '''2024 Jan 15  07:17:10.501  [FB]  0xB825  NR5G RRC Configuration Info
Subscription ID = 1
Misc ID         = 0
Major.Minor Version = 3. 4
Conn Config Info
   NR Cell Global Identity = 0x0000000000000000
   State = CONNECTED
   Config Status = true
   Connectivity Mode = NSA
   Standby Mode = SINGLE STANDBY
   Num Active SRB = 0
   Num Active DRB = 1
   MN MCG DRB IDs = 4
   SN MCG DRB IDs = NONE
   MN SCG DRB IDs = NONE
   SN SCG DRB IDs = NONE
   MN Split DRB IDs = NONE
   SN Split DRB IDs = NONE
   LTE Serving Cell Info {
      Num Bands = 1
      LTE Bands = { 
         17, 0, 0, 0, 0, 0, 0, 0, 
         0, 0, 0, 0
      }
   }
   Num Contiguous CC Groups = 0
   Num Active CC = 0
   Num Active RB = 1
   Radio Bearer Info
      ------------------------------------------------------------------------------------------------------------------------------------------------------------------
      |  |           |          |              |       |            |            |UL  |              |          |       |            |            |UL PDCP  |UL Data   |
      |RB|Termination|          |              |DL ROHC|DL Cipher   |DL Integrity|RB  |              |UL Primary|UL ROHC|UL Cipher   |UL Integrity|Dup      |Split     |
      |ID|Point      |DL RB Type|DL RB Path    |Enabled|Algo        |Algo        |Type|UL RB Path    |Path      |Enabled|Algo        |Algo        |Activated|Threshold |
      ------------------------------------------------------------------------------------------------------------------------------------------------------------------
      | 4|         MN|       DRB|           LTE|  false|   NEA0/NONE|   NIA0/NONE| DRB|           LTE|         0|  false|   NEA0/NONE|   NIA0/NONE|    false|        NA|
        ''')
        messages.append(msg)

        msg = ParsedRawMessage(index=0, packet_type="0xB97F", packet_length=100, name="NR5G ML1 Searcher Measurement Database Update Ext",
                               subtitle="",
                               datetime="2024 Jan 15  07:15:35.638", packet_text=
                               '''2024 Jan 15  07:15:35.638  [AD]  0xB97F  NR5G ML1 Searcher Measurement Database Update Ext
Subscription ID = 1
Misc ID         = 0
Major.Minor Version = 2. 9
System Time
   Slot Number = 1
   SubFrame Number = 1
   System Frame Number = 124
   SCS = 30KHZ
Num Layers = 1
SSB Periodicity Serv Cell = MS20
Frequency Offset = 2.029 PPM
Timing Offset = 4294967288
Component Carrier List[0]
   Raster ARFCN = 660768
   CC_ID = 0
   Num Cells = 3
   Serving Cell PCI = 700
   Serving Cell Index = 0
   Serving SSB = 0
   ServingRSRP Rx23[0]
      ServingRSRP_Rx23 = -110.21 dBm
   ServingRSRP Rx23[1]
      ServingRSRP_Rx23 = -107.13 dBm
   Serving RX Beam = { NA, NA }
   Serving RFIC ID = NA
   ServingSubarrayId[0] {
      SubArray ID = NA
   }
   ServingSubarrayId[1] {
      SubArray ID = NA
   }
   Cells
      ---------------------------------------------------------------------------------------------------------------------------------
      |   |      |      |     |            |            |Detected Beams                                                               |
      |   |      |      |     |            |            |     |RX Beam Info       |NR2NR       |NR2NR       |L2NR        |L2NR        |
      |   |      |PBCH  |Num  |Cell Quality|Cell Quality|SSB  |RX Beam |          |Filtered Tx |Filtered Tx |Filtered Tx |Filtered Tx |
      |#  |PCI   |SFN   |Beams|RSRP        |RSRQ        |Index|Id      |RSRP      |Beam RSRP L3|Beam RSRQ L3|Beam RSRP L3|Beam RSRQ L3|
      ---------------------------------------------------------------------------------------------------------------------------------
      |  0|   700|   124|    4|     -101.60|      -10.28|    0|       0|   -101.80|     -101.60|      -10.28|     -102.82|      -10.47|
      |   |      |      |     |            |            |     |       0|   -104.56|            |            |            |            |
      |   |      |      |     |            |            |    2|       0|   -113.08|     -113.06|      -11.00|     -115.18|      -12.17|
      |   |      |      |     |            |            |     |       0|   -117.18|            |            |            |            |
      |   |      |      |     |            |            |    1|       0|   -113.91|     -113.83|      -11.18|     -114.23|      -12.16|
      |   |      |      |     |            |            |     |       0|   -115.80|            |            |            |            |
      |   |      |      |     |            |            |    3|       0|   -118.43|     -118.55|      -12.88|     -119.73|      -14.20|
      |   |      |      |     |            |            |     |       0|   -120.80|            |            |            |            |
      |  1|   132|   434|    1|     -126.12|      -17.87|    3|       0|   -156.00|     -124.90|      -17.41|     -124.14|      -18.34|
      |   |      |      |     |            |            |     |       0|   -124.68|            |            |            |            |
      |  2|   523|   638|    1|     -128.73|      -20.66|    4|       0|   -129.45|     -128.90|      -20.55|          NA|          NA|
      |   |      |      |     |            |            |     |       0|   -156.00|            |            |            |            |
        ''')
        messages.append(msg)

        msg = ParsedRawMessage(index=0, packet_type="0xB801", packet_length=100,
                               name="NR5G NAS SM5G Plain OTA Outgoing Msg",
                               subtitle="PDU session release req",
                               datetime="2023 Nov 17  02:21:34.390", packet_text=
                               '''2023 Nov 17  02:21:34.390  [37]  0xB801  NR5G NAS SM5G Plain OTA Outgoing Msg  --  PDU session release req
Subscription ID = 1
Misc ID         = 0
pkt_version = 1 (0x1)
rel_number = 15 (0xf)
rel_version_major = 4 (0x4)
rel_version_minor = 0 (0x0)
prot_disc_type = 14 (0xe)
ext_protocol_disc = 46 (0x2e)
pdu_session_id = 2 (0x2)
proc_trans_id = 135 (0x87)
msg_type = 209 (0xd1) (PDU session release request)
nr5g_smm_msg
  pdu_session_rel_req
    _5gsm_cause_incl = 1 (0x1)
    _5gsm_cause
      cause = 36 (0x24) (Regular deactivation)
    ext_prot_config_incl = 0 (0x0)
        ''')
        messages.append(msg)

        msg = ParsedRawMessage(index=0, packet_type="0xB80A", packet_length=100,
                               name="NR5G NAS MM5G Plain OTA Incoming Msg",
                               subtitle="Security mode command",
                               datetime="2024 Jan 15  07:17:09.243",
                               packet_text=
                               '''2024 Jan 15  07:17:09.243  [3B]  0xB80A  NR5G NAS MM5G Plain OTA Incoming Msg  --  Security mode command
Subscription ID = 1
Misc ID         = 0
pkt_version = 1 (0x1)
rel_number = 15 (0xf)
rel_version_major = 4 (0x4)
rel_version_minor = 0 (0x0)
prot_disc_type = 14 (0xe)
ext_protocol_disc = 126 (0x7e)
security_header = 0 (0x0)
msg_type = 93 (0x5d) (Security mode command)
nr5g_mm_msg
  security_mode_cmd
    nas_security_algo
      ciphering_algorithm = 3 (0x3) (128-5G-EA3)
      integ_protection_algorithm = 3 (0x3) (128-5G-IA3)
    ngKSI
      tsc = 1 (0x1) (mapped sec context)
      nas_key_set_id = 1 (0x1)
    replayed_ue_sec_cap
      _5G_EA0 = 1 (0x1)
      _5G_EA1_128 = 1 (0x1)
      _5G_EA2_128 = 1 (0x1)
      _5G_EA3_128 = 1 (0x1)
      _5G_EA4 = 0 (0x0)
      _5G_EA5 = 0 (0x0)
      _5G_EA6 = 0 (0x0)
      _5G_EA7 = 0 (0x0)
      _5G_IA0 = 0 (0x0)
      _5G_IA1_128 = 1 (0x1)
      _5G_IA2_128 = 1 (0x1)
      _5G_IA3_128 = 1 (0x1)
      _5G_IA4 = 0 (0x0)
      _5G_IA5 = 0 (0x0)
      _5G_IA6 = 0 (0x0)
      _5G_IA7 = 0 (0x0)
      oct5_incl = 1 (0x1)
      EEA0 = 1 (0x1)
      EEA1_128 = 1 (0x1)
      EEA2_128 = 1 (0x1)
      EEA3_128 = 1 (0x1)
      EEA4 = 0 (0x0)
      EEA5 = 0 (0x0)
      EEA6 = 0 (0x0)
      EEA7 = 0 (0x0)
      oct6_incl = 1 (0x1)
      EIA0 = 0 (0x0)
      EIA1_128 = 1 (0x1)
      EIA2_128 = 1 (0x1)
      EIA3_128 = 1 (0x1)
      EIA4 = 0 (0x0)
      EIA5 = 0 (0x0)
      EIA6 = 0 (0x0)
      EIA7 = 0 (0x0)
    imeisv_req_incl = 1 (0x1)
    meisv_req
      imeisv_req_val = 1 (0x1)
    eps_nas_sec_algo_incl = 1 (0x1)
    nas_sec_algo
      cipher_algorithm = 2 (0x2) (128-EEA2)
      inte_prot_algorithm = 2 (0x2) (128-EIA2)
    add_5g_security_info_incl = 1 (0x1)
    add_5g_security_info
      length = 1 (0x1)
      RINMR = 1 (0x1)
      HDP = 0 (0x0)
    eap_msg_incl = 0 (0x0)
    nr5g_abba_type_incl = 0 (0x0)
    replayed_ue_sec_cap_incl = 1 (0x1)
    replayed_s1_ue_sec_cap
      EEA0 = 1 (0x1)
      EEA1_128 = 1 (0x1)
      EEA2_128 = 1 (0x1)
      EEA3_128 = 1 (0x1)
      EEA4 = 0 (0x0)
      EEA5 = 0 (0x0)
      EEA6 = 0 (0x0)
      EEA7 = 0 (0x0)
      EIA0 = 0 (0x0)
      EIA1_128 = 1 (0x1)
      EIA2_128 = 1 (0x1)
      EIA3_128 = 1 (0x1)
      EIA4 = 0 (0x0)
      EIA5 = 0 (0x0)
      EIA6 = 0 (0x0)
      EIA7 = 0 (0x0)
      oct5_incl = 1 (0x1)
      UEA0 = 1 (0x1)
      UEA1 = 1 (0x1)
      UEA2 = 0 (0x0)
      UEA3 = 0 (0x0)
      UEA4 = 0 (0x0)
      UEA5 = 0 (0x0)
      UEA6 = 0 (0x0)
      UEA7 = 0 (0x0)
      oct6_incl = 1 (0x1)
      UIA1 = 1 (0x1)
      UIA2 = 0 (0x0)
      UIA3 = 0 (0x0)
      UIA4 = 0 (0x0)
      UIA5 = 0 (0x0)
      UIA6 = 0 (0x0)
      UIA7 = 0 (0x0)
      oct7_incl = 0 (0x0)
      ''')
        messages.append(msg)
        msg = ParsedRawMessage(index=0, packet_type="0xB8A7", packet_length=100,
                               name="NR5G MAC CSF Report",
                               subtitle="", datetime="2024 Jan 15  07:15:37.648", packet_text=
                               '''2024 Jan 15  07:15:37.648  [6A]  0xB8A7  NR5G MAC CSF Report
Subscription ID = 1
Misc ID         = 0
Major.Minor = 3. 5
Num Records = 1
Records[0]
   Timestamp
      Slot = 14
      Numerology = 30kHz
      Frame = 324
   Num CSF Reports = 2
   Num CSF Type2 Reports = 0
   Num CSF Enh Type2 Reports = 0
   Reports
      -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
      |   |       |        |      |          |                                 |    |     |    |    |Num |Num |       |       |       |       |       |                                                                                                                                   |
      |   |       |        |      |          |                                 |    |     |    |Num |CSI |CSI |       |       |       |       |       |Quantities                                                                                                                         |
      |   |       |        |      |          |                                 |    |     |    |CSI |P2  |P2  |       |       |       |       |       |CSI                                                                                  |RSRP                                         |
      |   |       |        |      |          |                                 |    |     |Num |P2  |SB  |SB  |       |       |       |P2 SB  |P2 SB  |Metrics                                           |Bit Width                         |        |CRI  |     |Diff |       |    |     |
      |   |       |Resource|      |          |                                 |    |     |CSI |WB  |Even|Odd |       |       |       |Odd    |Even   |   |  |   |        |        |  |   |SB Result     |   |  |       |   |PMI |PMI|  |PMI|        |SSBRI|RSRP |RSRP |       |    |     |
      |   |Carrier|Carrier |Report|Report    |                                 |Late|Faked|P1  |Bits|Bits|Bits|Report |P1     |P2 WB  |Report |Report |   |  |WB |PMI WB  |PMI WB  |  |Num|   |SB|SB |SB |   |  |Zero   |WB |WB  |WB |  |SB |Resource|Bit  |Bit  |Bit  |Num    |    |SSBRI|
      |#  |ID     |ID      |ID    |Type      |Report Quantity Bitmask          |CSF |CSF  |Bits|Grp0|Grp1|Grp2|Dropped|Dropped|Dropped|Dropped|Dropped|CRI|RI|CQI|X1      |X2      |LI|SB |#  |ID|CQI|PMI|CRI|RI|Padding|CQI|X1  |X2 |LI|X2 |Set ID  |Width|Width|Width|Results|RSRP|CRI  |
      -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
      |  0|      0|       0|     2|  PERIODIC|                     RSRP:SSB_IDX|   0|    0|  17|   0|   0|   0|      0|      0|      0|      0|      0|   |  |   |        |        |  |   |   |  |   |   |   |  |       |   |    |   |  |   |       0|    3|    7|    4|      2|  55|    0|
      |   |       |        |      |          |                                 |    |     |    |    |    |    |       |       |       |       |       |   |  |   |        |        |  |   |   |  |   |   |   |  |       |   |    |   |  |   |        |     |     |     |       |   6|    2|
      |  1|      0|       0|     0|  PERIODIC|                CRI:RI:PMI:CQI:LI|   0|    0|  19|   0|   0|   0|      0|      0|      0|      0|      0|  0| 1| 11|      68|       1| 1|  0|  0| 0|  0|  0|  2| 2|      1|  4|   8|  1| 1|  0|        |     |     |     |       |    |     |
      |   |       |        |      |          |                                 |    |     |    |    |    |    |       |       |       |       |       |   |  |   |        |        |  |   |  1| 0|  0|  0|   |  |       |   |    |   |  |   |        |     |     |     |       |    |     |
      |   |       |        |      |          |                                 |    |     |    |    |    |    |       |       |       |       |       |   |  |   |        |        |  |   |  2| 0|  0|  0|   |  |       |   |    |   |  |   |        |     |     |     |       |    |     |
      |   |       |        |      |          |                                 |    |     |    |    |    |    |       |       |       |       |       |   |  |   |        |        |  |   |  3| 0|  0|  0|   |  |       |   |    |   |  |   |        |     |     |     |       |    |     |
      |   |       |        |      |          |                                 |    |     |    |    |    |    |       |       |       |       |       |   |  |   |        |        |  |   |  4| 0|  0|  0|   |  |       |   |    |   |  |   |        |     |     |     |       |    |     |
      |   |       |        |      |          |                                 |    |     |    |    |    |    |       |       |       |       |       |   |  |   |        |        |  |   |  5| 0|  0|  0|   |  |       |   |    |   |  |   |        |     |     |     |       |    |     |
      |   |       |        |      |          |                                 |    |     |    |    |    |    |       |       |       |       |       |   |  |   |        |        |  |   |  6| 0|  0|  0|   |  |       |   |    |   |  |   |        |     |     |     |       |    |     |
      |   |       |        |      |          |                                 |    |     |    |    |    |    |       |       |       |       |       |   |  |   |        |        |  |   |  7| 0|  0|  0|   |  |       |   |    |   |  |   |        |     |     |     |       |    |     |
      |   |       |        |      |          |                                 |    |     |    |    |    |    |       |       |       |       |       |   |  |   |        |        |  |   |  8| 0|  0|  0|   |  |       |   |    |   |  |   |        |     |     |     |       |    |     |
      |   |       |        |      |          |                                 |    |     |    |    |    |    |       |       |       |       |       |   |  |   |        |        |  |   |  9| 0|  0|  0|   |  |       |   |    |   |  |   |        |     |     |     |       |    |     |
      |   |       |        |      |          |                                 |    |     |    |    |    |    |       |       |       |       |       |   |  |   |        |        |  |   | 10| 0|  0|  0|   |  |       |   |    |   |  |   |        |     |     |     |       |    |     |
      |   |       |        |      |          |                                 |    |     |    |    |    |    |       |       |       |       |       |   |  |   |        |        |  |   | 11| 0|  0|  0|   |  |       |   |    |   |  |   |        |     |     |     |       |    |     |
      |   |       |        |      |          |                                 |    |     |    |    |    |    |       |       |       |       |       |   |  |   |        |        |  |   | 12| 0|  0|  0|   |  |       |   |    |   |  |   |        |     |     |     |       |    |     |
      |   |       |        |      |          |                                 |    |     |    |    |    |    |       |       |       |       |       |   |  |   |        |        |  |   | 13| 0|  0|  0|   |  |       |   |    |   |  |   |        |     |     |     |       |    |     |
      |   |       |        |      |          |                                 |    |     |    |    |    |    |       |       |       |       |       |   |  |   |        |        |  |   | 14| 0|  0|  0|   |  |       |   |    |   |  |   |        |     |     |     |       |    |     |
      |   |       |        |      |          |                                 |    |     |    |    |    |    |       |       |       |       |       |   |  |   |        |        |  |   | 15| 0|  0|  0|   |  |       |   |    |   |  |   |        |     |     |     |       |    |     |
      |   |       |        |      |          |                                 |    |     |    |    |    |    |       |       |       |       |       |   |  |   |        |        |  |   | 16| 0|  0|  0|   |  |       |   |    |   |  |   |        |     |     |     |       |    |     |
      |   |       |        |      |          |                                 |    |     |    |    |    |    |       |       |       |       |       |   |  |   |        |        |  |   | 17| 0|  0|  0|   |  |       |   |    |   |  |   |        |     |     |     |       |    |     |
      |   |       |        |      |          |                                 |    |     |    |    |    |    |       |       |       |       |       |   |  |   |        |        |  |   | 18| 0|  0|  0|   |  |       |   |    |   |  |   |        |     |     |     |       |    |     |
                               ''')
        messages.append(msg)

        msg = ParsedRawMessage(index=0, packet_type="0xB827", packet_length=100,
                               name="NR5G RRC OTA Packet",
                               subtitle="", datetime="2024 Jan 15  07:18:06.766", packet_text=
                               '''2024 Jan 15  07:18:06.766  [93]  0xB827  NR5G RRC PLMN Search Request
Subscription ID = 1
Misc ID         = 0
Version = 4
PLMN Search Request
   Source RAT = LTE
   Network Select Mode = AUTOMATIC
   Search Type = NONE
   Scan Scope = FULL BAND
   Guard Timer = 876 ms
   Num RATs = 1
   RAT List
      --------------------------------------------------------------------------------------------------------------------------------------------------------------------
      |#  |RAT   |Band Cap          |Band Cap 65_128   |Band Cap 129_192  |Band Cap 193_256  |Band Cap 257_320  |Band Cap 321_384  |Band Cap 385_448  |Band Cap 449_512  |
      --------------------------------------------------------------------------------------------------------------------------------------------------------------------
      |  0|  NR5G|0x000001203B082817|0x0000000000000062|0x0000000000000000|0x0000000000000000|0x0000000000000000|0x0000000000000000|0x0000000000000000|0x0000000000000000|

   NR5G Arfcn Counts = 0
   Num PLMNs = 1
   PLMN List
      ------------------------------
      |   |      |Plmn |Plmn |Plmn |
      |#  |RAT   |byte0|byte1|byte2|
      ------------------------------
      |  0|  NR5G| 0x13| 0x03| 0x43|
                               ''')
        messages.append(msg)
        msg = ParsedRawMessage(index=0, packet_type="0xB18F", packet_length=100,
                               name="LTE ML1 AdvRx IC Cell List",
                               subtitle="", datetime="2024 Jan 15  07:15:35.679", packet_text=
                               '''2024 Jan 15  07:15:35.679  [A3]  0xB18F  LTE ML1 AdvRx IC Cell List
Subscription ID = 1
Version = 54
Carrier Index = PCC
Earfcn = 66986
Num Neighbors = 1
Panic Escape Mask = 0x0000
Valid Sched Rate = 1
Is Carrier Cfg FW = 0
SubFn = 1283
TM Mode = 4
Serving
   -------------------------------------------------------------------------------
   |   |      |         |        |          |RSRP  |IC INR|                      |
   |   |Cell  |DL       |Num     |Filt RSRP |SS    |SS    |                      |
   |#  |ID    |Bandwidth|Antennas|(dB)      |Buffer|Buffer|Cell Type             |
   -------------------------------------------------------------------------------
   |  0|   147|       50|       4|    -92.25|    WB|    WB|          CELL_SERVING|

Neighbors
   -------------------------------------------------------------------------------
   |   |      |         |        |          |RSRP  |IC INR|                      |
   |   |Cell  |DL       |Num     |Filt RSRP |SS    |SS    |                      |
   |#  |ID    |Bandwidth|Antennas|(dB)      |Buffer|Buffer|Cell Type             |
   -------------------------------------------------------------------------------
   |  0|   295|       50|       4|   -104.00|    NB|    NB|   CELL_NOT_IN_IC_LIST|
                               ''')
        messages.append(msg)
        msg = ParsedRawMessage(index=0, packet_type="0xB821", packet_length=100,
                               name="NR5G RRC OTA Packet",
                               subtitle="UL_CCCH / RRC Setup Req", datetime="2024 Jan 15  07:17:09.075", packet_text=
                               '''2024 Jan 15  07:17:09.075  [4F]  0xB821  NR5G RRC OTA Packet  --  UL_CCCH / RRC Setup Req
Subscription ID = 1
Misc ID         = 0
Pkt Version = 17
RRC Release Number.Major.minor = 16.6.0
Radio Bearer ID = 0, Physical Cell ID = 354
NR Cell Global ID = 85569785951386673
Freq = 174770
Sfn = N/A, SubFrameNum = N/A
slot = 0
PDU Number = UL_CCCH Message,    Msg Length = 6
SIB Mask in SI =  0x00

Interpreted PDU:

value UL-CCCH-Message ::= 
{
message c1 : rrcSetupRequest : 
  {
    rrcSetupRequest 
    {
      ue-Identity randomValue : '11100001 01010110 11011001 11001000 0111011'B,
      establishmentCause mo-Signalling,
      spare '0'B
    }
  }
}
                               ''')
        messages.append(msg)

        msg = ParsedRawMessage(index=0, packet_type="0xB0C0", packet_length=100, name="LTE RRC OTA Packet",
                               subtitle="BCCH_DL_SCH / SystemInformationBlockType1",
                               datetime="2024 Jan 15  07:17:09.664", packet_text=
                               '''
        2024 Jan 15  07:17:09.664  [37]  0xB0C0  LTE RRC OTA Packet  --  BCCH_DL_SCH / SystemInformationBlockType1
Subscription ID = 1
Pkt Version = 27
RRC Release Number.Major.minor = 16.1.0
NR RRC Release Number.Major.minor = 16.6.0
Radio Bearer ID = 0, Physical Cell ID = 147
Freq = 5780
SysFrameNum = 310, SubFrameNum = 5
PDU Number = BCCH_DL_SCH Message,    Msg Length = 37
SIB Mask in SI =  0x02

Interpreted PDU:

value BCCH-DL-SCH-Message ::= 
{
  message c1 : systemInformationBlockType1 : 
      {
        cellAccessRelatedInfo 
        {
          plmn-IdentityList 
          {
            {
              plmn-Identity 
              {
                mcc 
                {
                  3,
                  1,
                  0
                },
                mnc 
                {
                  4,
                  1,
                  0
                }
              },
              cellReservedForOperatorUse notReserved
            },
            {
              plmn-Identity 
              {
                mcc 
                {
                  3,
                  1,
                  3
                },
                mnc 
                {
                  1,
                  0,
                  0
                }
              },
              cellReservedForOperatorUse notReserved
            }
          },
          trackingAreaCode '10010001 00001101'B,
          cellIdentity '01100111 10111011 11110000 1111'B,
          cellBarred notBarred,
          intraFreqReselection allowed,
          csg-Indication FALSE
        },
        cellSelectionInfo 
        {
          q-RxLevMin -65
        },
        p-Max 23,
        freqBandIndicator 17,
        schedulingInfoList 
        {
          {
            si-Periodicity rf16,
            sib-MappingInfo 
            {
            }
          },
          {
            si-Periodicity rf16,
            sib-MappingInfo 
            {
              sibType3
            }
          },
          {
            si-Periodicity rf64,
            sib-MappingInfo 
            {
              sibType5
            }
          }
        },
        si-WindowLength ms20,
        systemInfoValueTag 12,
        nonCriticalExtension 
        {
          lateNonCriticalExtension 
            CONTAINING
            {
              multiBandInfoList 
              {
                12
              },
              nonCriticalExtension 
              {
                nonCriticalExtension 
                {
                  nonCriticalExtension 
                  {
                    nonCriticalExtension 
                    {
                      nonCriticalExtension 
                      {
                        schedulingInfoListExt-r12 
                        {
                          {
                            si-Periodicity-r12 rf32,
                            sib-MappingInfo-r12 
                            {
                              sibType24-v1530
                            }
                          }
                        }
                      }
                    }
                  }
                }
              }
            },
          nonCriticalExtension 
          {
            ims-EmergencySupport-r9 true,
            nonCriticalExtension 
            {
              nonCriticalExtension 
              {
                cellAccessRelatedInfo-v1250 
                {
                },
                nonCriticalExtension 
                {
                  hyperSFN-r13 '10011110 11'B,
                  eDRX-Allowed-r13 true
                }
              }
            }
          }
        }
      }
}
        ''')

        messages.append(msg)
        msg = ParsedRawMessage(index=0, packet_type="0xB113", packet_length=100,
                               name="LTE LL1 PSS Results",
                               subtitle="", datetime="2024 Jan 15  07:14:07.642", packet_text=
                               """
                               2024 Jan 15  07:14:07.642  [E1]  0xB113  LTE LL1 PSS Results
Subscription ID = 1
Version = 181
Number of Half Frames = 1
Sub-frame Number = 9
System Frame Number = 539
Number of PSS Records = 10
Srch_type = LTE_LL1_SRCH_NCELL
Nb Id = 0
Earfcn = 66986
PSS Records
   -------------------------------
   |   |PSS    |        |        |
   |   |Peak   |        |        |
   |   |Value  |Peak    |PSS     |
   |#  |(dB)   |Position|Indicies|
   -------------------------------
   |  0| 17.114|    5192|       0|
   |  1| 15.764|    5190|       0|
   |  2| 15.594|    5193|       0|
   |  3| 11.994|    5191|       0|
   |  4| 11.291|    5189|       0|
   |  5|  8.494|    6272|       2|
   |  6|  8.237|    6273|       2|
   |  7|  7.926|    8242|       0|
   |  8|  7.620|    5270|       0|
   |  9|  7.214|    5321|       1|
                               """)
        messages.append(msg)
        msg = ParsedRawMessage(index=0, packet_type="0xB171", packet_length=100,
                               name="0xB171  LTE SRS Power Control Report",
                               subtitle="",
                               datetime="2024 Jan 15  07:17:09.664", packet_text=
                               '''
 2024 Jan 19  21:46:06.512  [5C]  0xB171  LTE SRS Power Control Report
Subscription ID = 1
Version = 24
Number of Records = 14
Report
   -------------------------------------------------------
   |   |     |    |      |SRS  |    |     |       |SRS   |
   |   |     |    |      |Tx   |    |     |TPC    |Actual|
   |   |Cell |    |      |Power|Path|     |Command|Tx    |
   |#  |Index|SFN |Sub-fn|(dBm)|Loss|M_SRS|(f(i)) |Power |
   -------------------------------------------------------
   |  0|    0| 818|     5|   18| 105|    4|      5|    18|
   |  1|    0| 819|     5|   18| 105|    4|      5|    18|
   |  2|    0| 820|     5|   17| 105|    4|      4|    17|
   |  3|    0| 821|     5|   17| 105|    4|      4|    17|
   |  4|    0| 822|     5|   17| 105|    4|      4|    17|
   |  5|    0| 823|     5|   17| 105|    4|      4|    17|
   |  6|    0| 824|     5|   17| 105|    4|      4|    17|
   |  7|    0| 825|     5|   17| 105|    4|      4|    17|
   |  8|    0| 826|     5|   17| 105|    4|      4|    17|
   |  9|    0| 827|     5|   17| 105|    4|      4|    17|
   | 10|    0| 828|     5|   17| 105|    4|      4|    17|
   | 11|    0| 829|     5|   17| 105|    4|      4|    17|
   | 12|    0| 830|     5|   17| 105|    4|      4|    17|
   | 13|    0| 831|     5|   17| 105|    4|      4|    17|
        ''')
        messages.append(msg)
        msg = ParsedRawMessage(index=0, packet_type="0xB18E", packet_length=100,
                               name="LTE ML1 System Scan Results",
                               subtitle="", datetime="2024 Jan 19  21:46:03.747", packet_text=
                               """2024 Jan 19  21:46:03.747  [14]  0xB18E  LTE ML1 System Scan Results
Subscription ID = 1
Version = 41
Use Init Search = 0
Num Candidates = 10
Candidates
   ------------------------------------------------------------
   |   |      |    |         |Energy      |NB_Energy   |      |
   |#  |EARFCN|Band|Bandwidth|(dBm/100KHz)|(dBm/100KHz)|Pruned|
   ------------------------------------------------------------
   |  0| 68661|  71|    5 MHz|         -73|           0|     0|
   |  1|  5230|  13|   10 MHz|         -78|           0|     0|
   |  2|  5780|  17|   10 MHz|         -80|           0|     0|
   |  3|  5330|  14|   10 MHz|         -82|           0|     0|
   |  4| 66986|  66|   10 MHz|         -88|           0|     0|
   |  5|   700|   2|   20 MHz|         -89|           0|     0|
   |  6|   975|   2|   15 MHz|         -93|           0|     0|
   |  7|  9820|  30|   10 MHz|        -101|           0|     0|
   |  8| 66736|  66|   20 MHz|        -103|           0|     0|
   |  9| 40072|  41|   20 MHz|        -118|           0|     0|

""")
        messages.append(msg)
        msg = ParsedRawMessage(index=0, packet_type="0xB196", packet_length=100,
                               name="LTE ML1 Cell Measurement Results",
                               subtitle="", datetime="2024 Jan 19  21:46:04.483", packet_text=
                               """
2024 Jan 19  21:46:04.483  [84]  0xB196  LTE ML1 Cell Measurement Results
Subscription ID = 1
Version = 41
Num Cells = 2
Is 1Rx Mode = 0
Cell Measurement List
   ------------------------------------------------------------------------------
   |   |       |        |       |Inst   |Inst   |Inst   |Inst   |Inst   |Inst   |
   |   |       |        |       |RSRP   |RSRP   |RSRQ   |RSRQ   |RSSI   |RSSI   |
   |   |       |Physical|Valid  |Rx[0]  |Rx[1]  |Rx[0]  |Rx[1]  |Rx[0]  |Rx[1]  |
   |#  |E-ARFCN|Cell ID |Rx     |(dBm)  |(dBm)  |(dBm)  |(dBm)  |(dBm)  |(dBm)  |
   ------------------------------------------------------------------------------
   |  0|   5780|     147|RX0_RX1| -84.50| -82.31| -11.44| -11.50| -56.13| -53.81|
   |  1|   5780|     295|RX0_RX1|-102.31| -97.00| -26.44| -23.50| -68.13| -65.75|
                               """)
        messages.append(msg)
        msg = ParsedRawMessage(index=0, packet_type="0xB883", packet_length=100,
                               name="NR5G MAC UL Physical Channel Schedule Report",
                               subtitle="", datetime="2024 Jan 15  07:15:47.888", packet_text=
                               """
2024 Jan 15  07:15:47.888  [D4]  0xB883  NR5G MAC UL Physical Channel Schedule Report
Subscription ID = 1
Misc ID         = 0
Major.Minor Version = 3. 17
Num Records = 1
Records
   --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
   |   |                   |       |Carriers                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        |
   |   |                   |       |       |                |                 |                                                                                                                                                                                                                                                                                                                                                                                     |PUCCH Data                                                                                                                                                                         |                                                                                             |                                             |
   |   |                   |       |       |                |                 |PUSCH Data                                                                                                                                                                                                                                                                                                                                                                           |     |Per PUCCH Data                                                                                                                                                               |SRS Data                                                                                     |                                             |
   |   |                   |       |       |                |                 |               |     |    |     |   |        |     |      |   |      |       |      |                                  |                  |                |       |    |       |      |          |    |        |        |    |     |    |    |     |      |          |     |      |      |Num |Num |Num |   |     |          |         |     |     |     |     |   |            |   |     |                  |                                  |      |       |        |     |      |   |                        |      |Num |    |Num |Num |  |     |    |      |     |   |Per SRS Data                                                                             |PRACH Data                                   |
   |   |                   |       |       |                |                 |               |L2   |    |     |   |        |     |      |   |      |       |TX    |                                  |                  |                |DMRS   |Freq|       |DMRS  |Data      |    |        |        |DMRS|     |    |    |RB   |      |DMRS      |DMRS |Dual  |Beta  |HARQ|CSF |CSF |SRS|REL16|          |         |Code |     |K    |     |   |            |Num|     |                  |                                  |      |       |        |REL16|Dual  |   |                        |      |HARQ|Num |UCI |UCI |  |Time |    |DFT   |DFT  |   |        |        |                       |      |     |        |       |    |Dual  |     |          |ZC  |        |      |ZC    |Dual  |
   |   |System Time        |Num    |Carrier|                |                 |               |new  |HARQ|RV   |   |        |RB   |Num   |BWP|Start |Num    |Slot  |                                  |                  |                |Symbol |Hop |Mapping|Config|Scrambling|PTRS|DMRS    |DMRS    |Add |RNTI |    |RA  |Start|CDM   |Scrambling|PTRS |Pol   |Offset|ACK |P1  |P2  |Res|DMRS |Modulation|Transform|Rate |CB   |Prime|ZC   |Num|            |Gap|Num  |                  |                                  |Start |Num    |Starting|DMRS |Pol   |Num|                        |Second|ACK |SR  |P1  |P2  |  |OCC  |I   |OCC   |OCC  |Num|Resource|Resource|                       |Config|Num  |Starting|Num    |Num |Pol   |Re   |Resource  |Root|Preamble|Symbol|Cyclic|Pol   |
   |#  |Slot|SCS    |Frame |Carrier|ID     |RNTI Type       |Phychan Bit Mask |TX Type        |TB   |ID  |Index|MCS|TX Mode |Start|RBs   |Id |Symbol|Symbols|Offset|UCI Request Mask                  |MCS Table         |TB Size (bytes) |Bitmask|Flag|Type   |Type  |Selection |EN  |Ports[0]|Ports[1]|Pos |Value|TPMI|Type|Hop  |Groups|Selection |Assoc|Status|Ind   |Bits|Bits|Bits|Ind|EN   |Order     |Precoding|(Q11)|Size |Value|Value|CBs|RBG Bitmap  |RBs|PUCCH|PUCCH Format      |UCI Request BMask                 |symbol|Symbols|RB      |EN   |Status|RB |Freq Hopping Flag       |Hop RB|Bits|Bits|Bits|Bits|M0|Index|DMRS|Length|Index|SRS|Set Id  |Id      |Res Config Type        |Index |Ports|Symbol  |Symbols|Hops|Status|start|Allocation|Seq |Format  |Offset|Shift |Status|
   --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
   |  0|  14|  30KHZ|   324|      1|      0|          C_RNTI|            PUCCH|               |     |    |     |   |        |     |      |   |      |       |      |                                  |                  |                |       |    |       |      |          |    |        |        |    |     |    |    |     |      |          |     |      |      |    |    |    |   |     |          |         |     |     |     |     |   |            |   |    1|   PUCCH_FORMAT_F3|                    CSI_RPT:SR_RPT|     0|     14|      20|    0|     0|  2|           HOP_MOD_GROUP|    22|   0|   1|  37|   0| 0|    0|   0|     0|    0|   |        |        |                       |      |     |        |       |    |      |     |          |    |        |      |      |      |

                               """)
        messages.append(msg)
        msg = ParsedRawMessage(index=0, packet_type="0xB884", packet_length=100,
                               name="NR5G MAC UL Physical Channel Power Control",
                               subtitle="", datetime="2024 Jan 15  07:17:09.284", packet_text=
                               """
2024 Jan 15  07:17:09.284  [2E]  0xB884  NR5G MAC UL Physical Channel Power Control
Subscription ID = 1
Misc ID         = 0
Major.Minor Version = 3. 3
Num Records = 1
Records
   -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
   |   |      |      |      |        |          |Carriers                                                                                                                                                                                                                |
   |   |      |      |      |        |          |        |Power Params                                                                                                                                                                                                   |
   |   |      |      |      |        |          |        |       |       |        |        |          |    |        |         |    |    |     |      |    |        |        |       |PRACH         |                |PUSCH                    |PUCCH                     |
   |   |      |      |      |        |          |        |       |       |        |        |          |    |        |         |    |    |     |      |    |        |        |       |       |PRACH |SRS             |     |     |Num   |      |     |      |Num   |      |
   |   |      |      |System|        |Timing    |        |       |       |Transmit|        |TPC       |PHR |        |Antenna  |TX  |Use |Use  |      |    |Spatial |Spatial |Minimum|       |Target|         |Rampup|Delta|     |Symbol|Rampup|Delta|      |Symbol|Rampup|
   |   |Slot  |      |Frame |Num     |Reference |Num     |Carrier|Channel|Power   |Pathloss|Adjustment|MTPL|Channel |Switch   |Port|Pmin|PRACH|Start |Num |Relation|Relation|Power  |RACH   |Power |SRS      |Power |TF   |RAR  |First |Power |TF   |PUCCH |First |Power |
   |#  |Number|SCS   |Number|Carriers|Number    |Channels|ID     |Type   |(dB)    |(dB)    |(dB)      |(dB)|Priority|Indicator|Mask|Beam|Beam |Symbol|Hops|Type    |Info    |(dB)   |Attempt|(dB)  |Bandwidth|(dB)  |(dB) |PUSCH|Hop   |(dB)  |(dB) |Format|Hop   |(dB)  |
   -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
   |  0|     4| 15KHZ|   272|       1|      2724|       1|      0|  PUSCH|    12.7|    98.0|       6.0|21.3|       5|        0| 0x1|   0|    0|     0|   0|       0|     127|  -44.0|       |      |         |      |  0.0|    0|    14|   0.0|     |      |      |      |

                       """)
        messages.append(msg)
        msg = ParsedRawMessage(index=0, packet_type="0xB889", packet_length=100,
                               name="NR5G MAC RACH Trigger",
                               subtitle="", datetime="2024 Jan 15  07:17:09.075", packet_text=
                               """
2024 Jan 15  07:17:09.075  [C6]  0xB889  NR5G MAC RACH Trigger
Subscription ID = 1
Misc ID         = 0
Major.Minor = 3. 9
RACH Trigger
   ------------------------------------------------------------------------------------------------------------------------------------------------------------
   |                   |      |                  |     |First |      |UL RACH|DL RACH|      |                    |               |          |    |Msg1 |PRACH |
   |System Time        |      |                  |     |Active|Active|Rsrc.  |Rsrc.  |Duplex|                    |               |          |Msg1|Freq |Config|
   |Frame|SubFrame|Slot|C-RNTI|Rach Reason       |CA ID|UL BWP|DL BWP|Present|Present|Mode  |Connection Type     |RACH Contention|Msg1 SCS  |FDM |Start|Index |
   ------------------------------------------------------------------------------------------------------------------------------------------------------------
   |  251|       8|   0|     0|CONNECTION_REQUEST|    0|     0|     0|      1|      1|   FDD|       CONNECTION_SA|    CONT_DL_MCE|   1.25KHZ|   1|    9|    13|

                       """)
        messages.append(msg)
        msg = ParsedRawMessage(index=0, packet_type="0x17F2", packet_length=100,
                               name="IMS Voice Call Statistics",
                               subtitle="", datetime="2024 Jan 15  07:14:46.813", packet_text=
                               """
2024 Jan 15  07:14:46.813  [E7]  0x17F2  IMS Voice Call Statistics
Subscription ID = 1
Version = 9
SipCallDur = 0
CodecType = AMR_WB
RTCP Voice Call Stat Params
   Tx Ssrc = 0xFDAD3D9E
   Rx Ssrc = 0x1954EBCE
   Num Tx Rtp = 0
   Num Rx Rtp = 5
   Num Rx Lost = 0
   Ave Rel Jitter = 0
   Max Rel Jitter = 0
   Avg Inst Jitter = 0
   Max Inst Jitter = 4
QDJ Voice Call Stat Params
   Num Frames Rcvd = 5
   Frames Not Enqued = 0
   Frames UnderFlow = 0
   Avg UnderFlow Rate = 0
   Avg Frame Delay = 67
   Max Frame Delay = 69
   Avg Q Size = 40
   Avg Target Delay = 40
   Frame Drop Count at JB = 0
Tx Rtp BitRate = 0
Rx Rtp BitRate = 0
TX RTP Payload = 0
RX RTP Payload = 257
MaxDelta = 4
MaxDelta Imax = 4
MaxDelta Imin = 5
Tx Payload Type = 104
Rx Payload Type = 104
IP Version = IPv4
Call State = ADSP_RESYNC
Extra Small Bin Count = 0
Small Bin Count = 0
Medium Bin Count = 0
Large Bin Count = 0
Audio Gap Ratio =                      0.00
RAT Type = LTE
                       """)
        messages.append(msg)
        msg = ParsedRawMessage(index=0, packet_type="0x1D4D", packet_length=100,
                               name="IMS CALL SUMMARY STATS",
                               subtitle="", datetime="2024 Jan 15  07:15:24.625", packet_text=
                               """
2024 Jan 15  07:15:24.625  [82]  0x1D4D  IMS CALL SUMMARY STATS
Subscription ID = 1
Version = 8
SubId = 1
CallStatusSummary {
   Common Call Stats
      Call ID = 20
      Call Status = 1
      CallTypeAtCallOrig = CALL_TYPE_VOICE
      CallTypeAtCallEnd = CALL_TYPE_VOICE
      IsTextEnabledinCall = 0
      IsVTEmergency = 0
      WasCallEverVT = 0
      wasCallEverRTT = 0
      Direction of Call = CALL_MO
      Disconnect Error Code = 200
      ClientEndCause = CLIENT_END_CAUSE_NONE
      CallEndCause = CALL_END_CAUSE_NORMAL
      WasCallConnected = 1
      IsCallEndedbyUser = 1
      IsCallEndedbyRemote = 0
      Redial Mask = REDIAL_MASK_NONE
      380EmergencySrvCategory = 0
      CallSetup Time = 6751 ms
      CallRingingRingback Time = 2046 ms
      CallRatatOrig = DCM_RAT_LTE
      CallRatatEnd = DCM_RAT_LTE
      IsConfCall = 0
      IsWPSCall = 0
      Encryption Status at Call orig = CALL_ENCRYPTION_DISABLED
      Encryption Status at Call End = CALL_ENCRYPTION_DISABLED
      MT Accepted Encryption Status = CALL_ENCRYPTION_DISABLED
      Call End Indication Supressed = 0
      Redial at IMS layer Call type = ORIGINATE_TYPE_NONE
      IsCallAutoRejected = 0
      AutoRejectReason = CALL_REJECT_NONE
      IsAnyCallonOtherSub = 0
      Call Information per Sub
         -------------------------------------------------------
         |#  |SubId|ActiveCallOnSub|HeldCallOnSub|E911CallonSub|
         -------------------------------------------------------
         |  0|    0|              1|            0|            0|
         |  1|    0|              0|            0|            0|

      ForkedDialogCount = 1
      EarlyMediaPlayed = 1
      Operator Mode = IR92
      SubOperator Mode = DISH
      MOUpgradesCount = 0
      MTUpgradesCount = 0
      MODowngradesCount = 0
      MTDowngradesCount = 0
      CallLocalHeldCount = 0
      CallRemoteHeldCount = 0
      CallLocalResumeCount = 0
      CallRemoteResumeCount = 0
      NoofDialogsEarlyMediaPlayed = 1
      DowngradeEventsCachedCount = 0
      LatestPDPStatus
         IPType = 1
         PCOValue = 0
         PDPId = 8
         PDPState = CONNECTIVITY_UP
         SourceRAT = DCM_RAT_NONE
         TargetRAT = DCM_RAT_NONE
         CurrentRAT = DCM_RAT_LTE
         ApnType = DCM_APN_IMS
         FailureCode = 0
      VerstatInfo
         isVerstat FT Valid = 0
         Verstat value for Call = CALL_TN_VALIDATION_NONE
         is UnwantedCallFT Valid = 0
         is UnwantedCall = 0
   RTP/RTCP Stats
      Media rtprtcp Stats
         ------------------------------------------------------------------------------------------------
         |   |     |                   |                    |          |          |RTP       |RTCP      |
         |   |     |                   |                    |          |          |Inactivty |Inactivty |
         |   |Media|TimeToOpenRTPStream|TimeToCloseRTPStream|no of RTP |no of RTCP|TimerValue|TimerValue|
         |#  |Type |(ms) (ms)          |(ms) (ms)           |Inactivity|Inactivity|(s)       |(s)       |
         ------------------------------------------------------------------------------------------------
         |  0|AUDIO|                  7|                  11|         0|         0|        20|        20|
         |  1|VIDEO|                  0|                   0|         0|         0|         0|         0|
         |  2| TEXT|                  0|                   0|         0|         0|         0|         0|

   CallEndDialog QOS Stats
      Pre conditionEnabled during Call Setup = 0
      Pre conditionEnabled Midcall = 0
      Dialog ID of Call ended = 57
      SRTP Enabled = 0
      KPI of QOS for media[0]
         QOS Enabled = 1
         Media Allowed on Default Bearer = 0
         Media Type = AUDIO
         Time to Establish Dedicated Bearer = 100 ms
         Time to Re Establish Dedicated Bearer = 0 ms
         Latest Qos Status = QOS_MODIFIED_AVAILABLE
         Mbr Status = MBR_MET_SUCCESS
         No of Times QosLost = 0
         No of Times QosReGranted = 0
         No of QOSEvents = 2
         QOS Event
            -------------------------------------------------------------------------------------------------------------------------------------------------------------------------
            |   |                      |                         |QOS Dir     |                           |                           |                                |Time Stamp  |
            |#  |QOS Message           |QOS Dir Matched          |Required    |Timer Started Mask         |Timer Stopped Mask         |QOSMBRMetStatus and Action      |of QOSEvent |
            -------------------------------------------------------------------------------------------------------------------------------------------------------------------------
            |  0|         QOS_AVAILABLE|QOS_FILTR_MATCH_DIR_BIDIR|DIR_SENDRECV|             QOS_TIMER_NONE|             QOS_TIMER_NONE|          MBR_MET_SUCCESS_UPDATE|  2063680152|
            |  1|QOS_MODIFIED_AVAILABLE|QOS_FILTR_MATCH_DIR_BIDIR|DIR_SENDRECV|             QOS_TIMER_NONE|             QOS_TIMER_NONE|                 MBR_MET_SUCCESS|  2063680152|

      KPI of QOS for media[1]
         QOS Enabled = 1
         Media Allowed on Default Bearer = 0
         Media Type = VIDEO
         Time to Establish Dedicated Bearer = 0 ms
         Time to Re Establish Dedicated Bearer = 0 ms
         Latest Qos Status = QOS_UNKNOWN
         Mbr Status = MBR_MET_NULL
         No of Times QosLost = 0
         No of Times QosReGranted = 0
         No of QOSEvents = 0
      KPI of QOS for media[2]
         QOS Enabled = 1
         Media Allowed on Default Bearer = 0
         Media Type = TEXT
         Time to Establish Dedicated Bearer = 0 ms
         Time to Re Establish Dedicated Bearer = 0 ms
         Latest Qos Status = QOS_UNKNOWN
         Mbr Status = MBR_MET_NULL
         No of Times QosLost = 0
         No of Times QosReGranted = 0
         No of QOSEvents = 0
   CodecStatsEnabled = 1
   Codec Stats
      LatestAudioCodec = AMR_WB
      LatestVideoCodec = 0
      LatestTextCodec = 0
      AudioCodecCachedCount = 3
      VideoCodecCachedCount = 0
      TextCodecCachedCount = 0
      AudioCodecInfo
         -----------
         |#  |Codec|
         -----------
         |  0|AMR_WB|
         |  1|AMR_WB|
         |  2|AMR_WB|

   E911StatsEnabled = 0
   HandoverStatsEnabled = 0
   EPSFBStatsEnabled = 0
   SRVCCStatsEnabled = 0
   CRBTStatsEnabled = 0
   CRSStatsEnabled = 0
   EarlyMediaStatsEnabled = 1
   EarlyMediaStatistics
      Dynamic Switch Enabled = 1
      EarlyMedia Auth State Count = 4
      Early Media
         ---------------
         |#  |Authstate|
         ---------------
         |  0|EARLY_MEDIA_STATE_ON|
         |  1|EARLY_MEDIA_STATE_SENDRECV|
         |  2|EARLY_MEDIA_STATE_SENDRECV|
         |  3|EARLY_MEDIA_STATE_NONE|

      EarlyMedia Method Count = 3
      Early Media Method
         ------------
         |#  |Method|
         ------------
         |  0|EARLY_MEDIA_METHOD_SIP_MESSAGE_RINGING|
         |  1|EARLY_MEDIA_METHOD_RTP_ACTIVE|
         |  2|EARLY_MEDIA_METHOD_SIP_MESSAGE_RINGING|

      EarlyMedia Indication Count = 3
      Early Media Indication
         ----------------
         |#  |indication|
         ----------------
         |  0|EARLY_MEDIA_ACTION_EARLY_MEDIA_IND|
         |  1|EARLY_MEDIA_ACTION_EARLY_MEDIA_IND|
         |  2|EARLY_MEDIA_ACTION_EARLY_MEDIA_IND|

   MultiTask Stats included = 0
}
                       """)
        messages.append(msg)
        msg = ParsedRawMessage(index=0, packet_type="0xB16F", packet_length=100,
                               name="LTE PUCCH Power Control",
                               subtitle="", datetime="2024 Jan 15  07:14:08.556", packet_text=
                               """
 2024 Jan 15  07:14:08.556  [E1]  0xB16F  LTE PUCCH Power Control
 Subscription ID = 1
 Version = 49
 Number of Records = 50
 Report
    -------------------------------------------------------------------------------------
    |   |    |      |              |        |    |           |   |    |    |PUCCH|PUCCH |
    |   |    |      |              |        |    |           |   |DL  |    |Tx   |Actual|
    |   |    |      |              |PUCCH   |N   |           |N  |Path|    |Power|Tx    |
    |#  |SFN |Sub-fn|DCI Format    |Format  |HARQ|TPC Command|CQI|Loss|g(i)|(dBm)|Power |
    -------------------------------------------------------------------------------------
    |  0| 597|     8|             2|      1b|   2|          0|  0| 111|   1|    1|     1|
    |  1| 599|     3|             2|      1b|   2|          0|  0| 111|   1|    1|     1|
    |  2| 599|     8|             2|      1b|   2|          0|  0| 111|   1|    1|     1|
    |  3| 599|     9|             2|      1a|   1|          0|  0| 111|   1|   -2|    -2|
    |  4| 600|     1|             2|      1a|   1|          0|  0| 111|   1|   -2|    -2|
    |  5| 600|     2|              |       1|   0|Not present|  0| 111|   1|   -2|    -2|
    |  6| 600|     4|              |       2|   0|Not present|  0| 111|   1|   -2|    -2|
    |  7| 600|     5|              |       2|   0|Not present|  0| 111|   1|   -2|    -2|
    |  8| 604|     2|              |       1|   0|Not present|  0| 110|   1|   -3|    -3|
    |  9| 604|     4|              |       2|   0|Not present|  0| 110|   1|   -3|    -3|
    | 10| 604|     5|              |       2|   0|Not present|  0| 110|   1|   -3|    -3|
    | 11| 605|     3|             2|      1a|   1|          0|  0| 110|   1|   -3|    -3|
    | 12| 607|     2|              |       1|   0|Not present|  0| 110|   1|   -3|    -3|
    | 13| 608|     4|              |       2|   0|Not present|  0| 110|   1|   -3|    -3|
    | 14| 608|     5|              |       2|   0|Not present|  0| 110|   1|   -3|    -3|
    | 15| 609|     2|              |       1|   0|Not present|  0| 110|   1|   -3|    -3|
    | 16| 611|     9|             2|      1a|   1|          0|  0| 110|   1|   -3|    -3|
    | 17| 612|     3|             2|      1b|   2|          0|  0| 110|   1|    0|     0|
    | 18| 612|     4|             2|      2a|   1|          0|  0| 110|   1|   -3|    -3|
    | 19| 612|     5|              |       2|   0|Not present|  0| 110|   1|   -3|    -3|
    | 20| 612|     9|             2|      1b|   2|          0|  0| 110|   1|    0|     0|
    | 21| 613|     2|              |       1|   0|Not present|  0| 110|   1|   -3|    -3|
    | 22| 615|     3|             2|      1a|   1|          0|  0| 110|   1|   -3|    -3|
    | 23| 616|     1|             2|      1b|   2|          0|  0| 110|   1|    0|     0|
    | 24| 616|     5|              |       2|   0|Not present|  0| 110|   1|   -3|    -3|
    | 25| 616|     9|             2|      1a|   1|          0|  0| 110|   1|   -3|    -3|
    | 26| 617|     3|             2|      1a|   1|          0|  0| 110|   1|   -3|    -3|
    | 27| 617|     6|             2|      1b|   2|          0|  0| 110|   1|    0|     0|
    | 28| 619|     3|             2|      1b|   2|          0|  0| 110|   1|    0|     0|
    | 29| 620|     2|              |       1|   0|Not present|  0| 110|   1|   -3|    -3|
    | 30| 620|     3|             2|      1a|   1|          0|  0| 110|   1|   -3|    -3|
    | 31| 620|     4|              |       2|   0|Not present|  0| 110|   1|   -3|    -3|
    | 32| 620|     5|              |       2|   0|Not present|  0| 110|   1|   -3|    -3|
    | 33| 620|     6|             2|      1b|   2|          0|  0| 110|   1|    0|     0|
    | 34| 621|     3|             2|      1b|   2|          0|  0| 110|   1|    0|     0|
    | 35| 623|     3|             2|      1b|   2|          0|  0| 110|   1|    0|     0|
    | 36| 624|     1|             2|      1b|   2|          0|  0| 110|   0|   -1|    -1|
    | 37| 624|     2|              |       1|   0|Not present|  0| 110|   0|   -4|    -4|
    | 38| 624|     4|              |       2|   0|Not present|  0| 110|   0|   -4|    -4|
    | 39| 624|     5|              |       2|   0|Not present|  0| 110|   0|   -4|    -4|
    | 40| 625|     8|             2|      1a|   1|          0|  0| 110|   0|   -4|    -4|
    | 41| 627|     2|              |       1|   0|Not present|  0| 110|   0|   -4|    -4|
    | 42| 628|     4|              |       2|   0|Not present|  0| 110|   0|   -4|    -4|
    | 43| 628|     5|              |       2|   0|Not present|  0| 110|   0|   -4|    -4|
    | 44| 629|     2|              |       1|   0|Not present|  0| 110|   0|   -4|    -4|
    | 45| 629|     3|             2|      1b|   2|          0|  0| 110|   0|   -1|    -1|
    | 46| 629|     6|             2|      1a|   1|         -1|  0| 110|  -1|   -5|    -5|
    | 47| 629|     8|             2|      1b|   2|          0|  0| 110|  -1|   -2|    -2|
    | 48| 630|     9|             2|      1b|   2|          0|  0| 110|  -1|   -2|    -2|
    | 49| 632|     2|              |       1|   0|Not present|  0| 110|  -1|   -5|    -5|
    """)
        messages.append(msg)
        msg = ParsedRawMessage(index=0, packet_type="0xB0E3", packet_length=100,
                               name="LTE NAS ESM Plain OTA Outgoing Message",
                               subtitle="PDN connectivity request Msg", datetime="2024 Jan 15  07:17:10.651",
                               packet_text=
                               """
2024 Jan 15  07:17:10.651  [70]  0xB0E3  LTE NAS ESM Plain OTA Outgoing Message  --  PDN connectivity request Msg
Subscription ID = 1
pkt_version = 1 (0x1)
rel_number = 9 (0x9)
rel_version_major = 5 (0x5)
rel_version_minor = 0 (0x0)
eps_bearer_id_or_skip_id = 0 (0x0)
prot_disc = 2 (0x2) (EPS session management messages)
trans_id = 12 (0xc)
msg_type = 208 (0xd0) (PDN connectivity request)
lte_esm_msg
  pdn_connectivity_req
    pdn_type = 3 (0x3) (Ipv4v6)
    req_type = 1 (0x1) (initial request)
    info_trans_flag_incl = 0 (0x0)
    access_pt_name_incl = 1 (0x1)
    access_pt_name_
      num_acc_pt_val = 4 (0x4)
      acc_pt_name_val[0] = 3 (0x3) (length)
      acc_pt_name_val[1] = 105 (0x69) (i)
      acc_pt_name_val[2] = 109 (0x6d) (m)
      acc_pt_name_val[3] = 115 (0x73) (s)
    prot_config_incl = 1 (0x1)
    prot_config
      ext = 1 (0x1)
      conf_prot = 0 (0x0)
      num_recs = 13 (0xd)
      prot_or_container[0]
        id = 32801 (0x8021) (IPCP)
        prot_or_container
          prot_len = 16 (0x10)
          ipcp_prot
            ipcp_prot_id = 1 (0x1) (CONF_REQ)
            identifier = 0 (0x0)
            rfc1332_conf_req
              num_options = 2 (0x2)
              conf_options[0]
                type = 129 (0x81)
                rfc1877_primary_dns_server_add
                  length = 6 (0x6)
                  ip_addr = 0 (0x0) (0.0.0.0)
              conf_options[1]
                type = 131 (0x83)
                rfc1877_sec_dns_server_add
                  length = 6 (0x6)
                  ip_addr = 0 (0x0) (0.0.0.0)
      prot_or_container[1]
        id = 13 (0xd) (DNS Server IPv4 Address Request)
        prot_or_container
          prot_len = 0 (0x0)
      prot_or_container[2]
        id = 3 (0x3) (DNS Server IPv6 Address Request)
        prot_or_container
          prot_len = 0 (0x0)
      prot_or_container[3]
        id = 1 (0x1) (P-CSCF IPv6 Address Request)
        prot_or_container
          prot_len = 0 (0x0)
      prot_or_container[4]
        id = 12 (0xc) (P-CSCF IPv4 Address Request)
        prot_or_container
          prot_len = 0 (0x0)
      prot_or_container[5]
        id = 18 (0x12) (P-CSCF Re-selection support)
        prot_or_container
          prot_len = 0 (0x0)
      prot_or_container[6]
        id = 2 (0x2) (IM CN Subsystem Signalling Flag)
        prot_or_container
          prot_len = 0 (0x0)
      prot_or_container[7]
        id = 10 (0xa) (IP address allocation via NAS signalling)
        prot_or_container
          prot_len = 0 (0x0)
      prot_or_container[8]
        id = 5 (0x5) (NWK Req Bearer Control indicator)
        prot_or_container
          prot_len = 0 (0x0)
      prot_or_container[9]
        id = 16 (0x10) (Ipv4 Link MTU Request)
        prot_or_container
          prot_len = 0 (0x0)
      prot_or_container[10]
        id = 17 (0x11) (MS support of Local address in TFT indicator)
        prot_or_container
          prot_len = 0 (0x0)
      prot_or_container[11]
        id = 26 (0x1a) (PDU Session ID)
        prot_or_container
          prot_len = 1 (0x1)
          container
            container_contents[0] = 2 (0x2)
      prot_or_container[12]
        id = 35 (0x23) (QoS Rules with the length of 2 Octs support indicator)
        prot_or_container
          prot_id_23_or_24_type
            Qos_rules_len_2_octets
              num_qos_rules = 0 (0x0)
    dev_properties_incl = 0 (0x0)
    nbifom_incl = 0 (0x0)
    header_compression_config_inclu = 0 (0x0)
    ext_prot_config_incl = 0 (0x0)
                       """)
        messages.append(msg)

        msg = ParsedRawMessage(index=0, packet_type="0xB16E", packet_length=100,
                               name="LTE PUSCH Power Control",
                               subtitle="", datetime="2024 Jan 19  21:46:06.212", packet_text=
                               """
2024 Jan 19  21:46:06.212  [10]  0xB16E  LTE PUSCH Power Control
Subscription ID = 1
Version = 48
cell_alpha PCC = 1
cell_alpha ul_id 1 = 0
cell_alpha ul_id 2 = 0
cell_alpha ul_id 3 = 0
Number of Records = 16
Report
   ------------------------------------------------------------------------------------------------
   |     |    |      |      |               |   |Transport|    |    |      |   |PUSCH|PUSCH |     |
   |     |    |      |      |               |   |Block    |DL  |    |      |   |Tx   |Actual|     |
   |Cell |    |      |DCI   |               |Num|Size     |Path|    |TPC   |   |Power|Tx    |Max  |
   |Index|SFN |Sub-fn|Format|Tx Type        |RBs|(bytes)  |Loss|F(i)|Frozen|TPC|(dBm)|Power |Power|
   ------------------------------------------------------------------------------------------------
   |    0| 676|     1|     0|        Dynamic|  1|        0| 105|   5|     0|  0|   12|    12|   25|
   |    0| 685|     1|     0|        Dynamic|  1|        0| 105|   5|     0|  0|   12|    12|   25|
   |    0| 694|     1|     0|        Dynamic|  1|        0| 105|   5|     0|  0|   12|    12|   25|
   |    0| 703|     1|     0|        Dynamic|  1|        0| 105|   5|     0|  0|   12|    12|   25|
   |    0| 712|     5|     0|        Dynamic|  1|        0| 105|   5|     0|  0|   12|    12|   25|
   |    0| 721|     1|     0|        Dynamic|  1|        0| 105|   5|     0|  0|   12|    12|   25|
   |    0| 730|     1|     0|        Dynamic|  1|        0| 105|   5|     0|  0|   12|    12|   25|
   |    0| 735|     5|     0|        Dynamic|  4|       18| 105|   5|     0|  0|   18|    18|   25|
   |    0| 739|     1|     0|        Dynamic|  1|        0| 105|   5|     0|  0|   12|    12|   25|
   |    0| 748|     1|     0|        Dynamic|  1|        0| 105|   5|     0|  0|   12|    12|   25|
   |    0| 757|     1|     0|        Dynamic|  1|        0| 105|   5|     0|  0|   12|    12|   25|
   |    0| 765|     5|     0|        Dynamic|  4|      193| 106|   5|     0|  0|   19|    19|   24|
   |    0| 774|     1|     0|        Dynamic|  1|        0| 106|   5|     0|  0|   13|    13|   25|
   |    0| 783|     1|     0|        Dynamic|  1|        0| 106|   5|     0|  0|   13|    13|   25|
   |    0| 792|     1|     0|        Dynamic|  1|        0| 106|   5|     0|  0|   13|    13|   25|
   |    0| 802|     1|     0|        Dynamic|  1|        0| 106|   5|     0|  0|   13|    13|   25|
                       """)
        messages.append(msg)
        msg = ParsedRawMessage(index=0, packet_type="0xB139", packet_length=100,
                               name="LTE LL1 PUSCH Tx Report",
                               subtitle="", datetime="2024 Jan 19  21:46:04.057", packet_text=
                               """
2024 Jan 19  21:46:04.057  [8F]  0xB139  LTE LL1 PUSCH Tx Report
Subscription ID = 1
Version = 162
Serving Cell ID = 147
Number of Records = 1
Dispatch SFN SF = 5865
Records
   ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
   |       |       |      |      |      |           |        |      |       |          |     |     |   |       |      |       |       |       |              |            |                                |       |       |       |   |        |        |       |        |        |    |       |         |        |      |    |    |     |     |                 |                                                |               |Cyclic   |Cyclic   |    |    |
   |       |       |      |      |      |           |        |      |       |          |     |     |   |       |      |       |       |       |              |            |                                |       |       |       |   |        |        |       |        |        |    |       |         |        |      |    |    |     |     |                 |                                                |               |Shift of |Shift of |    |    |
   |       |       |      |      |      |           |        |      |       |          |Start|Start|   |       |Enable|       |       |Rate   |              |            |                                |ACK/NAK|ACK/NAK|       |   |        |        |PUSCH  |        |        |    |Rate   |         |        |      |    |    |     |PUSCH|                 |                                                |               |DMRS     |DMRS     |DMRS|DMRS|
   |       |UL     |      |      |      |           |        |      |       |Resource  |RB   |RB   |Num|DL     |UL    |PUSCH  |       |Matched|              |            |                                |Inp    |Inp    |Rate   |   |        |PUSCH   |Digital|        |        |Num |Matched|         |        |Ack   |Ack |    |     |Tx   |                 |                                                |               |Symbols  |Symbols  |Root|Root|
   |Current|Carrier|      |      |      |Frequency  |Re-tx   |Redund|Mirror |Allocation|Slot |Slot |of |Carrier|DMRS  |TB Size|Coding |ACK    |              |Num RI Bits |                                |Length |Length |Matched|UE |SRS     |Mod     |Gain   |Start RB|Num RB  |CQI |CQI    |         |Num DL  |Nack  |Nack|CSF |Drop |Power|                 |                                                |               |Slot 0   |Slot 1   |Slot|Slot|
   |SFN SF |Index  |ACK   |CQI   |RI    |Hopping    |Index   |Ver   |Hopping|Type      |0    |1    |RB |Index  |OCC   |(bytes)|Rate   |Bits   |RI Payload    |(bits)      |ACK Payload                     |0      |1      |RI Bits|SRS|Occasion|Order   |(dB)   |Cluster1|Cluster1|Bits|Bits   |reserved4|Carriers|Index |Late|Late|PUSCH|(dBm)|DROP_PUSCH_REASON|CQI Payload                                     |Tx Resampler   |(Samples)|(Samples)|0   |1   |
   ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
   |   5862|    PCC|  None|  None|  None|   Disabled|   First|     0|      0|         0|   33|   33|  3|    PCC|     0|     22|  0.231|      0|00000000000000|           0|00000000000000000000000000000000|      0|      0|      0|OFF|     OFF|    QPSK|    195|       0|       0|   0|      0|        0|       0|0x0000|   0|   0|    0|   17|          NO_DROP|  0x00000000  0x00000000  0x00000000  0x00000000|  -0.3999989296|        7|        0|  28|  28|
   |       |       |      |      |      |           |        |      |       |          |     |     |   |       |      |       |       |       |              |            |00000000000000000000000000000000|       |       |       |   |        |        |       |        |        |    |       |         |        |      |    |    |     |     |                 |  0x00000000  0x00000000  0x00000000  0x00000000|               |         |         |    |    |
   |       |       |      |      |      |           |        |      |       |          |     |     |   |       |      |       |       |       |              |            |00000000000000000000000000000000|       |       |       |   |        |        |       |        |        |    |       |         |        |      |    |    |     |     |                 |  0x00000000  0x00000000  0x00000000            |               |         |         |    |    |
   |       |       |      |      |      |           |        |      |       |          |     |     |   |       |      |       |       |       |              |            |00000000000000000000000000000000|       |       |       |   |        |        |       |        |        |    |       |         |        |      |    |    |     |     |                 |                                                |               |         |         |    |    |

                       """)
        messages.append(msg)
        msg = ParsedRawMessage(index=0, packet_type="0xB060", packet_length=100,
                               name="LTE MAC Configuration",
                               subtitle="", datetime="2024 Jan 15  07:14:07.591", packet_text=
                               """
2024 Jan 15  07:14:07.591  [0C]  0xB060  LTE MAC Configuration
Subscription ID = 1
Version = 1
Number of SubPackets = 5
SubPacket ID = 1
SubPacket - ( DL Config SubPacket )
   Version = 2
   SubPacket Size = 12 bytes
   DL Config V2
      Sub Id = 1
      Num Active Stag = 1
      Scell Tag Info
         ------------------------------
         |   |    |Scell|Ta     |TA   |
         |   |STAG|Id   |Timer  |Timer|
         |#  |Id  |Mask |Present|(ms) |
         ------------------------------
         |  0| 255|  255|    255|10240|

SubPacket ID = 2
SubPacket - ( UL Config Subpacket )
   Version = 2
   SubPacket Size = 16 bytes
   UL Config V2
      Sub Id = 1
      SR resource present = Yes (1)
      SR periodicity = 10 ms
      BSR timer = Infinity
      SPS Number of Tx release = 0
      Retx BSR timer = 320 ms
SubPacket ID = 14
SubPacket - (All Rach Config SubPacket) {
   Version = 2
   Subpacket Size = 712 bytes
   Sub Id = 0
   Valid Cell Cfg Mask = 00000000b
   New Cell Cfg Mask = 00000000b
   Cell Rach Info
      -------------------------------------------------------------------------------------------------------------------------------------
      |   |     |        |       |      |      |        |          |       |          |        |      |      |     |      |     |    |RA  |
      |   |     |Preamble|Power  |      |      |        |          |       |          |        |      |      |     |      |     |    |rsp |
      |   |     |initial |ramping|      |      |Preamble|Contention|Message|Power     |Delta   |      |CS    |Root |PRACH |High |Max |win |
      |   |Scell|power   |step   |RA    |RA    |trans   |resolution|size   |offset    |preamble|PRACH |zone  |seq  |Freq  |speed|retx|size|
      |#  |Id   |(dB)    |(dB)   |index1|index2|max     |timer (ms)|Group_A|Group_B   |Msg3    |config|length|index|Offset|flag |Msg3|(ms)|
      -------------------------------------------------------------------------------------------------------------------------------------
      |  0|    0|       0|      0|     0|     0|       0|         0|      0|- Infinity|       0|     0|     0|    0|     0|    0|   0|   0|
      |  1|    0|       0|      0|     0|     0|       0|         0|      0|- Infinity|       0|     0|     0|    0|     0|    0|   0|   0|
      |  2|    0|       0|      0|     0|     0|       0|         0|      0|- Infinity|       0|     0|     0|    0|     0|    0|   0|   0|
      |  3|    0|       0|      0|     0|     0|       0|         0|      0|- Infinity|       0|     0|     0|    0|     0|    0|   0|   0|
      |  4|    0|       0|      0|     0|     0|       0|         0|      0|- Infinity|       0|     0|     0|    0|     0|    0|   0|   0|
      |  5|    0|       0|      0|     0|     0|       0|         0|      0|- Infinity|       0|     0|     0|    0|     0|    0|   0|   0|
      |  6|    0|       0|      0|     0|     0|       0|         0|      0|- Infinity|       0|     0|     0|    0|     0|    0|   0|   0|
      |  7|    0|       0|      0|     0|     0|       0|         0|      0|- Infinity|       0|     0|     0|    0|     0|    0|   0|   0|

}
SubPacket ID = 4
SubPacket - ( LC Config Subpacket )
   Version = 2
   SubPacket Size = 328 bytes
   Version 2 {
      Sub Id = 1
      Number of deleted LC = 0
      Number of added/modified LC = 1
      ---------------------------------------------------
      |     |          |          |          |Token     |
      |     |          |          |          |bucket    |
      |     |PBR       |          |          |size      |
      |LC ID|(KBytes/s)|Priority  |LC group  |(bytes)   |
      ---------------------------------------------------
      |    1|     65535|         1|         0|         0|

   }
SubPacket ID = 18

                       """)
        messages.append(msg)
        msg = ParsedRawMessage(index=0, packet_type="0xB0A5", packet_length=100,
                               name="LTE PDCP DL SRB Integrity Data PDU",
                               subtitle="", datetime="2024 Jan 15  07:14:07.644", packet_text=
                               """
2024 Jan 15  07:14:07.644  [62]  0xB0A5  LTE PDCP DL SRB Integrity Data PDU
Subscription ID = 1
Version = 1
Num Subpackets = 1
Subpacket[0]
   Subpacket ID = PDCP DL SRB Integrity PDU (0xC6)
   DL SRB Integrity Data PDU Subpacket
      Subpacket Version = 40
      Subpacket Size = 68 bytes
      Ciphering keys for SRBs (hex) =  12 B0 63 3E 1E AC 74 B8 EC BE 00 C2 B7 6A 10 E8
      Integrity Keys for SRBs (hex) =  69 17 91 A4 0A 2F AE C2 0E DC AA 6E 8E 67 9D DF
      SRB Cipher Algo = LTE AES
      SRB Integrity Algo = LTE AES
      Num PDUs = 1
      -------------------------------------------------------------------------------------------------------------------------
      |   |    |      |      |     |     |      |      |      |          |     |received  |computed  |                        |
      |cfg|    |sn    |bearer|valid|pdu  |logged|      |      |count     |     |MAC-I     |MAC-I     |un-ciphered log_buffer  |
      |idx|mode|length|id    |pdu  |size |bytes |sys_fn|sub_fn|(hex)     |sn   |(hex)     |(hex)     |(hex)                   |
      -------------------------------------------------------------------------------------------------------------------------
      | 33|  AM| 5 bit|     0|  Yes|    8|     8|   540|     5|       0x0|    0|0xD18545C2|0xD18545C2| 00 34 02 20 D1 85 45 C2|

                       """)
        messages.append(msg)
        msg = ParsedRawMessage(index=0, packet_type="0xB0A1", packet_length=100,
                               name="LTE PDCP DL Data PDU",
                               subtitle="", datetime="2024 Jan 15  07:14:47.063", packet_text=
                               """
2024 Jan 15  07:14:47.063  [B4]  0xB0A1  LTE PDCP DL Data PDU
Subscription ID = 1
Version = 53
Number Of Meta = 17
Number Of RB = 4
Log Count = 2
PDCP State
   ---------------------------------------------------------
   |   |RB   |PDCP  |            |            |            |
   |   |Cfg  |SN    |            |            |            |
   |#  |Index|Length|RX Deliv    |Rx Next     |Next Count  |
   ---------------------------------------------------------
   |  0|   33|     5|          21|          21|           0|
   |  1|   34|     5|           1|           1|           0|
   |  2|    4|    12|          21|          21|          21|
   |  3|    6|    12|           2|           2|           0|

Meta Log Buffer
   ------------------------------------------------------------------------------------------------------------------------------------------------------
   |   |System  |             |     |     |     |                  |         |         |            |            |            |            |            |
   |   |Time    |             |RB   |     |     |                  |         |         |            |            |            |            |            |
   |   |Sub|    |             |Cfg  |Key  |RLC  |                  |IP Packet|IP Packet|            |            |            |Number IP   |Number IP   |
   |#  |FN |SFN |Rx Timetick  |Index|Index|Path |Route Status      |Header[0]|Header[1]|Start Count |End Count   |RLC end SN  |Pkts        |bytes       |
   ------------------------------------------------------------------------------------------------------------------------------------------------------
   |  0|  8| 343|    0.0100648|    4|    2|  MCG|      DELIV_DIRECT|      0x0|      0x0|           4|           5|           1|           2|        1352|
   |  1|  4| 344|    0.0123723|    4|    2|  MCG|      DELIV_DIRECT|      0x0|      0x0|           6|           6|           2|           1|         101|
   |  2|  5| 346|     0.020407|    4|    2|  MCG|      DELIV_DIRECT|      0x0|      0x0|           7|           7|           3|           1|         101|
   |  3|  8| 348|    0.0292454|    4|    2|  MCG|      DELIV_DIRECT|      0x0|      0x0|           8|           8|           4|           1|         101|
   |  4|  4| 350|     0.035361|    4|    2|  MCG|      DELIV_DIRECT|      0x0|      0x0|           9|           9|           5|           1|         101|
   |  5|  4| 352|    0.0430317|    4|    2|  MCG|      DELIV_DIRECT|      0x0|      0x0|          10|          10|           6|           1|         101|
   |  6|  4| 354|     0.050694|    4|    2|  MCG|      DELIV_DIRECT|      0x0|      0x0|          11|          11|           7|           1|          47|
   |  7|  4| 360|    0.0736978|    4|    2|  MCG|      DELIV_DIRECT|      0x0|      0x0|          12|          12|           8|           1|          47|
   |  8|  9| 369|     0.110042|    4|    2|  MCG|      DELIV_DIRECT|      0x0|      0x0|          13|          13|           9|           1|         101|
   |  9|  7| 371|      0.11703|    4|    2|  MCG|      DELIV_DIRECT|      0x0|      0x0|          14|          14|          10|           1|         101|
   | 10|  3| 373|      0.12316|    4|    2|  MCG|      DELIV_DIRECT|      0x0|      0x0|          15|          15|          11|           1|         101|
   | 11|  4| 374|     0.127381|    4|    2|  MCG|      DELIV_DIRECT|      0x0|      0x0|          16|          16|          12|           1|         101|
   | 12|  4| 376|     0.135046|    4|    2|  MCG|      DELIV_DIRECT|      0x0|      0x0|          17|          17|          13|           1|         101|
   | 13|  2| 378|     0.141941|    4|    2|  MCG|      DELIV_DIRECT|      0x0|      0x0|          18|          18|          14|           1|         668|
   | 14|  4| 378|     0.142707|    4|    2|  MCG|      DELIV_DIRECT|      0x0|      0x0|          19|          19|          15|           1|         101|
   | 15|  3| 381|     0.153829|    4|    2|  MCG|      DELIV_DIRECT|      0x0|      0x0|          20|          20|          16|           1|         101|
   | 16|  1| 385|     0.168444|    6|    2|  MCG|      DELIV_DIRECT|      0x0|      0x0|           0|           1|           2|           2|         201|

                       """)
        messages.append(msg)
        msg = ParsedRawMessage(index=0, packet_type="0xB06E", packet_length=100,
                               name="LTE MAC DL RAR Transport Block",
                               subtitle="", datetime="2024 Jan 15  07:14:07.576", packet_text=
                               """
2024 Jan 15  07:14:07.576  [01]  0xB06E  LTE MAC DL RAR Transport Block
Subscription ID = 1
Version = 48
Number of SubPackets = 1
SubPacket ID = 20
SubPacket - (DL Transport Block Subpacket)
   Version = 1
   Subpacket Size = 48
   ---------------------------------------------------------------------------------------------------------------------------------------------
   |   |    |      |   |          |    |       |   |                        |   |     |Absolute|    |      |      |     |   |     |   |        |
   |Sub|Cell|      |   |          |HARQ|DL TBS |LOG|                        |BI |Rapid|TA Val  |Hop |RB    |Coding|TBS  |TPC|UL   |CQI|        |
   |Id |Id  |Sub-FN|SFN|RNTI Type |Id  |(bytes)|LEN|RAR TB                  |Val|Val  |(16xTs) |Flag|Assign|Scheme|Index|dB |Delay|Req|T-C-RNTI|
   ---------------------------------------------------------------------------------------------------------------------------------------------
   |  0| 147|     7|533|   RA_RNTI|   2|      7|  7| 5B 00 A1 06 78 6B 4F   |   |   27|      10|   0|   131|  QPSK|    3|  6|    0|  0|  0x6B4F|
""")
        messages.append(msg)
        msg = ParsedRawMessage(index=0, packet_type="0xB062", packet_length=100,
                               name="LTE MAC Rach Attempt",
                               subtitle="", datetime="2024 Jan 15  07:14:07.588", packet_text=

                               """
2024 Jan 15  07:14:07.588  [7E]  0xB062  LTE MAC Rach Attempt
Subscription ID = 1
Version = 1
Number of SubPackets = 1
SubPacket ID = 6
SubPacket - ( RACH Attempt Subpacket )
   Version = 50
   Subpacket Size = 56 bytes
   RACH Attempt V50 {
      Sub Id = 1
      CC Id = 0
      Retx counter = 1
      Rach result = Success
      Contention procedure = Contention Based RACH procedure
      Msg1 - RACH Access Preamble[0]
         Preamble Index = 27
         Preamble index mask = Invalid
         Preamble power offset = -102 dB
         Pcmaxc = 24
         Group Chosen = Group A
      Msg2 - Random Access Response
         Backoff Value = 0 ms
         Result = True
         TCRNTI = 27471
         TA value = 10 
      Msg3
         Grant Raw = 0x010678
         Grant = 22 bytes
         Harq ID = 7
         MAC PDU = 0x20, 0x06, 0x1F, 0x4B, 0x1D, 0x08, 0xE0, 0x00, 0xC8, 0x00
      Earfcn = 132522
      P Max = 24
      SCell ID = 0
      Max Serv RSRP Present = TRUE
      Max Serv RSRP Cal = -89
   }
""")
        messages.append(msg)
        msg = ParsedRawMessage(index=0, packet_type="0xB1DA", packet_length=100,
                               name="LTE ML1 Antenna Switch Diversity",
                               subtitle="", datetime="2024 Jan 15  07:14:07.597", packet_text=

                               """
2024 Jan 15  07:14:07.597  [97]  0xB1DA  LTE ML1 Antenna Switch Diversity
Subscription ID = 1
Version = 53
Feature Enabled = TRUE
PRACH Switch Enabled = TRUE
Sub Id = 0
Phy Cell Id = 147
Call State = CONNECTED
Switch Type = None
MTPL Ratio = 16
EARFCN = 66986
Gating Thresh = -100 dBm
-------------------------------------------------------------------------------------------------------------------------------------------------------------
|     |       |          |          |          |Thresh  |Adj     |          |          |          |          |       |      |          |     |       |      |
|     |Carrier|Curr Delta|Avg Delta |          |High    |Thres   |Filt RSRP0|Filt RSRP1|Filt RSRP2|Filt RSRP3|Antenna|Action|Hysteresis|Cycle|Suspend|Switch|
|SFN  |Id     |(dBm)     |(dBm)     |Thresh Low|(dBm)   |(dBm)   |(dBm)     |(dBm)     |(dBm)     |(dBm)     |Number |Time  |Count     |Num  |Count  |Reason|
-------------------------------------------------------------------------------------------------------------------------------------------------------------
| 5360|    PCC|    0.0000|  -15.0000|    3.0000|  5.0000|  5.0000|  -89.6250|  -89.4375| -180.0000| -180.0000|      2|     0|         0|    1|INVALID| UNSET|

""")
        messages.append(msg)
        msg = ParsedRawMessage(index=0, packet_type="0xB081", packet_length=100,
                               name="LTE RLC DL Config Log packet",
                               subtitle="", datetime="2024 Jan 15  07:14:07.591", packet_text=

                               """
2024 Jan 15  07:14:07.591  [99]  0xB081  LTE RLC DL Config Log packet 
Subscription ID = 1
Version = 50
Submit Reason = RRC_REQ
Config Mask = RLC_DL | PDCP_DL
Num RB Logged = 1
Config Reason = RECFG
PDCP DRB Rel Mask = 0x00000000
RLC DRB Rel Mask = 0x00000000
PDCP SRB Rel mask = 0x00
RLC SRB Rel Mask = 0x00
PDCP DRB Changed Mask = 0x00000000
RLC DRB Changed mask = 0x00000000
PDCP SRB Changed Mask = 0x01
RLC SRB Changed mask = 0x01
RB Config
   ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
   |   |                |     |     |                |PDCP RB Info                                                                                                                                                                  |                                                                            |
   |   |                |     |     |                |                      |          |          |      |           |       |       |      |PDCP Config                                                                            |RLC RB Info                                                                 |
   |   |                |     |     |                |                      |          |          |      |           |       |       |      |      |       |    |          |        |        |          |ROHC Config                |    |      |       |           |UM               |AM                        |
   |   |                |     |     |                |                      |          |          |      |           |       |       |      |      |       |    |          |Rtatus  |Out Of  |          |       |          |DRB     |    |      |       |           |T         |      |T Status|T         |      |
   |   |                |RB   |     |                |                      |          |          |Config|Reestablish|Discard|Recover|Rohc  |Config|Discard|Sn  |Integrity |Report  |Order   |T         |       |Profile   |Continue|    |      |Config |Reestablish|Reassembly|SN    |Prohibit|Reassembly|SN    |
   |#  |RB Mode         |Index|EPSID|RB Type         |Config Action         |RLC Path  |PDCP Path |Bmask |Pdcp       |On Pdcp|Pdcp   |Enable|Mask  |Timer  |Size|Protection|Required|Delivery|Reordering|Max CID|Mask      |Rohc    |LCID|Action|Bitmask|RLC        |(ms)      |Length|(ms)    |(ms)      |Length|
   ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
   |  0|              AM|    1|    1|             SRB|               ACT_ADD|       LTE|       LTE|     0|      false|  false|  false| false|     0|  65535|   5|     false|   false|   false|     65535|      0|       0x0|   false|   1|     1|   0x00|      false|          |      |       0|        50|    10|

""")
        messages.append(msg)
        msg = ParsedRawMessage(index=0, packet_type="0xB13C", packet_length=100,
                               name="LTE LL1 PUCCH Tx Report",
                               subtitle="", datetime="2024 Jan 15  07:14:46.683", packet_text=

                               """
2024 Jan 15  07:14:46.683  [84]  0xB13C  LTE LL1 PUCCH Tx Report
Subscription ID = 1
Version = 162
Serving Cell ID = 147
Number of Records = 10
Dispatch SFN SF = 3487
Records
   ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
   |       |       |Start|Start|      |SRS        |   |DMRS|DMRS|                            |PUCCH  |PUCCH|        |       |   |     |                                |       |      |       |   |      |       |                 |          |         |      |    |    |     |               |
   |       |UL     |RB   |RB   |      |Shorting   |   |Seq |Seq |                            |Digital|Tx   |        |DL     |   |     |                                |ACK    |      |       |   |      |Num CSF|                 |          |         |Ack   |Ack |    |     |               |
   |Current|Carrier|Slot |Slot |      |for 2nd    |UE |Slot|Slot|                            |Gain   |Power|Num DL  |Carrier|Num|CDM  |                                |Payload|Is SR |Is SR  |SR |CSF   |P      |                 |CSF       |         |Nack  |Nack|CSF |Drop |               |
   |SFN SF |Index  |0    |1    |Format|Slot       |SRS|0   |1   |Cyclic Shift Seq per Symbol |(dB)   |(dBm)|Carriers|Index  |RB |Index|ACK Payload                     |Length |Config|Present|Bit|Length|Reports|DROP_PUCCH_REASON|Payload   |n_1_pucch|Index |Late|Late|Pucch|Tx Resampler   |
   ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
   |   3477|    PCC|    4|   45|     3|     Normal|OFF|  27|  27|   0   9   0   0   0  11   0|    195|  -10|       4|    PCC|  1|    0|00000000000000000000000001111011|      8|     0|      0|  0|     0|      0|          NO_DROP|0x00000000|       41|0x0210|   0|   0|    0|  -0.3999987508|
   |       |       |     |     |      |           |   |    |    |   0   6   0   0   0  11   0|       |     |        |       |   |     |00000000000000000000000000000000|       |      |       |   |      |       |                 |0x00000000|         |      |    |    |     |               |
   |       |       |     |     |      |           |   |    |    |                            |       |     |        |       |   |     |00000000000000000000000000000000|       |      |       |   |      |       |                 |0x00000000|         |      |    |    |     |               |
   |       |       |     |     |      |           |   |    |    |                            |       |     |        |       |   |     |00000000000000000000000000000000|       |      |       |   |      |       |                 |0x00000000|         |      |    |    |     |               |
   |   3478|    PCC|    4|   45|     3|     Normal|OFF|  27|  27|   0  11   0   0   0   9   0|    195|  -10|       4|    PCC|  1|    0|00000000000000000000000001111111|      8|     0|      0|  0|     0|      0|          NO_DROP|0x00000000|       42|0x0210|   0|   0|    0|  -0.3999987508|
   |       |       |     |     |      |           |   |    |    |   0   0   0   0   0  10   0|       |     |        |       |   |     |00000000000000000000000000000000|       |      |       |   |      |       |                 |0x00000000|         |      |    |    |     |               |
   |       |       |     |     |      |           |   |    |    |                            |       |     |        |       |   |     |00000000000000000000000000000000|       |      |       |   |      |       |                 |0x00000000|         |      |    |    |     |               |
   |       |       |     |     |      |           |   |    |    |                            |       |     |        |       |   |     |00000000000000000000000000000000|       |      |       |   |      |       |                 |0x00000000|         |      |    |    |     |               |
   |   3479|    PCC|    4|   45|     3|     Normal|OFF|  27|  27|   0   9   0   0   0   3   0|    195|  -10|       4|    PCC|  1|    0|00000000000000000000000001111111|      8|     0|      0|  0|     0|      0|          NO_DROP|0x00000000|       43|0x0210|   0|   0|    0|  -0.3999987508|
   |       |       |     |     |      |           |   |    |    |   0  11   0   0   0   6   0|       |     |        |       |   |     |00000000000000000000000000000000|       |      |       |   |      |       |                 |0x00000000|         |      |    |    |     |               |
   |       |       |     |     |      |           |   |    |    |                            |       |     |        |       |   |     |00000000000000000000000000000000|       |      |       |   |      |       |                 |0x00000000|         |      |    |    |     |               |
   |       |       |     |     |      |           |   |    |    |                            |       |     |        |       |   |     |00000000000000000000000000000000|       |      |       |   |      |       |                 |0x00000000|         |      |    |    |     |               |
   |   3480|    PCC|    4|   45|     3|     Normal|OFF|  27|  27|   0   8   0   0   0   1   0|    195|  -10|       4|    PCC|  1|    0|00000000000000000000000001001000|      8|     0|      0|  0|     0|      0|          NO_DROP|0x00000000|       40|0x0210|   0|   0|    0|  -0.3999987515|
   |       |       |     |     |      |           |   |    |    |   0   9   0   0   0   5   0|       |     |        |       |   |     |00000000000000000000000000000000|       |      |       |   |      |       |                 |0x00000000|         |      |    |    |     |               |
   |       |       |     |     |      |           |   |    |    |                            |       |     |        |       |   |     |00000000000000000000000000000000|       |      |       |   |      |       |                 |0x00000000|         |      |    |    |     |               |
   |       |       |     |     |      |           |   |    |    |                            |       |     |        |       |   |     |00000000000000000000000000000000|       |      |       |   |      |       |                 |0x00000000|         |      |    |    |     |               |
   |   3481|    PCC|    4|   45|     3|     Normal|OFF|  27|  27|   0   4   0   0   0   1   0|    195|  -10|       4|    PCC|  1|    0|00000000000000000000000001111111|      8|     0|      0|  0|     0|      0|          NO_DROP|0x00000000|       43|0x0210|   0|   0|    0|  -0.3999987503|
   |       |       |     |     |      |           |   |    |    |   0   4   0   0   0  10   0|       |     |        |       |   |     |00000000000000000000000000000000|       |      |       |   |      |       |                 |0x00000000|         |      |    |    |     |               |
   |       |       |     |     |      |           |   |    |    |                            |       |     |        |       |   |     |00000000000000000000000000000000|       |      |       |   |      |       |                 |0x00000000|         |      |    |    |     |               |
   |       |       |     |     |      |           |   |    |    |                            |       |     |        |       |   |     |00000000000000000000000000000000|       |      |       |   |      |       |                 |0x00000000|         |      |    |    |     |               |
   |   3482|    PCC|    4|   45|     3|     Normal|OFF|  27|  27|   0   4   0   0   0   3   0|    195|  -10|       4|    PCC|  1|    0|00000000000000000000000001111011|      8|     1|      1|  1|     0|      0|          NO_DROP|0x00000000|       40|0x0210|   0|   0|    0|  -0.3999987494|
   |       |       |     |     |      |           |   |    |    |   0  11   0   0   0  10   0|       |     |        |       |   |     |00000000000000000000000000000000|       |      |       |   |      |       |                 |0x00000000|         |      |    |    |     |               |
   |       |       |     |     |      |           |   |    |    |                            |       |     |        |       |   |     |00000000000000000000000000000000|       |      |       |   |      |       |                 |0x00000000|         |      |    |    |     |               |
   |       |       |     |     |      |           |   |    |    |                            |       |     |        |       |   |     |00000000000000000000000000000000|       |      |       |   |      |       |                 |0x00000000|         |      |    |    |     |               |
   |   3483|    PCC|    4|   45|     3|     Normal|OFF|  27|  27|   0   0   0   0   0   0   0|    195|  -10|       4|    PCC|  1|    0|00000000000000000000000001111111|      8|     0|      0|  0|     0|      0|          NO_DROP|0x00000000|       41|0x0210|   0|   0|    0|  -0.3999987494|
   |       |       |     |     |      |           |   |    |    |   0   3   0   0   0   9   0|       |     |        |       |   |     |00000000000000000000000000000000|       |      |       |   |      |       |                 |0x00000000|         |      |    |    |     |               |
   |       |       |     |     |      |           |   |    |    |                            |       |     |        |       |   |     |00000000000000000000000000000000|       |      |       |   |      |       |                 |0x00000000|         |      |    |    |     |               |
   |       |       |     |     |      |           |   |    |    |                            |       |     |        |       |   |     |00000000000000000000000000000000|       |      |       |   |      |       |                 |0x00000000|         |      |    |    |     |               |
   |   3484|    PCC|    4|   45|     3|     Normal|OFF|  27|  27|   0   3   0   0   0  11   0|    195|  -10|       4|    PCC|  1|    0|00000000000000000000000001111111|      8|     0|      0|  0|     0|      0|          NO_DROP|0x00000000|       41|0x0210|   0|   0|    0|  -0.3999987501|
   |       |       |     |     |      |           |   |    |    |   0   0   0   0   0   9   0|       |     |        |       |   |     |00000000000000000000000000000000|       |      |       |   |      |       |                 |0x00000000|         |      |    |    |     |               |
   |       |       |     |     |      |           |   |    |    |                            |       |     |        |       |   |     |00000000000000000000000000000000|       |      |       |   |      |       |                 |0x00000000|         |      |    |    |     |               |
   |       |       |     |     |      |           |   |    |    |                            |       |     |        |       |   |     |00000000000000000000000000000000|       |      |       |   |      |       |                 |0x00000000|         |      |    |    |     |               |
   |   3485|    PCC|    4|   45|     3|     Normal|OFF|  27|  27|   0   5   0   0   0  11   0|    195|  -10|       4|    PCC|  1|    0|00000000000000000000000001001100|      8|     0|      0|  0|     0|      0|          NO_DROP|0x00000000|       42|0x0210|   0|   0|    0|  -0.3999987496|
   |       |       |     |     |      |           |   |    |    |   0  10   0   0   0   9   0|       |     |        |       |   |     |00000000000000000000000000000000|       |      |       |   |      |       |                 |0x00000000|         |      |    |    |     |               |
   |       |       |     |     |      |           |   |    |    |                            |       |     |        |       |   |     |00000000000000000000000000000000|       |      |       |   |      |       |                 |0x00000000|         |      |    |    |     |               |
   |       |       |     |     |      |           |   |    |    |                            |       |     |        |       |   |     |00000000000000000000000000000000|       |      |       |   |      |       |                 |0x00000000|         |      |    |    |     |               |
   |   3486|    PCC|    4|   45|     3|     Normal|OFF|  27|  27|   0   2   0   0   0   4   0|    195|  -10|       4|    PCC|  1|    0|00000000000000000000000001111011|      8|     0|      0|  0|     0|      0|          NO_DROP|0x00000000|       43|0x0210|   0|   0|    0|  -0.3999987503|
   |       |       |     |     |      |           |   |    |    |   0   8   0   0   0   1   0|       |     |        |       |   |     |00000000000000000000000000000000|       |      |       |   |      |       |                 |0x00000000|         |      |    |    |     |               |
   |       |       |     |     |      |           |   |    |    |                            |       |     |        |       |   |     |00000000000000000000000000000000|       |      |       |   |      |       |                 |0x00000000|         |      |    |    |     |               |
   |       |       |     |     |      |           |   |    |    |                            |       |     |        |       |   |     |00000000000000000000000000000000|       |      |       |   |      |       |                 |0x00000000|         |      |    |    |     |               |

""")
        messages.append(msg)
        msg = ParsedRawMessage(index=0, packet_type="0xB16C", packet_length=100,
                               name="LTE DCI Information Report",
                               subtitle="", datetime="2024 Jan 15  07:14:46.673", packet_text=

                               """
2024 Jan 15  07:14:46.673  [F1]  0xB16C  LTE DCI Information Report
Subscription ID = 1
Version = 49
Duplex Mode = FDD
Subframe Cfg = 15
Number of Records = 20
DCI Info Records
   ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
   |   |     |      |     |     |       |                                         |UL Grant Info                                                                                                                                                                                                            |DL Grant Info                                                                  |
   |   |     |      |     |     |       |TPC DCI Info                             |     |   |    |   |               |     |         |          |     |             |          |       |       |          |    |        |Number  |      |        |      |     |     |        |Number  |         |           |DL   |DL    |       |DL     |   |DL   |     |               |           |      |
   |   |     |      |Num  |Num  |PDCCH  |       |TPC DCI   |              |TPC DCI|     |   |    |   |               |     |         |Redundancy|     |             |          |       |       |Resource  |    |Start of|of      |Cyclic|        |      |     |     |Start of|of      |TX       |           |Grant|Grant |Num    |Grant  |   |Grant|DL   |               |           |      |
   |   |     |      |UL   |DL   |Order  |TPC DCI|Format    |TPC DCI RNTI  |TPC    |Cell |   |HARQ|   |               |K of |UL       |Version   |MCS  |             |Modulation|CQI    |SRS    |Allocation|Rbg |Resource|Resource|Shift |Hopping |Search|RIV  |RIV  |Resource|Resource|Antenna  |Aggregation|Cell |Format|ACK/NAK|TPC    |   |Srs  |Grant|               |Aggregation|Search|
   |#  |SFN  |Sub-fn|Grant|Grant|Present|Present|Type      |Type          |Command|Index|NDI|ID  |TPC|Rnti Type      |DCI 0|Index/DAI|Index     |Index|TBS Index    |Type      |Request|Request|Type      |Size|Block   |Blocks  |DMRS  |Flag    |Space |Width|Value|Block 2 |Blocks 2|Selection|Level      |Index|Type  |Bits   |Command|DAI|Req  |N CCE|Rnti Type      |Level      |Space |
   ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
   |  0|  345|     7|    0|    4|     No|     No|          |              |       |     |   |    |   |               |     |         |          |     |             |          |       |       |          |    |        |        |      |        |      |     |     |        |        |         |           |    0|     2|      2|      1|   |   No|    8|         C_RNTI|          0|     0|
   |   |     |      |     |     |       |       |          |              |       |     |   |    |   |               |     |         |          |     |             |          |       |       |          |    |        |        |      |        |      |     |     |        |        |         |           |    1|     2|      2|      1|   |   No|    4|         C_RNTI|          0|     0|
   |   |     |      |     |     |       |       |          |              |       |     |   |    |   |               |     |         |          |     |             |          |       |       |          |    |        |        |      |        |      |     |     |        |        |         |           |    2|     2|      2|      1|   |   No|    8|         C_RNTI|          0|     0|
   |   |     |      |     |     |       |       |          |              |       |     |   |    |   |               |     |         |          |     |             |          |       |       |          |    |        |        |      |        |      |     |     |        |        |         |           |    3|     2|      1|      1|   |   No|    0|         C_RNTI|          0|     0|
   |  1|  345|     8|    0|    4|     No|     No|          |              |       |     |   |    |   |               |     |         |          |     |             |          |       |       |          |    |        |        |      |        |      |     |     |        |        |         |           |    0|     2|      2|      1|   |   No|    8|         C_RNTI|          0|     0|
   |   |     |      |     |     |       |       |          |              |       |     |   |    |   |               |     |         |          |     |             |          |       |       |          |    |        |        |      |        |      |     |     |        |        |         |           |    1|     2|      2|      2|   |   No|    4|         C_RNTI|          0|     0|
   |   |     |      |     |     |       |       |          |              |       |     |   |    |   |               |     |         |          |     |             |          |       |       |          |    |        |        |      |        |      |     |     |        |        |         |           |    2|     2|      2|      2|   |   No|    4|         C_RNTI|          0|     0|
   |   |     |      |     |     |       |       |          |              |       |     |   |    |   |               |     |         |          |     |             |          |       |       |          |    |        |        |      |        |      |     |     |        |        |         |           |    3|     2|      1|      2|   |   No|   24|         C_RNTI|          0|     0|
   |  2|  345|     9|    0|    4|     No|     No|          |              |       |     |   |    |   |               |     |         |          |     |             |          |       |       |          |    |        |        |      |        |      |     |     |        |        |         |           |    0|     2|      2|      1|   |   No|    8|         C_RNTI|          0|     0|
   |   |     |      |     |     |       |       |          |              |       |     |   |    |   |               |     |         |          |     |             |          |       |       |          |    |        |        |      |        |      |     |     |        |        |         |           |    1|     2|      2|      3|   |   No|    4|         C_RNTI|          0|     0|
   |   |     |      |     |     |       |       |          |              |       |     |   |    |   |               |     |         |          |     |             |          |       |       |          |    |        |        |      |        |      |     |     |        |        |         |           |    2|     2|      2|      3|   |   No|   16|         C_RNTI|          0|     0|
   |   |     |      |     |     |       |       |          |              |       |     |   |    |   |               |     |         |          |     |             |          |       |       |          |    |        |        |      |        |      |     |     |        |        |         |           |    3|     2|      1|      3|   |   No|   16|         C_RNTI|          0|     0|
   |  3|  346|     0|    0|    4|     No|     No|          |              |       |     |   |    |   |               |     |         |          |     |             |          |       |       |          |    |        |        |      |        |      |     |     |        |        |         |           |    0|     2|      2|      1|   |   No|    8|         C_RNTI|          0|     0|
   |   |     |      |     |     |       |       |          |              |       |     |   |    |   |               |     |         |          |     |             |          |       |       |          |    |        |        |      |        |      |     |     |        |        |         |           |    1|     2|      2|      3|   |   No|    4|         C_RNTI|          0|     0|
   |   |     |      |     |     |       |       |          |              |       |     |   |    |   |               |     |         |          |     |             |          |       |       |          |    |        |        |      |        |      |     |     |        |        |         |           |    2|     2|      2|      3|   |   No|   16|         C_RNTI|          0|     0|
   |   |     |      |     |     |       |       |          |              |       |     |   |    |   |               |     |         |          |     |             |          |       |       |          |    |        |        |      |        |      |     |     |        |        |         |           |    3|     2|      1|      3|   |   No|   16|         C_RNTI|          0|     0|
   |  4|  346|     1|    0|    2|     No|     No|          |              |       |     |   |    |   |               |     |         |          |     |             |          |       |       |          |    |        |        |      |        |      |     |     |        |        |         |           |    1|     2|      2|      0|   |   No|    4|         C_RNTI|          0|     0|
   |   |     |      |     |     |       |       |          |              |       |     |   |    |   |               |     |         |          |     |             |          |       |       |          |    |        |        |      |        |      |     |     |        |        |         |           |    3|     2|      1|      0|   |   No|    4|         C_RNTI|          0|     0|
   |  5|  346|     2|    1|    4|     No|     No|          |              |       |    0|  0|   2|  1|         C_RNTI|    4|         |         0|   14| TBS_INDEX_20|    64 QAM|      3|     No|         0|   0|      27|      15|     0|Disabled|     1|   11|  727|       0|       0|        0|          1|    0|     2|      2|      1|   |   No|    8|         C_RNTI|          0|     0|
   |   |     |      |     |     |       |       |          |              |       |     |   |    |   |               |     |         |          |     |             |          |       |       |          |    |        |        |      |        |      |     |     |        |        |         |           |    1|     2|      2|      1|   |   No|    4|         C_RNTI|          0|     0|
   |   |     |      |     |     |       |       |          |              |       |     |   |    |   |               |     |         |          |     |             |          |       |       |          |    |        |        |      |        |      |     |     |        |        |         |           |    2|     2|      2|      1|   |   No|   16|         C_RNTI|          0|     0|
   |   |     |      |     |     |       |       |          |              |       |     |   |    |   |               |     |         |          |     |             |          |       |       |          |    |        |        |      |        |      |     |     |        |        |         |           |    3|     2|      1|      1|   |   No|    4|         C_RNTI|          0|     0|
   |  6|  346|     3|    1|    4|     No|     No|          |              |       |    0|  0|   3|  1|         C_RNTI|    4|         |         0|   17| TBS_INDEX_23|    64 QAM|      2|     No|         0|   0|      31|       4|     1|Disabled|     1|   11|  181|       0|       0|        0|          1|    0|     2|      2|      1|   |   No|    6|         C_RNTI|          0|     0|
   |   |     |      |     |     |       |       |          |              |       |     |   |    |   |               |     |         |          |     |             |          |       |       |          |    |        |        |      |        |      |     |     |        |        |         |           |    1|     2|      2|      2|   |   No|    4|         C_RNTI|          0|     0|
   |   |     |      |     |     |       |       |          |              |       |     |   |    |   |               |     |         |          |     |             |          |       |       |          |    |        |        |      |        |      |     |     |        |        |         |           |    2|     2|      2|      2|   |   No|   12|         C_RNTI|          0|     0|
   |   |     |      |     |     |       |       |          |              |       |     |   |    |   |               |     |         |          |     |             |          |       |       |          |    |        |        |      |        |      |     |     |        |        |         |           |    3|     2|      1|      2|   |   No|    8|         C_RNTI|          0|     0|
   |  7|  346|     4|    0|    4|     No|     No|          |              |       |     |   |    |   |               |     |         |          |     |             |          |       |       |          |    |        |        |      |        |      |     |     |        |        |         |           |    0|     2|      2|      1|   |   No|    6|         C_RNTI|          0|     0|
   |   |     |      |     |     |       |       |          |              |       |     |   |    |   |               |     |         |          |     |             |          |       |       |          |    |        |        |      |        |      |     |     |        |        |         |           |    1|     2|      2|      3|   |   No|    4|         C_RNTI|          0|     0|
   |   |     |      |     |     |       |       |          |              |       |     |   |    |   |               |     |         |          |     |             |          |       |       |          |    |        |        |      |        |      |     |     |        |        |         |           |    2|     2|      2|      3|   |   No|   12|         C_RNTI|          0|     0|
   |   |     |      |     |     |       |       |          |              |       |     |   |    |   |               |     |         |          |     |             |          |       |       |          |    |        |        |      |        |      |     |     |        |        |         |           |    3|     2|      1|      3|   |   No|    8|         C_RNTI|          0|     0|
   |  8|  346|     5|    0|    4|     No|     No|          |              |       |     |   |    |   |               |     |         |          |     |             |          |       |       |          |    |        |        |      |        |      |     |     |        |        |         |           |    0|     2|      2|      1|   |   No|   34|         C_RNTI|          0|     0|
   |   |     |      |     |     |       |       |          |              |       |     |   |    |   |               |     |         |          |     |             |          |       |       |          |    |        |        |      |        |      |     |     |        |        |         |           |    1|     2|      2|      0|   |   No|    0|         C_RNTI|          0|     0|
   |   |     |      |     |     |       |       |          |              |       |     |   |    |   |               |     |         |          |     |             |          |       |       |          |    |        |        |      |        |      |     |     |        |        |         |           |    2|     2|      2|      0|   |   No|    4|         C_RNTI|          0|     0|
   |   |     |      |     |     |       |       |          |              |       |     |   |    |   |               |     |         |          |     |             |          |       |       |          |    |        |        |      |        |      |     |     |        |        |         |           |    3|     2|      1|      0|   |   No|    8|         C_RNTI|          0|     0|
   |  9|  346|     6|    0|    2|     No|     No|          |              |       |     |   |    |   |               |     |         |          |     |             |          |       |       |          |    |        |        |      |        |      |     |     |        |        |         |           |    1|     2|      2|      3|   |   No|    4|         C_RNTI|          0|     0|
   |   |     |      |     |     |       |       |          |              |       |     |   |    |   |               |     |         |          |     |             |          |       |       |          |    |        |        |      |        |      |     |     |        |        |         |           |    3|     2|      1|      3|   |   No|    8|         C_RNTI|          0|     0|
   | 10|  346|     7|    0|    2|     No|     No|          |              |       |     |   |    |   |               |     |         |          |     |             |          |       |       |          |    |        |        |      |        |      |     |     |        |        |         |           |    1|     2|      2|      0|   |   No|    4|         C_RNTI|          0|     0|
   |   |     |      |     |     |       |       |          |              |       |     |   |    |   |               |     |         |          |     |             |          |       |       |          |    |        |        |      |        |      |     |     |        |        |         |           |    3|     2|      1|      0|   |   No|   12|         C_RNTI|          0|     0|
   | 11|  346|     8|    0|    4|     No|     No|          |              |       |     |   |    |   |               |     |         |          |     |             |          |       |       |          |    |        |        |      |        |      |     |     |        |        |         |           |    0|     2|      2|      1|   |   No|   20|         C_RNTI|          0|     0|
   |   |     |      |     |     |       |       |          |              |       |     |   |    |   |               |     |         |          |     |             |          |       |       |          |    |        |        |      |        |      |     |     |        |        |         |           |    1|     2|      2|      1|   |   No|    4|         C_RNTI|          0|     0|
   |   |     |      |     |     |       |       |          |              |       |     |   |    |   |               |     |         |          |     |             |          |       |       |          |    |        |        |      |        |      |     |     |        |        |         |           |    2|     2|      2|      1|   |   No|    4|         C_RNTI|          0|     0|
   |   |     |      |     |     |       |       |          |              |       |     |   |    |   |               |     |         |          |     |             |          |       |       |          |    |        |        |      |        |      |     |     |        |        |         |           |    3|     2|      1|      1|   |   No|    4|         C_RNTI|          0|     0|
   | 12|  346|     9|    0|    4|     No|     No|          |              |       |     |   |    |   |               |     |         |          |     |             |          |       |       |          |    |        |        |      |        |      |     |     |        |        |         |           |    0|     2|      2|      1|   |   No|    8|         C_RNTI|          0|     0|
   |   |     |      |     |     |       |       |          |              |       |     |   |    |   |               |     |         |          |     |             |          |       |       |          |    |        |        |      |        |      |     |     |        |        |         |           |    1|     2|      2|      2|   |   No|    4|         C_RNTI|          0|     0|
   |   |     |      |     |     |       |       |          |              |       |     |   |    |   |               |     |         |          |     |             |          |       |       |          |    |        |        |      |        |      |     |     |        |        |         |           |    2|     2|      2|      2|   |   No|   16|         C_RNTI|          0|     0|
   |   |     |      |     |     |       |       |          |              |       |     |   |    |   |               |     |         |          |     |             |          |       |       |          |    |        |        |      |        |      |     |     |        |        |         |           |    3|     2|      1|      2|   |   No|   12|         C_RNTI|          0|     0|
   | 13|  347|     0|    0|    3|     No|     No|          |              |       |     |   |    |   |               |     |         |          |     |             |          |       |       |          |    |        |        |      |        |      |     |     |        |        |         |           |    1|     2|      2|      2|   |   No|    4|         C_RNTI|          0|     0|
   |   |     |      |     |     |       |       |          |              |       |     |   |    |   |               |     |         |          |     |             |          |       |       |          |    |        |        |      |        |      |     |     |        |        |         |           |    2|     2|      2|      2|   |   No|   16|         C_RNTI|          0|     0|
   |   |     |      |     |     |       |       |          |              |       |     |   |    |   |               |     |         |          |     |             |          |       |       |          |    |        |        |      |        |      |     |     |        |        |         |           |    3|     2|      1|      2|   |   No|   16|         C_RNTI|          0|     0|
   | 14|  347|     1|    0|    4|     No|     No|          |              |       |     |   |    |   |               |     |         |          |     |             |          |       |       |          |    |        |        |      |        |      |     |     |        |        |         |           |    0|     2|      2|      1|   |   No|    8|         C_RNTI|          0|     0|
   |   |     |      |     |     |       |       |          |              |       |     |   |    |   |               |     |         |          |     |             |          |       |       |          |    |        |        |      |        |      |     |     |        |        |         |           |    1|     2|      2|      3|   |   No|    4|         C_RNTI|          0|     0|
   |   |     |      |     |     |       |       |          |              |       |     |   |    |   |               |     |         |          |     |             |          |       |       |          |    |        |        |      |        |      |     |     |        |        |         |           |    2|     2|      2|      3|   |   No|   16|         C_RNTI|          0|     0|
   |   |     |      |     |     |       |       |          |              |       |     |   |    |   |               |     |         |          |     |             |          |       |       |          |    |        |        |      |        |      |     |     |        |        |         |           |    3|     2|      1|      3|   |   No|    0|         C_RNTI|          0|     0|
   | 15|  347|     2|    0|    4|     No|     No|          |              |       |     |   |    |   |               |     |         |          |     |             |          |       |       |          |    |        |        |      |        |      |     |     |        |        |         |           |    0|     2|      2|      1|   |   No|    8|         C_RNTI|          0|     0|
   |   |     |      |     |     |       |       |          |              |       |     |   |    |   |               |     |         |          |     |             |          |       |       |          |    |        |        |      |        |      |     |     |        |        |         |           |    1|     2|      2|      0|   |   No|    4|         C_RNTI|          0|     0|
   |   |     |      |     |     |       |       |          |              |       |     |   |    |   |               |     |         |          |     |             |          |       |       |          |    |        |        |      |        |      |     |     |        |        |         |           |    2|     2|      2|      0|   |   No|   12|         C_RNTI|          0|     0|
   |   |     |      |     |     |       |       |          |              |       |     |   |    |   |               |     |         |          |     |             |          |       |       |          |    |        |        |      |        |      |     |     |        |        |         |           |    3|     2|      1|      0|   |   No|   16|         C_RNTI|          0|     0|
   | 16|  347|     3|    0|    4|     No|     No|          |              |       |     |   |    |   |               |     |         |          |     |             |          |       |       |          |    |        |        |      |        |      |     |     |        |        |         |           |    0|     2|      2|      1|   |   No|    2|         C_RNTI|          0|     0|
   |   |     |      |     |     |       |       |          |              |       |     |   |    |   |               |     |         |          |     |             |          |       |       |          |    |        |        |      |        |      |     |     |        |        |         |           |    1|     2|      2|      1|   |   No|    4|         C_RNTI|          0|     0|
   |   |     |      |     |     |       |       |          |              |       |     |   |    |   |               |     |         |          |     |             |          |       |       |          |    |        |        |      |        |      |     |     |        |        |         |           |    2|     2|      2|      1|   |   No|   12|         C_RNTI|          0|     0|
   |   |     |      |     |     |       |       |          |              |       |     |   |    |   |               |     |         |          |     |             |          |       |       |          |    |        |        |      |        |      |     |     |        |        |         |           |    3|     2|      1|      1|   |   No|   12|         C_RNTI|          0|     0|
   | 17|  347|     4|    0|    4|     No|     No|          |              |       |     |   |    |   |               |     |         |          |     |             |          |       |       |          |    |        |        |      |        |      |     |     |        |        |         |           |    0|     2|      2|      1|   |   No|    6|         C_RNTI|          0|     0|
   |   |     |      |     |     |       |       |          |              |       |     |   |    |   |               |     |         |          |     |             |          |       |       |          |    |        |        |      |        |      |     |     |        |        |         |           |    1|     2|      2|      2|   |   No|    4|         C_RNTI|          0|     0|
   |   |     |      |     |     |       |       |          |              |       |     |   |    |   |               |     |         |          |     |             |          |       |       |          |    |        |        |      |        |      |     |     |        |        |         |           |    2|     2|      2|      2|   |   No|   12|         C_RNTI|          0|     0|
   |   |     |      |     |     |       |       |          |              |       |     |   |    |   |               |     |         |          |     |             |          |       |       |          |    |        |        |      |        |      |     |     |        |        |         |           |    3|     2|      1|      2|   |   No|   24|         C_RNTI|          0|     0|
   | 18|  347|     5|    0|    4|     No|     No|          |              |       |     |   |    |   |               |     |         |          |     |             |          |       |       |          |    |        |        |      |        |      |     |     |        |        |         |           |    0|     2|      2|      1|   |   No|   34|         C_RNTI|          0|     0|
   |   |     |      |     |     |       |       |          |              |       |     |   |    |   |               |     |         |          |     |             |          |       |       |          |    |        |        |      |        |      |     |     |        |        |         |           |    1|     2|      2|      3|   |   No|    4|         C_RNTI|          0|     0|
   |   |     |      |     |     |       |       |          |              |       |     |   |    |   |               |     |         |          |     |             |          |       |       |          |    |        |        |      |        |      |     |     |        |        |         |           |    2|     2|      2|      3|   |   No|    8|         C_RNTI|          0|     0|
   |   |     |      |     |     |       |       |          |              |       |     |   |    |   |               |     |         |          |     |             |          |       |       |          |    |        |        |      |        |      |     |     |        |        |         |           |    3|     2|      1|      3|   |   No|    8|         C_RNTI|          0|     0|
   | 19|  347|     6|    0|    2|     No|     No|          |              |       |     |   |    |   |               |     |         |          |     |             |          |       |       |          |    |        |        |      |        |      |     |     |        |        |         |           |    1|     2|      2|      0|   |   No|    4|         C_RNTI|          0|     0|
   |   |     |      |     |     |       |       |          |              |       |     |   |    |   |               |     |         |          |     |             |          |       |       |          |    |        |        |      |        |      |     |     |        |        |         |           |    3|     2|      1|      0|   |   No|    8|         C_RNTI|          0|     0|

""")
        messages.append(msg)
        msg = ParsedRawMessage(index=0, packet_type="0xB064", packet_length=100,
                               name="LTE MAC UL Transport Block",
                               subtitle="", datetime="2024 Jan 15  07:14:46.604", packet_text=

                               """
2024 Jan 15  07:14:46.604  [3F]  0xB064  LTE MAC UL Transport Block
Subscription ID = 1
Version = 1
Number of SubPackets = 1
SubPacket ID = 8
SubPacket - ( UL Transport Block Subpacket )
   Version = 3
   Subpacket Size = 148
   Uplink Transport Block V3
      Number of samples = 5
      ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
      |   |    |       |          |      |     |       |     |       |                 |               |     |                        |          |        |     |     |     |     |     |       |         |         |         |         |            |       |      |       |      |       |       |DC-   |DC- PHR|DC-   |DC- PHR|
      |Sub|Cell|       |          |      |     |Grant  |RLC  |Padding|                 |               |HDR  |                        |          |        |     |BSR  |BSR  |BSR  |BSR  |       |BSR LCG 0|BSR LCG 1|BSR LCG 2|BSR LCG 3|            |       |PH    |Pcmax_c|PH    |Pcmax_c|DC- PHR|PHR PH|Pcmax_c|PHR PH|Pcmax_c|
      |Id |Id  |HARQ ID|RNTI Type |Sub-FN|SFN  |(bytes)|PDUs |(bytes)|BSR event        |BSR trig       |LEN  |Mac Hdr + CE            |LC ID     |e-LC ID |LEN  |LCG 0|LCG 1|LCG 2|LCG 3|PHR Ind|(bytes)  |(bytes)  |(bytes)  |(bytes)  |SCC Bitmap  |Pcmax_c|SCell1|SCell1 |SCell2|SCell2 |Pcmax_c|SCell1|SCell1 |SCell2|SCell2 |
      ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
      |  1|   0|      7|    C-RNTI|     1|  331|    301|    1|    283|High Data Arrival|          S-BSR|   14| 3D 38 07 25 04 1F C0 00|     S-BSR|        |    1|     |     |     |    0|       |         |         |         |        0|            |       |      |       |      |       |       |      |       |      |       |
      |   |    |       |          |      |     |       |     |       |                 |               |     | 01 00 00 9B 34 7F      |    DC-PHR|        |    7|     |     |     |     |       |         |         |         |         |            |       |      |       |      |       |       |      |       |      |       |
      |   |    |       |          |      |     |       |     |       |                 |               |     |                        |         5|        |    4|     |     |     |     |       |         |         |         |         |            |       |      |       |      |       |       |      |       |      |       |
      |   |    |       |          |      |     |       |     |       |                 |               |     |                        |   Padding|        |   -1|     |     |     |     |       |         |         |         |         |            |       |      |       |      |       |       |      |       |      |       |
      |  1|   0|      1|    C-RNTI|     9|  332|    285|    1|    269|High Data Arrival|          S-BSR|   14| 3D 38 07 25 02 1F C0 00|     S-BSR|        |    1|     |     |     |    0|       |         |         |         |        0|            |       |      |       |      |       |       |      |       |      |       |
      |   |    |       |          |      |     |       |     |       |                 |               |     | 01 00 00 9B 34 7F      |    DC-PHR|        |    7|     |     |     |     |       |         |         |         |         |            |       |      |       |      |       |       |      |       |      |       |
      |   |    |       |          |      |     |       |     |       |                 |               |     |                        |         5|        |    2|     |     |     |     |       |         |         |         |         |            |       |      |       |      |       |       |      |       |      |       |
      |   |    |       |          |      |     |       |     |       |                 |               |     |                        |   Padding|        |   -1|     |     |     |     |       |         |         |         |         |            |       |      |       |      |       |       |      |       |      |       |
      |  1|   0|      7|    C-RNTI|     9|  335|    285|    1|    267|High Data Arrival|          S-BSR|   14| 3D 38 07 25 04 1F C0 00|     S-BSR|        |    1|     |     |     |    0|       |         |         |         |        0|            |       |      |       |      |       |       |      |       |      |       |
      |   |    |       |          |      |     |       |     |       |                 |               |     | 01 00 00 9B 34 7F      |    DC-PHR|        |    7|     |     |     |     |       |         |         |         |         |            |       |      |       |      |       |       |      |       |      |       |
      |   |    |       |          |      |     |       |     |       |                 |               |     |                        |         5|        |    4|     |     |     |     |       |         |         |         |         |            |       |      |       |      |       |       |      |       |      |       |
      |   |    |       |          |      |     |       |     |       |                 |               |     |                        |   Padding|        |   -1|     |     |     |     |       |         |         |         |         |            |       |      |       |      |       |       |      |       |      |       |
      |  1|   0|      3|    C-RNTI|     9|  337|    285|    1|    269|High Data Arrival|          S-BSR|   14| 3D 38 07 25 02 1F C0 00|     S-BSR|        |    1|     |     |     |    0|       |         |         |         |        0|            |       |      |       |      |       |       |      |       |      |       |
      |   |    |       |          |      |     |       |     |       |                 |               |     | 01 00 00 9B 34 7F      |    DC-PHR|        |    7|     |     |     |     |       |         |         |         |         |            |       |      |       |      |       |       |      |       |      |       |
      |   |    |       |          |      |     |       |     |       |                 |               |     |                        |         5|        |    2|     |     |     |     |       |         |         |         |         |            |       |      |       |      |       |       |      |       |      |       |
      |   |    |       |          |      |     |       |     |       |                 |               |     |                        |   Padding|        |   -1|     |     |     |     |       |         |         |         |         |            |       |      |       |      |       |       |      |       |      |       |
      |  1|   0|      7|    C-RNTI|     9|  339|    249|    1|    233|High Data Arrival|          S-BSR|   14| 3D 38 07 25 02 1F C0 00|     S-BSR|        |    1|     |     |     |    0|       |         |         |         |        0|            |       |      |       |      |       |       |      |       |      |       |
      |   |    |       |          |      |     |       |     |       |                 |               |     | 01 00 00 9B 34 7F      |    DC-PHR|        |    7|     |     |     |     |       |         |         |         |         |            |       |      |       |      |       |       |      |       |      |       |
      |   |    |       |          |      |     |       |     |       |                 |               |     |                        |         5|        |    2|     |     |     |     |       |         |         |         |         |            |       |      |       |      |       |       |      |       |      |       |
      |   |    |       |          |      |     |       |     |       |                 |               |     |                        |   Padding|        |   -1|     |     |     |     |       |         |         |         |         |            |       |      |       |      |       |       |      |       |      |       |

""")
        messages.append(msg)
        msg = ParsedRawMessage(index=0, packet_type="0xB0EF", packet_length=100,
                               name="LTE NAS EMM USIM card mode",
                               subtitle="", datetime="2024 Jan 15  07:15:51.068", packet_text=

                               """
2024 Jan 15  07:15:51.068  [5C]  0xB0EF  LTE NAS EMM USIM card mode
Subscription ID = 1
Version = 1
Card Mode = 3
LTE service support = True
IMSI = { 57, 49, 67, 32, 0, 149, 135, 6 }
EPSLOCI = { 
   11, 246, 19, 0, 20, 255, 73, 177, 
   208, 142, 0, 12, 19, 0, 20, 145, 
   13, 0
}
""")
        messages.append(msg)
        msg = ParsedRawMessage(index=0, packet_type="0xB0B5", packet_length=100,
                               name="LTE PDCP UL SRB Integrity Data PDU",
                               subtitle="", datetime="2024 Jan 15  07:14:07.591", packet_text=

                               """
2024 Jan 15  07:14:07.591  [78]  0xB0B5  LTE PDCP UL SRB Integrity Data PDU
Subscription ID = 1
Version = 56
SRB Ciphering Keys (hex) =  12 B0 63 3E 1E AC 74 B8 EC BE 00 C2 B7 6A 10 E8
SRB Integrity Keys (hex) =  69 17 91 A4 0A 2F AE C2 0E DC AA 6E 8E 67 9D DF
SRB Cipher Algo = NONE
SRB Integrity Algo = NONE
Num PDUs = 1
Entry
   --------------------------------------------------------------------------------------------------------------------------
   |   |Rb Info                            |     |      |             |            |               |                        |
   |   |Cfg|Rb  |Seq   |Bearer|            |PDU  |Logged|System Time  |            |Computed Mac-I |un-ciphered log_buffer  |
   |#  |Idx|Mode|Len   |Id    |Valid Pdu   |Size |Bytes |sys_fn|sub_fn|Count (hex) |(hex)          |(hex)                   |
   --------------------------------------------------------------------------------------------------------------------------
   |  0| 33|  AM| 5 bit|     0|   VALID PDU|   14|    14|   N/A|   N/A|  0x00000000|     0x00000000| 00 24 10 09 8E 5B D9 B2|
   |   |   |    |      |      |            |     |      |      |      |            |               | 85 80 00 00 00 00      |

""")
        messages.append(msg)
        msg = ParsedRawMessage(index=0, packet_type="0xB0B4", packet_length=100,
                               name="LTE PDCP UL Statistics Pkt",
                               subtitle="", datetime="2024 Jan 15  07:14:29.446", packet_text=

                               """
2024 Jan 15  07:14:29.446  [AF]  0xB0B4  LTE PDCP UL Statistics Pkt
Subscription ID = 1
Version = 59
Meta {
   Reason = PERIODIC
   Num Rb Logged = 4
   Num Error = 0
}
Per RB
   ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
   |   |        |      |        |        |    |            |                |                |                |                |            |            |            |            |            |            |            |                             |            |                                                                             |              |ROHC Info                                             |                                                                                                                                                         |
   |   |        |      |        |        |    |            |                |                |                |                |            |            |            |            |            |            |            |                             |            |                                                                             |              |          |          |Num       |          |          |                                                                                                                                                         |
   |   |        |      |        |        |Num |            |                |                |                |                |            |            |            |            |            |            |            |                             |            |                                                                             |              |          |          |Piggyback |          |          |UDC Info                                                                                                                                                 |
   |   |        |RB    |        |        |Flow|            |                |                |                |                |            |            |            |            |            |            |            |                             |            |Wm Flow Control Stats                                                        |              |Num ROHC  |          |Rohc      |Num Rohc  |Num Rohc  |          |          |Num UDC Fc|UDC Fc    |Num UDC   |UDC Reenq |          |          |          |Num Enb   |Num UDC   |Num UDC   |Num UDC   |Num UDC   |
   |   |Bearer  |Config|        |        |Ctrl|            |                |Data Bytes From |Num Pdcp Ul Buf |Data SDUs From  |Num Control |Control Pdu |Num Status  |Num Discard |Discard SDU |Num PDU HO  |Num PDU HO  |                             |Num Pdcp    |            |            |            |            |Count       |Count Dne   |              |Ctrl PDU  |Num ROHC  |Feedback  |Pdu Drop  |Pdu Drop  |Num UDC   |UDC Comp  |Uncomp    |Uncomp    |Reenq Pkts|Bytes     |Num UDC   |Num UDC   |Num UDC UE|UDC Ctrl  |Dsm Fc    |CPU Fc    |Dsm Fc    |CPU Fc    |
   |#  |Type    |Index |RB Type |RB Mode |Trig|Num Data Pdu|Data Pdu Bytes  |Wm              |Bytes           |Wm              |Pdu         |Bytes       |Report      |SDU         |Bytes       |ReTx        |ReTx Bytes  |Pdcp Flow State              |Window Stall|Total Count |Count Low   |Count High  |Count Empty |NonEmpty    |Bytes       |Wm Flow State |Tx        |Fail      |Rcvd      |Ho        |Ho Bytes  |Comp Pkts |Bytes     |Pkts      |Bytes     |Highest Q |Highest Q |Fail      |ENB Reset |Reset     |Pdus      |Down      |Down      |Shutdown  |Freeze    |
   ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
   |  0| DEFAULT|    33|     SRB|      AM|   0|          25|           12978|           12978|               0|              25|           0|           0|           0|           0|           0|           0|           0|                       ENABLE|           0|           0|           0|           0|           0|           0|           0|   LOW_ENABLED|          |          |          |          |          |          |          |          |          |          |          |          |          |          |          |          |          |          |          |
   |  1| DEFAULT|    34|     SRB|      AM|   0|           0|               0|               0|               0|               0|           0|           0|           0|           0|           0|           0|           0|                       ENABLE|           0|           0|           0|           0|           0|           0|           0|   LOW_ENABLED|          |          |          |          |          |          |          |          |          |          |          |          |          |          |          |          |          |          |          |
   |  2| DEFAULT|     4|     DRB|      AM|   0|           0|               0|               0|               0|               0|           0|           0|           0|           0|           0|           0|           0|                       ENABLE|           0|       12443|           1|           0|          79|          75|           0|   LOW_ENABLED|          |          |          |          |          |          |          |          |          |          |          |          |          |          |          |          |          |          |          |
   |  3| DEFAULT|     5|     DRB|      AM|   0|         714|          146825|          144683|               0|             714|           0|           0|           0|           0|           0|           2|         104|                       ENABLE|           0|           1|           1|           0|           0|           0|           0|   LOW_ENABLED|          |          |          |          |          |          |          |          |          |          |          |          |          |          |          |          |          |          |          |


""")
        messages.append(msg)
        msg = ParsedRawMessage(index=0, packet_type="0xB0B1", packet_length=100,
                               name="LTE PDCP UL Data PDU",
                               subtitle="", datetime="2024 Jan 15  07:14:24.391", packet_text=

                               """
2024 Jan 15  07:14:24.391  [C8]  0xB0B1  LTE PDCP UL Data PDU
Subscription ID = 1
Version = 60
Num RB ID Configured = 4
Num PDUs = 1
PDUs
   -------------------------------------------------------------------------------------------------------------------------------
   |   |      |System Time  |      |       |            |   |                                                                    |
   |   |RB    |      |System|      |RLC    |            |   |LSM                                                                 |
   |   |Config|Slot  |Frame |      |Payload|Start PDCP  |Num|   |               |Num|NLO                                         |
   |#  |Index |Number|Number|RLC SN|Length |Count       |LSM|#  |PDCP Count     |NLO|#  |PDCP Payload                            |
   -------------------------------------------------------------------------------------------------------------------------------
   |  0|    33|     2|   165|    49|      7|          24|  1|  0|             24|  1|  0| 0x18 0x12 0x00 0x83                    |


""")
        messages.append(msg)
        msg = ParsedRawMessage(index=0, packet_type="0x1568", packet_length=100,
                               name="IMS RTP SN and Payload",
                               subtitle="", datetime="2024 Jan 15  07:14:46.689", packet_text=

                               """
2024 Jan 15  07:14:46.689  [EF]  0x1568  IMS RTP SN and Payload
Subscription ID = 1
Version = 17
Direction = NETWORK_TO_UE
Rat Type = LTE
Sequence = 4
Ssrc = 424995790
Rtp Time stamp = 1280
CodecType = AMR-WB
mediaType = AUDIO
PayLoad Size = 73
Logged Payload Size = 61
Audio AMR-WB
   Marker = 0
   Codec mode Request = 15
   isMoreFrame = false
   Frame Type Index = AMR-WB 23.85 KBIT/S
   isFrameGood = true
   Mode = BANDWIDTH EFFICIENT
Latency Info Present = 0
Latency Block None
Rtp Raw Payload = { 
   244, 80, 17, 128, 25, 153, 102, 141, 
   252, 25, 64, 0, 21, 188, 2, 129, 
   199, 236, 148, 24, 132, 216, 7, 96, 
   1, 8, 97, 96, 191, 4, 134, 250, 
   17, 188, 240, 76, 236, 148, 2, 69, 
   76, 66, 129, 97, 184, 8, 4, 162, 
   5, 157, 129, 52, 240, 74, 18, 84, 
   200, 4, 168, 24, 16
}
Rtp Redundant Indicator = Original RTP Packet
""")
        messages.append(msg)
        msg = ParsedRawMessage(index=0, packet_type="0xB061", packet_length=100,
                               name="LTE MAC Rach Trigger",
                               subtitle="", datetime="2024 Jan 19  21:46:04.008", packet_text=

                               """
2024 Jan 19  21:46:04.008  [8B]  0xB061  LTE MAC Rach Trigger
Subscription ID = 1
Version = 1
Number of SubPackets = 2
SubPacket ID = 3
SubPacket - ( RACH Config Subpacket )
   Version = 9
   SubPacket Size = 28
   RACH Config V9
      Sub Id = 1
      Num Active Cell = 1
      Cell Rach Info[0]
         CC Id = 0
         Preamble initial power = -104 dB
         Power ramping step = 2 dB
         RA index1 = 32
         RA index2 = 48
         Preamble trans max = 10
         Contention resolution timer = 64 ms
         Message size Group_A = 18
         Power offset Group_B = -10 dB
         Delta preamble Msg3 = 6
         PRACH config = 3
         CS zone length = 12
         Root seq index = 0
         PRACH Freq Offset = 7
         High speed flag = 0
         Max retx Msg3 = 5
         RA rsp win size = 10 ms
SubPacket ID = 5
SubPacket - ( RACH Reason Subpacket )
   Version = 5
   Subpacket Size = 20 bytes
   RACH Reason V5
      Sub Id = 1
      CC Id = 0
      Rach reason = CONNECTION_REQ
      Maching ID = 0x5A, 0x72, 0x86, 0x7B, 0xC1, 0xE6
      RACH Contention = Contention Based RACH procedure
      Preamble = 0
      Preamble RA mask = 0xFF
      Msg3 size = 6 bytes
      Radio condn = 105 dB
      CRNTI = 0x7DEC
""")
        messages.append(msg)

        #     msg = ParsedRawMessage(index = 0, packet_type = "0x1FE7", packet_length=100, name="QTrace Event", subtitle="QEVENT 84 - 2", datetime="", packet_text=
        #     """2023 Nov 17  01:59:04.733  [BC]  0x1FE7  QTrace Event  --  QEVENT 84 - 2
        # nr5g_mac_rach.c     9254     D     Sub-ID:1     Misc-ID:0     QEvent 0x41100854 | NR5GMAC_QSH_EVENT_RACH_MSG2 | RAID_MATCH, ca: 0 | MTPL exceeded: 1 | RAR PRUNE bmsk: 0
        #     """)
        #     messages.append(msg)
        #     msg = ParsedRawMessage(index = 0, packet_type = "0x1FE7", packet_length=100, name="QTrace Event", subtitle="QEVENT 84 - 0", datetime="", packet_text=
        #     """2023 Nov 17  01:59:04.721  [EF]  0x1FE7  QTrace Event  --  QEVENT 84 - 0
        # nr5g_mac_rach.c     3669     D     Sub-ID:1     Misc-ID:0     QEvent 0x41100054 | NR5GMAC_QSH_EVENT_RACH_MSG1_PARTA | RACH Attempt#:0|SCS_1_25Khz|Lpream:0|RA_ID:24|RO:(68:1:0)|c_v:357|u:789|RBoffset:4|RNTI:15
        #     """)
        #     messages.append(msg)
        #     msg = ParsedRawMessage(index = 0, packet_type = "0x1FE7", packet_length=100, name="QTrace Event", subtitle="QEVENT 87 - 10", datetime="", packet_text=
        #     """2023 Nov 17  02:04:11.825  [40]  0x1FE7  QTrace Event  --  QEVENT 87 - 10
        # nr5g_rrc_qsh.c     1032     D     Sub-ID:1     Misc-ID:0     QEvent 0x29102857 | NR5GRRC_QSH_EVENT_UL_OTA_MSG | event_data=0x00000041 | RRCReconfigurationComplete
        #     """)
        #     messages.append(msg)
        #         msg = ParsedRawMessage(index = 0, packet_type="0xB887", packet_length=100, name="NR5G MAC PDSCH Status", subtitle="", datetime="2023 Dec 13  20:38:22.186", packet_text=
        #         """2023 Dec 13  20:38:22.186  [37]  0xB887  NR5G MAC PDSCH Status
        # Subscription ID = 1
        # Misc ID         = 0
        # Major.Minor = 2. 5
        # Log Fields Change BMask = 0x0
        # Sub ID = 0
        # Num Records = 1
        # Records
        #    ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
        #    |   |                     |      |PDSCH Status Info                                                                                                                                                                                                                                                                             |
        #    |   |                     |      |       |    |      |    |         |    |       |        |        |     |        |   |   |    |  |HARQ |    |    |   |      |         |        |      |    |   |       |      |      |    |       |       |       |       |      |     |        |     |        |       |       |       |       |
        #    |   |                     |      |       |    |      |    |         |    |       |        |        |     |        |   |   |    |  |Or   |    |K1  |   |      |         |        |      |    |   |       |      |      |    |       |       |       |       |      |     |        |     |        |RX     |RX     |RX     |RX     |
        #    |   |                     |Num   |       |    |      |    |         |    |       |        |        |     |        |   |   |    |  |MBSFN|    |Or  |   |      |         |        |      |New |   |       |      |      |    |HD     |HARQ   |HD     |HARQ   |      |Is   |        |High |        |Antenna|Antenna|Antenna|Antenna|
        #    |   |System Time          |PDSCH |Carrier|Tech|      |Conn|         |Band|Variant|Physical|        |TB   |        |SCS|   |Num |  |Area |RNTI|PMCH|   |Num   |Iteration|CRC     |CRC   |Tx  |   |Discard|Bypass|Bypass|Num |Onload |Onload |Offload|Offload|Did   |IOVec|        |Clock|        |Mapping|Mapping|Mapping|Mapping|
        #    |#  |Slot|Numerology|Frame|Status|ID     |Id  |Opcode|ID  |Bandwidth|Type|Id     |cell ID |EARFCN  |Index|TB Size |MU |MCS|Rbs |RV|Id   |Type|ID  |TCI|Layers|Index    |State   |Status|Flag|NDI|Mode   |Decode|HARQ  |ReTx|Timeout|Timeout|Timeout|Timeout|Recomb|Valid|Mod Type|Mode |Num RX  |0      |1      |2      |3      |
        #    ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
        #    |  0|   7|     30kHz|  835|     1|      0|   1|     3|   0|        3|   0|      0|     625|  520110|    0|      16|  1|  3|   9| 0|    0|   4|   1|  0|     1|        0|    PASS|  PASS|   1|  0|      0|     0|     1|   0|      0|      0|      0|      0|     0| true|    QPSK|    0|2x2_MIMO|      0|      0|      0|      0|
        #         """)
        #         messages.append(msg)
        # C:\Users\tm-reddev04\Documents\tmdc\storage\qxdm_mask_files\automation_freqtest.yaml
        # msg = ParsedRawMessage(index=0, packet_type="0xB887", packet_length=100, name="NR5G MAC PDSCH Status",
        #                        subtitle="", datetime="", packet_text=
        #                        """2023 Dec 13  20:38:22.186  [37]  0xB887  NR5G MAC PDSCH Status
        #
        #
        # """
        #
        #                        )

        # conf = parse_config("C:\\Users\\PS001015449\\PycharmProjects\\QxDM\\input.json")
        for message in messages:
            message.packet_config = {}
        json_arr = [{"_packetType": message.packet_type_hex, "_rawPayload": message.packet_text,
                     "_parsedPayload": message.test()} for message in messages]
        base_path = os.path.dirname(os.path.abspath(__file__))
        dt_format = datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S")
        with open(os.path.join(os.path.dirname(base_path), "temp", f"{dt_format}_parsed.json"), "w") as outfile:
            json_obj = json.dumps(json_arr, indent=2)
            outfile.write(json_obj)

    test_table_parsing()


if __name__ == "__main__":
    test_parsing()
