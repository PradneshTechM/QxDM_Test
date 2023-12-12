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


class ValidationType(Enum):
    FIRST_WORD_EXACT = auto()
    FIRST_WORD_ONE_OF = auto()   # TODO: prepend "one of: " to output for clarity
    FOUND_MATCH = auto()
    ANY_SUBSTRING = auto()
    FIRST_SAVE = auto()
    CHECK_SAVED = auto()
    CONCAT_AND_COMPARE = auto()
    COLLECTION = auto()          # TODO: prepend "contains all: " to output for clarity
    NUMBER_COMPARISON = auto()   # TODO: prepend how comparison is done to output for clarity
    DOES_NOT_CONTAIN = auto()
    STRING_MATCH_ONE_OF = auto() # TODO: Figure out how to display mismatch


class FieldResult(Enum):
    VALUE_MATCH = auto()
    VALUE_MISMATCH = auto()
    COLLECTION_MISMATCH = auto()
    FIELD_MISSING = auto()


# specifies whether the field is a value or a collection of values
class FieldType(Enum):
    VALUE = auto()
    COLLECTION = auto()


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


class ValidatedMessage:
    def __init__(self, description: str, name: str, subtitle: str,
                 datetime: str):
        self.description = description
        self.name = name
        self.subtitle = subtitle
        self.datetime = datetime
        self.fields = []

    def add_validated_field(self, field: ValidatedField):
        self.fields.append(field)

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
    return s[len(prefix):] if s.startswith(prefix) else s


def remove_space_equals_prefix(s):
    return re.sub('^(\\s|=)*', '', s)


def remove_parens(s):
    return re.sub('\\(|\\)', '', s)


class ParsedMessage:
    def __init__(self, description: str, name: str, subtitle: str,
                 datetime: str, saved_values: dict):
        self.description = description
        self.name = name
        self.subtitle = subtitle
        self.datetime = datetime
        self.fields = []
        self.saved_values = saved_values

    def add_parsed_field(self, field: ParsedField):
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
    
    def __init__(self, index: int, packet_type: Any, packet_length: int, name: str, subtitle: str, datetime: str, packet_text: str):
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
        parsed, flags = self.parse_payload()
        val = {
            "_flags": flags, 
            **parsed
        }
        print(json.dumps(val, indent=2))
        sys.stdout.flush()
        sys.stderr.flush()
        return val
        
    def to_json(self):
        try:
            parsedPayload, flags = self.parse_payload()
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
            if(val.lower() == 'true'):
                return True
            elif(val.lower() == 'false'):
                return False
            elif(re.match(ParsedRawMessage.INT_REGEX, val)):
                int_val = int(val)
                if int_val < -9223372036854775808 or int_val > 9223372036854775807:
                    print(f'Huge {self.index}: {val}')
                    return val
                return int_val
            elif(re.match(ParsedRawMessage.FLOAT_REGEX, val)):
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
                    else: _insert_cleaned(_obj, key, val)
            
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
        
        def _QtraceMessage(lines: list[str],_obj:dict):
            #
            
            
            if len(lines) > 0:
                i =0
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
                    rows=line.split('|')
                    j=0
                    while j < len(rows):
                        rowdata = rows[j]
                        if j == 0:
                            if 'Sub-ID:1' in rowdata:
                                _obj['Subscription ID']=1
                            elif 'Sub-ID:0' in rowdata:
                                _obj['Subscription ID']=0
                        elif j< 3:
                            if ':' in rowdata:
                                key_value = rowdata.split(':')
                                key = key_value[0].strip().replace('{','')
                                
                                value = ':'.join( key_value[1:]).strip().replace('}','')
                                _obj[key] = value
                                if key == 'tput.kbps':
                                    _obj['Sub-Type']=key
                                    valueArr = value.replace('[','').replace(']','').split(';')
                                    k=0
                                    while k < len(valueArr):
                                        valueLine = valueArr[k]
                                        if ':' in valueLine:
                                            key_value = valueLine.split(':')
                                            keyChild = key_value[0].strip()
                                            valueChild = ':'.join( key_value[1:]).strip().replace('}','')
                                            _obj[keyChild] = valueChild
                                        k +=1
                                        
                                    
                            else:
                                if rowdata != ' NR ':
                                    _obj['Sub-Type']=rowdata.strip()
                        else:
                            if ':' in rowdata:
                                key_value = rowdata.split(':')
                                key = key_value[0].strip()
                                value =   ':'.join( key_value[1:]).strip()
                                _obj[key] = value
                        j +=1
                    i += 1
                return True
            else:
                return False
                
        def _QtraceEvent(lines: list[str],_obj:dict):   
            if len(lines) > 0:
                i =0
                while i < len(lines):
                    line = lines[i].strip()
                    if  '     QEvent 0X' in line:
                        self.subtitle = 'QEvent'
                        _obj['Sub-Type'] = line.split('|')[1].strip()
                    else:
                        return False
                    rows=line.split('|')
                    j=0
                    while j < len(rows):
                        rowdata = rows[j]
                        if j == 0:
                            if 'Sub-ID:1' in rowdata:
                                _obj['Subscription ID']=1
                            elif 'Sub-ID:0' in rowdata:
                                _obj['Subscription ID']=0
                            if 'Misc-ID:1' in rowdata:
                                _obj['Misc ID']=1
                            elif 'Misc-ID:0' in rowdata:
                                _obj['Misc ID']=0
                        else:
                            if '=' in rowdata:
                                key_value = rowdata.split('=')
                                key = key_value[0].strip()
                                if '=' in key_value[1]:
                                    otherData =  '='.join( key_value[1:]).strip()
                                    otherRows = otherData.split(' ')
                                    rows += otherRows[1:]
                                else:
                                    value = key_value[1].strip()
                            elif ':' in rowdata:
                                if '[' in  rowdata and ']' not in rowdata :
                                    j +=1
                                    rowdata =  rowdata +',' + rows[j]
                                key_value = rowdata.split(':')
                                key = key_value[0].strip()
                                value =   ':'.join( key_value[1:]).strip()
                                _obj[key] = value           
                                    
                        j +=1            
                                
                                
                                
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
                            else: return deep_key, deep_obj
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
                            key, content = _deep(lines[i:j+1])
                            
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
                    lines.reverse()
                    bottom_most_names_and_len: list[(str, int)] = []
                    for r_index, row in enumerate(lines):
                        row = row.strip()
                        row = row[1:len(row)-1]
                        split_row = row.split(TABLE_VERTICAL_BOUNDARY)
                        skipped_bottom_cols = 0
                        for c_index, col_name in enumerate(split_row):
                            if r_index > 0:
                                len_of_current = len(col_name)
                                index = c_index + skipped_bottom_cols
                                while len_of_current > 0:
                                    len_of_bottom_most_col = bottom_most_names_and_len[index][1] + 1 # add 1 to compensate for removed TABLE_BOUNDARY character
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
                
                columns = _parse_cols(lines[table_cols_start:table_cols_end+1])
                
                all_parsed_rows: List[Dict[str, Any]] = []
                
                # parse table data rows into arrays of objects with key-val
                for i in range(table_rows_start, table_rows_end):
                    row = lines[i].strip()
                    row = row[1:len(row)-1]
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
                    table_name = lines[table_start].strip() # the previous line is the table name
                    continue
                
                # table columns end, aka ---------------
                if not table_cols_end and re.match(TABLE_BOUNDARIES_REGEX, line):
                    table_cols_end = i - 1
                    table_rows_start = i + 1
                    table_rows_end = table_rows_start + 1
                    while table_rows_end < len(lines) and re.match(TABLE_VERTICAL_BOUNDARY_REGEX, lines[table_rows_end].strip()):
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
        def _PARSE(lines: list[str], _obj: dict):
            flags = {}
            # parse payloads that are encoded in hex
            if _hex_payload(lines):
               return 
            if (self.name == 'QTrace Messages' ) and _QtraceMessage(lines,_obj):
                print('QTrace Messages',_obj)
            if (self.name == 'QTrace Event' ) and _QtraceEvent(lines,_obj):
                print('QTrace Event',_obj)
            if (self.packet_type_hex.lower() in TABLE_PACKET_TYPES):
                f = _tables(lines, _obj)
                flags = {**flags, **f}
            # else parse class/struct type data and generic key-value pairs
            else: _struct_or_generic_parse(lines, _obj)
            
            if self.packet_config:
                _apply_parsing_config(_obj, flags)
            
            return flags
            
        # start here
    
        # remove empty (only whitespace) lines
        raw_lines = [s for s in self.packet_text.splitlines() if s.strip() != ""]
            
        # parse payload      
        # skip first line, because first line content is main content 
        # (packet type, length, etc), and is already parsed  
        flags = _PARSE(raw_lines[1:], payload)
                    
        return payload, flags


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
                    packet_config[key] = val
        return packet_config
    
    def test_table_parsing():
        messages: List[ParsedRawMessage] = []

#         msg = ParsedRawMessage(index = 0, packet_type = "0xB193", packet_length=100, name="Unrecognized", subtitle="", datetime="", packet_text=
# """2023 Jun 16  20:16:42.611  [EB]  0xB193  Unrecognized\r\nSubscription ID = 1\r\n\tThis packet is currently not supported.\r\n""")
#         messages.append(msg)

#         msg = ParsedRawMessage(index = 0, packet_type = "0xB80B", packet_length=100, name="NR5G NAS MM5G Plain OTA Outgoing Msg", subtitle="Registration request", datetime="", packet_text=
# """2023 Jun  8  21:16:17.494  [CC]  0xB80B  NR5G NAS MM5G Plain OTA Outgoing Msg  --  Registration request
# Subscription ID = 2
# Misc ID         = 0
# pkt_version = 1 (0x1)
# rel_number = 15 (0xf)
# rel_version_major = 4 (0x4)
# rel_version_minor = 0 (0x0)
# prot_disc_type = 14 (0xe)
# ext_protocol_disc = 126 (0x7e)
# security_header = 0 (0x0)
# msg_type = 65 (0x41) (Registration request)
# nr5g_mm_msg
#   registration_req
#     ngKSI
#       tsc = 0 (0x0) (native sec context)
#       nas_key_set_id = 1 (0x1)
#     reg_type
#       FOR = 0 (0x0)
#       _5gs_reg_type = 2 (0x2) (mob reg updating)
#     _5gs_mob_id
#       ident_type = 2 (0x2) (5G_GUTI)
#       fill_1111 = 15 (0xf)
#       mcc_1 = 3 (0x3)
#       mcc_2 = 1 (0x1)
#       mcc_3 = 4 (0x4)
#       mnc_3 = 0 (0x0)
#       mnc_1 = 0 (0x0)
#       mnc_2 = 2 (0x2)
#       AMF_Region_ID = 255 (0xff)
#       AMF_SET_ID = 1 (0x1)
#       AMF_Pointer = 1 (0x1)
#       _5g_tmsi[0] = 224 (0xe0)
#       _5g_tmsi[1] = 0 (0x0)
#       _5g_tmsi[2] = 31 (0x1f)
#       _5g_tmsi[3] = 232 (0xe8)
#     non_current_key_set_id_incl = 0 (0x0)
#     _5gmm_capability_incl = 0 (0x0)
#     ue_security_cap_incl = 1 (0x1)
#     ue_security_cap
#       EA0_5G = 1 (0x1)
#       EA1_128_5G = 1 (0x1)
#       EA2_128_5G = 1 (0x1)
#       EA3_128_5G = 1 (0x1)
#       EA4_5G = 0 (0x0)
#       EA5_5G = 0 (0x0)
#       EA6_5G = 0 (0x0)
#       EA7_5G = 0 (0x0)
#       IA0_5G = 0 (0x0)
#       IA1_128_5G = 1 (0x1)
#       IA2_128_5G = 1 (0x1)
#       IA3_128_5G = 1 (0x1)
#       IA4_5G = 0 (0x0)
#       IA5_5G = 0 (0x0)
#       IA6_5G = 0 (0x0)
#       IA7_5G = 0 (0x0)
#       oct5_incl = 0 (0x0)
#       oct6_incl = 0 (0x0)
#     requested_nssai_incl = 0 (0x0)
#     last_visit_reg_tai_incl = 0 (0x0)
#     s1_ue_mwk_cap_incl = 0 (0x0)
#     uplink_data_status_incl = 0 (0x0)
#     pdu_session_status_incl = 0 (0x0)
#     mico_ind_incl = 0 (0x0)
#     ue_status_incl = 0 (0x0)
#     add_guti_inc = 0 (0x0)
#     allowed_pdu_session_status_inc = 0 (0x0)
#     ue_usage_setting_inc = 0 (0x0)
#     req_drx_params_inc = 0 (0x0)
#     eps_nas_msg_container_inc = 0 (0x0)
#     ladn_ind_inc = 0 (0x0)
#     payload_container_type_incl = 0 (0x0)
#     eps_nas_payload_container_inc = 0 (0x0)
#     nwk_slicing_ind_incl = 0 (0x0)
#     _5gs_update_type_incl = 0 (0x0)
#     mobile_station_class_mark2_incl = 0 (0x0)
#     supported_codes_incl = 0 (0x0)
#     nas_msg_container_incl = 1 (0x1)
#     nas_msg_container
#       num_nas_msg_container = 50 (0x32)
#       nas_msg_container[0] = 188 (0xbc)
#       nas_msg_container[1] = 104 (0x68)
#       nas_msg_container[2] = 135 (0x87)
#       nas_msg_container[3] = 94 (0x5e)
#       nas_msg_container[4] = 225 (0xe1)
#       nas_msg_container[5] = 207 (0xcf)
#       nas_msg_container[6] = 110 (0x6e)
#       nas_msg_container[7] = 203 (0xcb)
#       nas_msg_container[8] = 110 (0x6e)
#       nas_msg_container[9] = 203 (0xcb)
#       nas_msg_container[10] = 101 (0x65)
#       nas_msg_container[11] = 144 (0x90)
#       nas_msg_container[12] = 4 (0x4)
#       nas_msg_container[13] = 195 (0xc3)
#       nas_msg_container[14] = 237 (0xed)
#       nas_msg_container[15] = 214 (0xd6)
#       nas_msg_container[16] = 134 (0x86)
#       nas_msg_container[17] = 213 (0xd5)
#       nas_msg_container[18] = 77 (0x4d)
#       nas_msg_container[19] = 155 (0x9b)
#       nas_msg_container[20] = 232 (0xe8)
#       nas_msg_container[21] = 19 (0x13)
#       nas_msg_container[22] = 54 (0x36)
#       nas_msg_container[23] = 9 (0x9)
#       nas_msg_container[24] = 98 (0x62)
#       nas_msg_container[25] = 47 (0x2f)
#       nas_msg_container[26] = 167 (0xa7)
#       nas_msg_container[27] = 139 (0x8b)
#       nas_msg_container[28] = 149 (0x95)
#       nas_msg_container[29] = 128 (0x80)
#       nas_msg_container[30] = 45 (0x2d)
#       nas_msg_container[31] = 68 (0x44)
#       nas_msg_container[32] = 205 (0xcd)
#       nas_msg_container[33] = 148 (0x94)
#       nas_msg_container[34] = 151 (0x97)
#       nas_msg_container[35] = 16 (0x10)
#       nas_msg_container[36] = 90 (0x5a)
#       nas_msg_container[37] = 17 (0x11)
#       nas_msg_container[38] = 124 (0x7c)
#       nas_msg_container[39] = 213 (0xd5)
#       nas_msg_container[40] = 12 (0xc)
#       nas_msg_container[41] = 147 (0x93)
#       nas_msg_container[42] = 193 (0xc1)
#       nas_msg_container[43] = 50 (0x32)
#       nas_msg_container[44] = 148 (0x94)
#       nas_msg_container[45] = 48 (0x30)
#       nas_msg_container[46] = 221 (0xdd)
#       nas_msg_container[47] = 34 (0x22)
#       nas_msg_container[48] = 105 (0x69)
#       nas_msg_container[49] = 190 (0xbe)
#     eps_bearer_context_incl = 0 (0x0)
#     req_ext_drx_incl = 0 (0x0)
#     t3324_incl = 0 (0x0)
#     ue_radio_cap_id_incl = 0 (0x0)
#     req_mapped_nssai_incl = 0 (0x0)
#     add_info_req_incl = 0 (0x0)
#     wus_assistence_info_incl = 0 (0x0)
#     n5gc_ind_incl = 0 (0x0)
#     nbn1_mode_drx_incl = 0 (0x0)
#     ue_req_type_incl = 0 (0x0)
#     paging_restriction_incl = 0 (0x0)
#     serv_level_aa_incl = 0 (0x0)
#     nid_incl = 0 (0x0)
#     ms_determined_plmn_incl = 0 (0x0)
#     req_peips_assist_incl = 0 (0x0)""")
#         messages.append(msg)
        
#         msg = ParsedRawMessage(index = 0, packet_type = "0xB0ED", packet_length=100, name="LTE NAS EMM Plain OTA Outgoing Message", subtitle="Tracking area update complete Msg", datetime="", packet_text=
# """2023 Jun  8  21:16:25.115  [20]  0xB0ED  LTE NAS EMM Plain OTA Outgoing Message  --  Tracking area update complete Msg
# Subscription ID = 1
# pkt_version = 1 (0x1)
# rel_number = 9 (0x9)
# rel_version_major = 5 (0x5)
# rel_version_minor = 0 (0x0)
# security_header_or_skip_ind = 0 (0x0)
# prot_disc = 7 (0x7) (EPS mobility management messages)
# msg_type = 74 (0x4a) (Tracking area update complete)
# lte_emm_msg""")
#         messages.append(msg)
        

#         msg = ParsedRawMessage(index = 0, packet_type = "0xB821", packet_length=100, name="NR5G RRC OTA Packet", subtitle="DL_DCCH / RRCReconfiguration", datetime="", packet_text=
# """2023 Jun  8  21:14:27.078  [28]  0xB821  NR5G RRC OTA Packet  --  DL_DCCH / RRCReconfiguration
# Subscription ID = 2
# Misc ID         = 0
# Pkt Version = 12
# RRC Release Number.Major.minor = 15.10.0
# Radio Bearer ID = 1, Physical Cell ID = 1
# NR Cell Global Id = N/A
# Freq = 639936
# Sfn = 702, SubFrameNum = 0
# slot = 0
# PDU Number = DL_DCCH / RRCReconfiguration Message,    Msg Length = 485
# SIB Mask in SI =  0x00""")
#         messages.append(msg)
        
        
#         msg = ParsedRawMessage(index = 0, packet_type = "0xB173", packet_length=100, name="LTE PDSCH Stat Indication", subtitle="", datetime="", packet_text=
# """2023 Jun  8  21:16:02.785  [80]  0xB173  LTE PDSCH Stat Indication
# Subscription ID = 1
# Version      = 48
# Num Records  = 8
# Records
#    ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#    |   |        |     |   |      |Num      |       |Transport Blocks                                                                                                                |    |    |     |       |
#    |   |        |     |   |      |Transport|Serving|    |  |   |      |         |     |Discarded|                                   |           |       |   |   |          |        |    |    |Alt  |       |
#    |   |Subframe|Frame|Num|Num   |Blocks   |Cell   |HARQ|  |   |CRC   |         |TB   |reTx     |                                   |Did        |TB Size|   |Num|Modulation|ACK/NACK|PMCH|Area|TBS  |Alt MCS|
#    |#  |Num     |Num  |RBs|Layers|Present  |Index  |ID  |RV|NDI|Result|RNTI Type|Index|Present  |Discarded ReTx                     |Recombining|(bytes)|MCS|RBs|Type      |Decision|ID  |ID  |Index|Enabled|
#    ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#    |  0|       6|  155|  6|     2|        2|  PCELL|   5| 0|  1|  Pass|        C|    0|     None|                         NO_DISCARD|         No|    225| 17|  6|     64QAM|     ACK|    |    | NONE|  false|
#    |   |        |     |   |      |         |       |   5| 0|  0|  Pass|        C|    1|     None|                         NO_DISCARD|         No|    225| 17|  6|     64QAM|     ACK|    |    |     |       |
#    |  1|       8|  155|  3|     1|        1|  PCELL|   6| 0|  1|  Pass|        C|    0|     None|                         NO_DISCARD|         No|      7|  0|  3|      QPSK|     ACK|    |    | NONE|  false|
#    |  2|       6|  159|  3|     2|        2|  PCELL|   7| 0|  0|  Pass|        C|    0|     None|                         NO_DISCARD|         No|    113| 17|  3|     64QAM|     ACK|    |    | NONE|  false|
#    |   |        |     |   |      |         |       |   7| 0|  0|  Pass|        C|    1|     None|                         NO_DISCARD|         No|    113| 17|  3|     64QAM|     ACK|    |    |     |       |
#    |  3|       6|  163|  3|     1|        1|  PCELL|   0| 0|  0|  Pass|        C|    0|     None|                         NO_DISCARD|         No|    113| 17|  3|     64QAM|     ACK|    |    | NONE|  false|
#    |  4|       6|  167|  3|     1|        1|  PCELL|   1| 0|  0|  Pass|        C|    0|     None|                         NO_DISCARD|         No|    113| 17|  3|     64QAM|     ACK|    |    | NONE|  false|
#    |  5|       6|  171|  3|     1|        1|  PCELL|   2| 0|  1|  Pass|        C|    0|     None|                         NO_DISCARD|         No|    113| 17|  3|     64QAM|     ACK|    |    | NONE|  false|
#    |  6|       6|  175|  3|     1|        1|  PCELL|   3| 0|  0|  Pass|        C|    0|     None|                         NO_DISCARD|         No|    113| 17|  3|     64QAM|     ACK|    |    | NONE|  false|
#    |  7|       6|  179|  3|     1|        1|  PCELL|   4| 0|  1|  Pass|        C|    0|     None|                         NO_DISCARD|         No|    113| 17|  3|     64QAM|     ACK|    |    | NONE|  false|

# """)
#         messages.append(msg)

#         msg = ParsedRawMessage(index = 0, packet_type = "0xB063", packet_length=100, name="LTE MAC DL Transport Block", subtitle="", datetime="", packet_text=
# """2023 Jun  8  21:15:55.505  [8F]  0xB063  LTE MAC DL Transport Block
# Subscription ID = 1
# Version = 50
# TB Log Buff
#    Config Info
#       Num Tb = 11
#       Reason = 0
#    TB Info[0]
#       TB Common Info[0]
#          -----------------------------------------------------------------------------------------
#          |   |           |           |     |        |       |               |  |    |Num|        |
#          |   |           |Num Pad    |     |        |Reparse|               |CC|HARQ|MAC|MAC Hdr |
#          |#  |TB Size    |Bytes      |Frame|SubFrame|Flag   |RNTI Type      |ID|ID  |Sdu|Len     |
#          -----------------------------------------------------------------------------------------
#          |  0|          7|          1|  474|       4|      1|         C_RNTI| 0|   2|  1|       3|

#       MAC Sdu Info[0]
#          MAC Sdu Info Table[0]
#             --------------------------------------------------------------------------------------------------------------
#             |   |                                  |SDU CE Info                                          |               |
#             |   |                                  |RLC PDCP Info                                |       |               |
#             |   |MAC Common Info                   |       |  | |  | |  |   |       |Num |       |       |Dynamic Log    |
#             |   |Is |                      |       |       |  | |  | |  |   |       |PDCP|Num    |Mac CE |Info           |
#             |#  |MCE|LCID                  |Sdu Len|SN     |DC|P|RF|E|FI|LSF|SO     |Grp |NLOs   |Payload|Li Num|Li Len  |
#             --------------------------------------------------------------------------------------------------------------
#             |  0|  0|                     4|      3|      0| 0|0| 0|0| 0|  0|      0|   0|      0|       |      |        |

#    TB Info[1]
#       TB Common Info[0]
#          -----------------------------------------------------------------------------------------
#          |   |           |           |     |        |       |               |  |    |Num|        |
#          |   |           |Num Pad    |     |        |Reparse|               |CC|HARQ|MAC|MAC Hdr |
#          |#  |TB Size    |Bytes      |Frame|SubFrame|Flag   |RNTI Type      |ID|ID  |Sdu|Len     |
#          -----------------------------------------------------------------------------------------
#          |  0|        113|          0|  474|       6|      1|         C_RNTI| 0|   3|  1|       3|

#       MAC Sdu Info[0]
#          MAC Sdu Info Table[0]
#             --------------------------------------------------------------------------------------------------------------
#             |   |                                  |SDU CE Info                                          |               |
#             |   |                                  |RLC PDCP Info                                |       |               |
#             |   |MAC Common Info                   |       |  | |  | |  |   |       |Num |       |       |Dynamic Log    |
#             |   |Is |                      |       |       |  | |  | |  |   |       |PDCP|Num    |Mac CE |Info           |
#             |#  |MCE|LCID                  |Sdu Len|SN     |DC|P|RF|E|FI|LSF|SO     |Grp |NLOs   |Payload|Li Num|Li Len  |
#             --------------------------------------------------------------------------------------------------------------
#             |  0|  0|                     4|    110|   8385| 1|1| 0|0| 0|  0|      0|   1|      1|       |     1|     107|

#          PDCP Group Info[0]
#             Group[0]
#                Group Type         =    PDCP_START_INFO
#                PDCP DC bit        = 1
#                PDCP SN            =               3513
#             Group[1]
#                Group Type         =      PDCP_END_INFO
#                PDCP DC bit        = 1
#                PDCP SN            =               3513
#    TB Info[2]
#       TB Common Info[0]
#          -----------------------------------------------------------------------------------------
#          |   |           |           |     |        |       |               |  |    |Num|        |
#          |   |           |Num Pad    |     |        |Reparse|               |CC|HARQ|MAC|MAC Hdr |
#          |#  |TB Size    |Bytes      |Frame|SubFrame|Flag   |RNTI Type      |ID|ID  |Sdu|Len     |
#          -----------------------------------------------------------------------------------------
#          |  0|        113|         28|  476|       7|      1|         C_RNTI| 0|   5|  1|       3|

#       MAC Sdu Info[0]
#          MAC Sdu Info Table[0]
#             --------------------------------------------------------------------------------------------------------------
#             |   |                                  |SDU CE Info                                          |               |
#             |   |                                  |RLC PDCP Info                                |       |               |
#             |   |MAC Common Info                   |       |  | |  | |  |   |       |Num |       |       |Dynamic Log    |
#             |   |Is |                      |       |       |  | |  | |  |   |       |PDCP|Num    |Mac CE |Info           |
#             |#  |MCE|LCID                  |Sdu Len|SN     |DC|P|RF|E|FI|LSF|SO     |Grp |NLOs   |Payload|Li Num|Li Len  |
#             --------------------------------------------------------------------------------------------------------------
#             |  0|  0|                     4|     82|   8386| 1|1| 0|0| 0|  0|      0|   1|      1|       |     1|      79|

#          PDCP Group Info[0]
#             Group[0]
#                Group Type         =    PDCP_START_INFO
#                PDCP DC bit        = 1
#                PDCP SN            =               3514
#             Group[1]
#                Group Type         =      PDCP_END_INFO
#                PDCP DC bit        = 1
#                PDCP SN            =               3514
#    TB Info[3]
#       TB Common Info[0]
#          -----------------------------------------------------------------------------------------
#          |   |           |           |     |        |       |               |  |    |Num|        |
#          |   |           |Num Pad    |     |        |Reparse|               |CC|HARQ|MAC|MAC Hdr |
#          |#  |TB Size    |Bytes      |Frame|SubFrame|Flag   |RNTI Type      |ID|ID  |Sdu|Len     |
#          -----------------------------------------------------------------------------------------
#          |  0|        113|          0|  477|       0|      1|         C_RNTI| 0|   6|  1|       2|

#       MAC Sdu Info[0]
#          MAC Sdu Info Table[0]
#             --------------------------------------------------------------------------------------------------------------
#             |   |                                  |SDU CE Info                                          |               |
#             |   |                                  |RLC PDCP Info                                |       |               |
#             |   |MAC Common Info                   |       |  | |  | |  |   |       |Num |       |       |Dynamic Log    |
#             |   |Is |                      |       |       |  | |  | |  |   |       |PDCP|Num    |Mac CE |Info           |
#             |#  |MCE|LCID                  |Sdu Len|SN     |DC|P|RF|E|FI|LSF|SO     |Grp |NLOs   |Payload|Li Num|Li Len  |
#             --------------------------------------------------------------------------------------------------------------
#             |  0|  0|                     4|    111|   8387| 1|1| 0|0| 0|  0|      0|   1|      1|       |     1|     108|

#          PDCP Group Info[0]
#             Group[0]
#                Group Type         =    PDCP_START_INFO
#                PDCP DC bit        = 1
#                PDCP SN            =               3515
#             Group[1]
#                Group Type         =      PDCP_END_INFO
#                PDCP DC bit        = 1
#                PDCP SN            =               3515
#    TB Info[4]
#       TB Common Info[0]
#          -----------------------------------------------------------------------------------------
#          |   |           |           |     |        |       |               |  |    |Num|        |
#          |   |           |Num Pad    |     |        |Reparse|               |CC|HARQ|MAC|MAC Hdr |
#          |#  |TB Size    |Bytes      |Frame|SubFrame|Flag   |RNTI Type      |ID|ID  |Sdu|Len     |
#          -----------------------------------------------------------------------------------------
#          |  0|        113|          0|  477|       3|      1|         C_RNTI| 0|   7|  2|       4|

#       MAC Sdu Info[0]
#          MAC Sdu Info Table[0]
#             --------------------------------------------------------------------------------------------------------------
#             |   |                                  |SDU CE Info                                          |               |
#             |   |                                  |RLC PDCP Info                                |       |               |
#             |   |MAC Common Info                   |       |  | |  | |  |   |       |Num |       |       |Dynamic Log    |
#             |   |Is |                      |       |       |  | |  | |  |   |       |PDCP|Num    |Mac CE |Info           |
#             |#  |MCE|LCID                  |Sdu Len|SN     |DC|P|RF|E|FI|LSF|SO     |Grp |NLOs   |Payload|Li Num|Li Len  |
#             --------------------------------------------------------------------------------------------------------------
#             |  0|  0|                     4|      3|      0| 0|0| 0|1| 0|  0|      0|   0|      0|       |      |        |

#       MAC Sdu Info[1]
#          MAC Sdu Info Table[0]
#             --------------------------------------------------------------------------------------------------------------
#             |   |                                  |SDU CE Info                                          |               |
#             |   |                                  |RLC PDCP Info                                |       |               |
#             |   |MAC Common Info                   |       |  | |  | |  |   |       |Num |       |       |Dynamic Log    |
#             |   |Is |                      |       |       |  | |  | |  |   |       |PDCP|Num    |Mac CE |Info           |
#             |#  |MCE|LCID                  |Sdu Len|SN     |DC|P|RF|E|FI|LSF|SO     |Grp |NLOs   |Payload|Li Num|Li Len  |
#             --------------------------------------------------------------------------------------------------------------
#             |  0|  0|                     4|    106|   8388| 1|0| 0|0| 1|  0|      0|   1|      1|       |     1|     103|

#          PDCP Group Info[0]
#             Group[0]
#                Group Type         =   PDCP_HEADER_INFO
#                FIRST TWO BYTES    =             0xBC8D
#    TB Info[5]
#       TB Common Info[0]
#          -----------------------------------------------------------------------------------------
#          |   |           |           |     |        |       |               |  |    |Num|        |
#          |   |           |Num Pad    |     |        |Reparse|               |CC|HARQ|MAC|MAC Hdr |
#          |#  |TB Size    |Bytes      |Frame|SubFrame|Flag   |RNTI Type      |ID|ID  |Sdu|Len     |
#          -----------------------------------------------------------------------------------------
#          |  0|         57|         41|  477|       3|      1|         C_RNTI| 0|   7|  1|       3|

#       MAC Sdu Info[0]
#          MAC Sdu Info Table[0]
#             --------------------------------------------------------------------------------------------------------------
#             |   |                                  |SDU CE Info                                          |               |
#             |   |                                  |RLC PDCP Info                                |       |               |
#             |   |MAC Common Info                   |       |  | |  | |  |   |       |Num |       |       |Dynamic Log    |
#             |   |Is |                      |       |       |  | |  | |  |   |       |PDCP|Num    |Mac CE |Info           |
#             |#  |MCE|LCID                  |Sdu Len|SN     |DC|P|RF|E|FI|LSF|SO     |Grp |NLOs   |Payload|Li Num|Li Len  |
#             --------------------------------------------------------------------------------------------------------------
#             |  0|  0|                     4|     13|   8389| 1|1| 0|0| 2|  0|      0|   1|      1|       |     1|      10|

#          PDCP Group Info[0]
#             Group[0]
#                Group Type         = PDCP_FRAG_TAIL_INNER_INFO
#                FIRST TWO BYTES    =             0xCC16
#    TB Info[6]
#       TB Common Info[0]
#          -----------------------------------------------------------------------------------------
#          |   |           |           |     |        |       |               |  |    |Num|        |
#          |   |           |Num Pad    |     |        |Reparse|               |CC|HARQ|MAC|MAC Hdr |
#          |#  |TB Size    |Bytes      |Frame|SubFrame|Flag   |RNTI Type      |ID|ID  |Sdu|Len     |
#          -----------------------------------------------------------------------------------------
#          |  0|        113|          0|  477|       7|      1|         C_RNTI| 0|   0|  1|       2|

#       MAC Sdu Info[0]
#          MAC Sdu Info Table[0]
#             --------------------------------------------------------------------------------------------------------------
#             |   |                                  |SDU CE Info                                          |               |
#             |   |                                  |RLC PDCP Info                                |       |               |
#             |   |MAC Common Info                   |       |  | |  | |  |   |       |Num |       |       |Dynamic Log    |
#             |   |Is |                      |       |       |  | |  | |  |   |       |PDCP|Num    |Mac CE |Info           |
#             |#  |MCE|LCID                  |Sdu Len|SN     |DC|P|RF|E|FI|LSF|SO     |Grp |NLOs   |Payload|Li Num|Li Len  |
#             --------------------------------------------------------------------------------------------------------------
#             |  0|  0|                     4|    111|   8390| 1|0| 0|0| 1|  0|      0|   1|      1|       |     1|     108|

#          PDCP Group Info[0]
#             Group[0]
#                Group Type         =   PDCP_HEADER_INFO
#                FIRST TWO BYTES    =             0xBD8D
#    TB Info[7]
#       TB Common Info[0]
#          -----------------------------------------------------------------------------------------
#          |   |           |           |     |        |       |               |  |    |Num|        |
#          |   |           |Num Pad    |     |        |Reparse|               |CC|HARQ|MAC|MAC Hdr |
#          |#  |TB Size    |Bytes      |Frame|SubFrame|Flag   |RNTI Type      |ID|ID  |Sdu|Len     |
#          -----------------------------------------------------------------------------------------
#          |  0|         57|         40|  477|       7|      1|         C_RNTI| 0|   0|  1|       3|

#       MAC Sdu Info[0]
#          MAC Sdu Info Table[0]
#             --------------------------------------------------------------------------------------------------------------
#             |   |                                  |SDU CE Info                                          |               |
#             |   |                                  |RLC PDCP Info                                |       |               |
#             |   |MAC Common Info                   |       |  | |  | |  |   |       |Num |       |       |Dynamic Log    |
#             |   |Is |                      |       |       |  | |  | |  |   |       |PDCP|Num    |Mac CE |Info           |
#             |#  |MCE|LCID                  |Sdu Len|SN     |DC|P|RF|E|FI|LSF|SO     |Grp |NLOs   |Payload|Li Num|Li Len  |
#             --------------------------------------------------------------------------------------------------------------
#             |  0|  0|                     4|     14|   8391| 1|1| 0|0| 2|  0|      0|   1|      1|       |     1|      11|

#          PDCP Group Info[0]
#             Group[0]
#                Group Type         = PDCP_FRAG_TAIL_INNER_INFO
#                FIRST TWO BYTES    =             0x60BB
#    TB Info[8]
#       TB Common Info[0]
#          -----------------------------------------------------------------------------------------
#          |   |           |           |     |        |       |               |  |    |Num|        |
#          |   |           |Num Pad    |     |        |Reparse|               |CC|HARQ|MAC|MAC Hdr |
#          |#  |TB Size    |Bytes      |Frame|SubFrame|Flag   |RNTI Type      |ID|ID  |Sdu|Len     |
#          -----------------------------------------------------------------------------------------
#          |  0|        113|          0|  477|       9|      1|         C_RNTI| 0|   1|  1|       2|

#       MAC Sdu Info[0]
#          MAC Sdu Info Table[0]
#             --------------------------------------------------------------------------------------------------------------
#             |   |                                  |SDU CE Info                                          |               |
#             |   |                                  |RLC PDCP Info                                |       |               |
#             |   |MAC Common Info                   |       |  | |  | |  |   |       |Num |       |       |Dynamic Log    |
#             |   |Is |                      |       |       |  | |  | |  |   |       |PDCP|Num    |Mac CE |Info           |
#             |#  |MCE|LCID                  |Sdu Len|SN     |DC|P|RF|E|FI|LSF|SO     |Grp |NLOs   |Payload|Li Num|Li Len  |
#             --------------------------------------------------------------------------------------------------------------
#             |  0|  0|                     4|    111|   8392| 1|0| 0|0| 1|  0|      0|   1|      1|       |     1|     108|

#          PDCP Group Info[0]
#             Group[0]
#                Group Type         =   PDCP_HEADER_INFO
#                FIRST TWO BYTES    =             0xBE8D
#    TB Info[9]
#       TB Common Info[0]
#          -----------------------------------------------------------------------------------------
#          |   |           |           |     |        |       |               |  |    |Num|        |
#          |   |           |Num Pad    |     |        |Reparse|               |CC|HARQ|MAC|MAC Hdr |
#          |#  |TB Size    |Bytes      |Frame|SubFrame|Flag   |RNTI Type      |ID|ID  |Sdu|Len     |
#          -----------------------------------------------------------------------------------------
#          |  0|         57|         48|  477|       9|      1|         C_RNTI| 0|   1|  1|       3|

#       MAC Sdu Info[0]
#          MAC Sdu Info Table[0]
#             --------------------------------------------------------------------------------------------------------------
#             |   |                                  |SDU CE Info                                          |               |
#             |   |                                  |RLC PDCP Info                                |       |               |
#             |   |MAC Common Info                   |       |  | |  | |  |   |       |Num |       |       |Dynamic Log    |
#             |   |Is |                      |       |       |  | |  | |  |   |       |PDCP|Num    |Mac CE |Info           |
#             |#  |MCE|LCID                  |Sdu Len|SN     |DC|P|RF|E|FI|LSF|SO     |Grp |NLOs   |Payload|Li Num|Li Len  |
#             --------------------------------------------------------------------------------------------------------------
#             |  0|  0|                     4|      6|   8393| 1|1| 0|0| 2|  0|      0|   1|      1|       |     1|       3|

#          PDCP Group Info[0]
#             Group[0]
#                Group Type         = PDCP_FRAG_TAIL_INNER_INFO
#                FIRST TWO BYTES    =             0x50CA
#    TB Info[10]
#       TB Common Info[0]
#          -----------------------------------------------------------------------------------------
#          |   |           |           |     |        |       |               |  |    |Num|        |
#          |   |           |Num Pad    |     |        |Reparse|               |CC|HARQ|MAC|MAC Hdr |
#          |#  |TB Size    |Bytes      |Frame|SubFrame|Flag   |RNTI Type      |ID|ID  |Sdu|Len     |
#          -----------------------------------------------------------------------------------------
#          |  0|         18|          2|  475|       1|      0|         C_RNTI| 0|   4|  1|       3|

#       MAC Sdu Info[0]
#          MAC Sdu Info Table[0]
#             --------------------------------------------------------------------------------------------------------------
#             |   |                                  |SDU CE Info                                          |               |
#             |   |                                  |RLC PDCP Info                                |       |               |
#             |   |MAC Common Info                   |       |  | |  | |  |   |       |Num |       |       |Dynamic Log    |
#             |   |Is |                      |       |       |  | |  | |  |   |       |PDCP|Num    |Mac CE |Info           |
#             |#  |MCE|LCID                  |Sdu Len|SN     |DC|P|RF|E|FI|LSF|SO     |Grp |NLOs   |Payload|Li Num|Li Len  |
#             --------------------------------------------------------------------------------------------------------------
#             |  0|  0|                     5|     14|    243| 1|0| 0|0| 0|  0|      0|   1|      1|       |     1|      12|

#          PDCP Group Info[0]
#             Group[0]
#                Group Type         =    PDCP_START_INFO
#                PDCP DC bit        = 1
#                PDCP SN            =                237
# """)
#         messages.append(msg)
        
#         msg = ParsedRawMessage(index = 0, packet_type = "0xB0EC", packet_length=100, name="LTE NAS EMM Plain OTA Incoming Message", subtitle="Tracking area update accept Msg", datetime="", packet_text=
# """2023 Jun  8  21:16:18.723  [A5]  0xB0EC  LTE NAS EMM Plain OTA Incoming Message  --  Tracking area update accept Msg
# Subscription ID = 1
# pkt_version = 1 (0x1)
# rel_number = 9 (0x9)
# rel_version_major = 5 (0x5)
# rel_version_minor = 0 (0x0)
# security_header_or_skip_ind = 0 (0x0)
# prot_disc = 7 (0x7) (EPS mobility management messages)
# msg_type = 73 (0x49) (Tracking area update accept)
# lte_emm_msg
#   emm_ta_update_accept
#     eps_update_result = 0 (0x0) (TA updated)
#     t3412_incl = 1 (0x1)
#     t3412
#       unit = 2 (0x2)
#       timer_value = 9 (0x9)
#     guti_incl = 0 (0x0)
#     tai_list_incl = 1 (0x1)
#     tai_list
#       num_tai_list = 1 (0x1)
#       tai_list[0]
#         list_type = 1 (0x1)
#         num_element = 0 (0x0)
#         mcc_mnc
#           mcc_1 = 3 (0x3)
#           mcc_2 = 1 (0x1)
#           mcc_3 = 1 (0x1)
#           mnc_3 = 0 (0x0)
#           mnc_1 = 4 (0x4)
#           mnc_2 = 8 (0x8)
#         tac[0] = 3586 (0xe02)
#     eps_bearer_context_incl = 1 (0x1)
#     eps_bearer_context_status
#       len_eps_bearer_context = 2 (0x2)
#       ebi_7 = 0 (0x0)
#       ebi_6 = 1 (0x1)
#       ebi_5 = 1 (0x1)
#       ebi_4 = 0 (0x0)
#       ebi_3 = 0 (0x0)
#       ebi_2 = 0 (0x0)
#       ebi_1 = 0 (0x0)
#       ebi_0 = 0 (0x0)
#       ebi_15 = 0 (0x0)
#       ebi_14 = 0 (0x0)
#       ebi_13 = 0 (0x0)
#       ebi_12 = 0 (0x0)
#       ebi_11 = 0 (0x0)
#       ebi_10 = 0 (0x0)
#       ebi_9 = 0 (0x0)
#       ebi_8 = 0 (0x0)
#     loc_area_id_incl = 0 (0x0)
#     mod_id_incl = 0 (0x0)
#     emm_cause_incl = 0 (0x0)
#     T3402_incl = 1 (0x1)
#     gprs_timer3402
#       unit = 1 (0x1)
#       timer_value = 12 (0xc)
#     T3423_incl = 0 (0x0)
#     equ_plmns_incl = 0 (0x0)
#     emergnecy_num_list_incl = 1 (0x1)
#     emergency_num_list
#       count = 1 (0x1)
#       data[0]
#         length = 3 (0x3)
#         emer_serv_cat_val = 0 (0x0)
#         number[0] = 9 (0x9)
#         number[1] = 1 (0x1)
#         number[2] = 1 (0x1)
#         number[3] = 15 (0xf)
#     eps_netwk_feature_support_incl = 1 (0x1)
#     eps_netwk_feature_support
#       length = 2 (0x2)
#       CPCIoT = 0 (0x0)
#       ERwoPDN = 0 (0x0)
#       ESRPS = 0 (0x0)
#       CS_LCS = 0 (0x0) (No info about support of loc service via cs is available)
#       EPC_LCS = 0 (0x0) (Location Services via EPC not supported)
#       EMC_BS = 1 (0x1) (Emergency bearer services in S1 Mode supported)
#       IMSVoPS = 1 (0x1) (IMS Vo PS Session in S1 Mode supported)
#       _15Bearers = 0 (0x0)
#       IWKN26 = 0 (0x0)
#       RestrictDCNR = 0 (0x0)
#       RestrictEC = 0 (0x0)
#       ePCO = 1 (0x1)
#       HC_CPCIoT = 0 (0x0)
#       S1_Udata = 0 (0x0)
#       UPCIoT = 0 (0x0)
#     add_update_result_incl = 0 (0x0)
#     t3412_ext_incl = 0 (0x0)
#     t3324_incl = 0 (0x0)
#     ext_drx_par_incl = 0 (0x0)
#     header_cmp_config_status_incl = 0 (0x0)
#     dcn_id_incl = 0 (0x0)
#     sms_srvc_status_incl = 0 (0x0)
#     non_3gpp_access_emerg_num_policy_incl = 0 (0x0)
#     t3448_incl = 0 (0x0)
#     nwk_policy_incl = 0 (0x0)
#     t3447_ext_incl = 0 (0x0)
#     ext_emergency_number_incl = 0 (0x0)
#     cipher_ket_data_incl = 0 (0x0)

 
# """)
#         messages.append(msg)
        
#         msg = ParsedRawMessage(index = 0, packet_type = "0xB0ED", packet_length=100, name="LTE NAS EMM Plain OTA Outgoing Message", subtitle="Tracking area update request Msg", datetime="", packet_text=
# """
# 2023 Jun  8  21:16:25.001  [4B]  0xB0ED  LTE NAS EMM Plain OTA Outgoing Message  --  Tracking area update request Msg
# Subscription ID = 1
# pkt_version = 1 (0x1)
# rel_number = 9 (0x9)
# rel_version_major = 5 (0x5)
# rel_version_minor = 0 (0x0)
# security_header_or_skip_ind = 0 (0x0)
# prot_disc = 7 (0x7) (EPS mobility management messages)
# msg_type = 72 (0x48) (Tracking area update request)
# lte_emm_msg
#   emm_ta_update_req
#     tsc_asme = 0 (0x0) (cached sec context)
#     nas_key_set_id_asme = 0 (0x0)
#     active_flag = 0 (0x0)
#     eps_update_type = 0 (0x0) (TA updating)
#     old_guti
#       id_type = 6 (0x6) (GUTI)
#       odd_even_ind = 0 (0x0)
#       Guti_1111 = 15 (0xf)
#       mcc_1 = 3 (0x3)
#       mcc_2 = 1 (0x1)
#       mcc_3 = 1 (0x1)
#       mnc_3 = 0 (0x0)
#       mnc_1 = 4 (0x4)
#       mnc_2 = 8 (0x8)
#       MME_group_id = 64010 (0xfa0a)
#       MME_code = 19 (0x13)
#       m_tmsi = 3276050395 (0xc3448fdb)
#     key_set_id_incl = 0 (0x0)
#     gprs_cipher_key_incl_incl = 0 (0x0)
#     p_tmsi_sig_incl = 0 (0x0)
#     guti_incl = 0 (0x0)
#     nounce_incl = 0 (0x0)
#     ue_netwk_cap_incl = 1 (0x1)
#     ue_netwk_cap
#       EEA0 = 1 (0x1)
#       EEA1_128 = 1 (0x1)
#       EEA2_128 = 1 (0x1)
#       EEA3_128 = 1 (0x1)
#       EEA4 = 0 (0x0)
#       EEA5 = 0 (0x0)
#       EEA6 = 0 (0x0)
#       EEA7 = 0 (0x0)
#       EIA0 = 0 (0x0)
#       EIA1_128 = 1 (0x1)
#       EIA2_128 = 1 (0x1)
#       EIA3_128 = 1 (0x1)
#       EIA4 = 0 (0x0)
#       EIA5 = 0 (0x0)
#       EIA6 = 0 (0x0)
#       EIA7 = 0 (0x0)
#       oct5_incl = 1 (0x1)
#       UEA0 = 1 (0x1)
#       UEA1 = 1 (0x1)
#       UEA2 = 0 (0x0)
#       UEA3 = 0 (0x0)
#       UEA4 = 0 (0x0)
#       UEA5 = 0 (0x0)
#       UEA6 = 0 (0x0)
#       UEA7 = 0 (0x0)
#       oct6_incl = 1 (0x1)
#       UCS2 = 0 (0x0)
#       UIA1 = 1 (0x1)
#       UIA2 = 0 (0x0)
#       UIA3 = 0 (0x0)
#       UIA4 = 0 (0x0)
#       UIA5 = 0 (0x0)
#       UIA6 = 0 (0x0)
#       UIA7 = 0 (0x0)
#       oct7_incl = 1 (0x1)
#       ProSedd = 0 (0x0)
#       ProSe = 0 (0x0)
#       H_245_ASH = 0 (0x0)
#       ACC_CSFB = 1 (0x1)
#       LPP = 1 (0x1)
#       LCS = 0 (0x0)
#       vcc_1xsr = 0 (0x0)
#       NF = 0 (0x0)
#       oct8_incl = 1 (0x1)
#       ePCO = 1 (0x1)
#       HC_CPCIoT = 0 (0x0)
#       ERwoPDN = 0 (0x0)
#       S1_Udata = 0 (0x0)
#       UPCIoT = 0 (0x0)
#       CPCIoT = 0 (0x0)
#       Prose_Relay = 0 (0x0)
#       Prose_dc = 0 (0x0)
#       oct9_incl = 1 (0x1)
#       bearers = 1 (0x1)
#       SGC = 0 (0x0)
#       N1Mode = 1 (0x1)
#       DCNR = 1 (0x1)
#       Cp_Backoff = 0 (0x0)
#       Restric_IEC = 0 (0x0)
#       V2X_PCS = 0 (0x0)
#       multiDRB = 0 (0x0)
#       oct10_incl = 0 (0x0)
#       oct11_incl = 0 (0x0)
#       oct12_incl = 0 (0x0)
#       oct13_incl = 0 (0x0)
#       oct14_incl = 0 (0x0)
#       oct15_incl = 0 (0x0)
#     reg_tai_incl = 1 (0x1)
#     last_visited_reg_tai
#       mcc_mnc
#         mcc_1 = 3 (0x3)
#         mcc_2 = 1 (0x1)
#         mcc_3 = 1 (0x1)
#         mnc_3 = 0 (0x0)
#         mnc_1 = 4 (0x4)
#         mnc_2 = 8 (0x8)
#       tracking_area_id = 3586 (0xe02)
#     drx_params_incl = 1 (0x1)
#     drx_params
#       split_pg_cycle_code = 10 (0xa)
#       cycle_len_coeff = 0 (0x0)
#       split_on_ccch = 0 (0x0)
#       non_drx_timer = 0 (0x0)
#     ue_radio_info_needed_incl = 0 (0x0)
#     eps_bearer_context_incl = 1 (0x1)
#     eps_bearer_context_status
#       len_eps_bearer_context = 2 (0x2)
#       ebi_7 = 0 (0x0)
#       ebi_6 = 1 (0x1)
#       ebi_5 = 1 (0x1)
#       ebi_4 = 0 (0x0)
#       ebi_3 = 0 (0x0)
#       ebi_2 = 0 (0x0)
#       ebi_1 = 0 (0x0)
#       ebi_0 = 0 (0x0)
#       ebi_15 = 0 (0x0)
#       ebi_14 = 0 (0x0)
#       ebi_13 = 0 (0x0)
#       ebi_12 = 0 (0x0)
#       ebi_11 = 0 (0x0)
#       ebi_10 = 0 (0x0)
#       ebi_9 = 0 (0x0)
#       ebi_8 = 0 (0x0)
#     ms_netwk_cap_incl = 1 (0x1)
#     ms_netwk_cap
#       length = 4 (0x4)
#       r99 = 1 (0x1)
#       GEA1 bits
#         GEA/1 = 0 (0x0)
#       SM capabilities via dedicated channels = 1 (0x1)
#       SM capabilities via GPRS channels = 1 (0x1)
#       UCS2 support = 0 (0x0)
#       SS Screening Indicator = 1 (0x1)
#       SoLSA Capability = 0 (0x0)
#       Revision level indicator = 1 (0x1)
#       PFC feature mode = 1 (0x1)
#       Extended GEA bits
#         GEA/2 = 1 (0x1)
#         GEA/3 = 1 (0x1)
#         GEA/4 = 0 (0x0)
#         GEA/5 = 0 (0x0)
#         GEA/6 = 0 (0x0)
#         GEA/7 = 0 (0x0)
#       LCS VA capability = 0 (0x0)
#       PS inter-RAT HO from GERAN to UTRAN Iu mode capability = 0 (0x0)
#       PS inter-RAT HO from GERAN to E-UTRAN S1 mode capability = 0 (0x0)
#       EMM Combined procedures Capability = 1 (0x1)
#       ISR support = 1 (0x1)
#       SRVCC to GERAN/UTRAN capability = 0 (0x0)
#       EPC capability = 1 (0x1)
#       NF capability = 0 (0x0)
#       GERAN network sharing capability = 0 (0x0)
#       User plane integrity protection support = 0 (0x0)
#       GIA/4 = 0 (0x0)
#       GIA/5 = 0 (0x0)
#       GIA/6 = 0 (0x0)
#       GIA/7 = 0 (0x0)
#       ePCO IE indicator = 0 (0x0)
#       Restriction on use of enhanced coverage capability = 0 (0x0)
#       Dual connectivity of E-UTRA with NR capability = 1 (0x1)
#       spare_bits0_count = 0 (0x0)
#     old_loc_area_id_incl = 0 (0x0)
#     tmsi_stat_incl = 0 (0x0)
#     ms_class_mark2_incl = 0 (0x0)
#     ms_class_mark3_incl = 0 (0x0)
#     supp_codecs_incl = 0 (0x0)
#     add_update_type_incl = 0 (0x0)
#     voice_domain_pref_incl = 1 (0x1)
#     voice_domain_pref
#       length = 1 (0x1)
#       UE_usage_setting = 0 (0x0) (Voice centric)
#       voice_domain_pref_for_EUTRAN = 3 (0x3) (IMS PS Voice preferred, CS Voice as secondary)
#     old_guti_type_incl = 1 (0x1)
#     old_guti_type
#       guti_type = 0 (0x0) (Native GUTI)
#     dev_properties_incl = 0 (0x0)
#     ms_network_feature_incl = 1 (0x1)
#     ms_network_feature_support
#       ext_periodic_timers = 1 (0x1)
#     network_resource_id_container_incl = 0 (0x0)
#     t3324_incl = 0 (0x0)
#     t3412_ext_incl = 0 (0x0)
#     ext_drx_par_incl = 0 (0x0)
#     ue_add_security_cap_incl = 1 (0x1)
#     ue_add_security_cap
#       length = 4 (0x4)
#       _5G_EA0 = 1 (0x1)
#       _128_5G_EA1 = 1 (0x1)
#       _128_5G_EA2 = 1 (0x1)
#       _128_5G_EA3 = 1 (0x1)
#       _5G_EA4 = 0 (0x0)
#       _5G_EA5 = 0 (0x0)
#       _5G_EA6 = 0 (0x0)
#       _5G_EA7 = 0 (0x0)
#       _5G_EA8 = 0 (0x0)
#       _5G_EA9 = 0 (0x0)
#       _5G_EA10 = 0 (0x0)
#       _5G_EA11 = 0 (0x0)
#       _5G_EA12 = 0 (0x0)
#       _5G_EA13 = 0 (0x0)
#       _5G_EA14 = 0 (0x0)
#       _5G_EA15 = 0 (0x0)
#       _5G_IA0 = 0 (0x0)
#       _128_5G_IA1 = 1 (0x1)
#       _128_5G_IA2 = 1 (0x1)
#       _128_5G_IA3 = 1 (0x1)
#       _5G_IA4 = 0 (0x0)
#       _5G_IA5 = 0 (0x0)
#       _5G_IA6 = 0 (0x0)
#       _5G_IA7 = 0 (0x0)
#       _5G_IA8 = 0 (0x0)
#       _5G_IA9 = 0 (0x0)
#       _5G_IA10 = 0 (0x0)
#       _5G_IA11 = 0 (0x0)
#       _5G_IA12 = 0 (0x0)
#       _5G_IA13 = 0 (0x0)
#       _5G_IA14 = 0 (0x0)
#       _5G_IA15 = 0 (0x0)
#     ue_status_incl = 0 (0x0)
#     add_info_req_incl = 0 (0x0)
# """)
#         messages.append(msg)
        
#         msg = ParsedRawMessage(index = 0, packet_type = "0xB193", packet_length=100, name="LTE ML1 Serving Cell Meas Response", subtitle="", datetime="", packet_text=
#         """2021 Dec 30  20:27:47.721  [DC]  0xB193  LTE ML1 Serving Cell Meas Response
# Subscription ID = 1
# Version              = 1
# Number of SubPackets = 1
# SubPacket ID         = 25
# Serving Cell Measurement Result
#    Version = 24
#    SubPacket Size = 276 bytes
#    E-ARFCN                   = 66986
#    Num of Cell               = 1
#    Cells[0]
#       Physical Cell ID          = 132
#       Serving Cell Index        = PCell
#       Is Serving Cell           = 1
#       Current SFN               = 352
#       Current Subframe Number   = 9
#       Is Restricted             = false
#       Cell Timing[0]            = 166942
#       Cell Timing[1]            = 166942
#       Cell Timing SFN[0]        = 352
#       Cell Timing SFN[1]        = 352
#       Is 1Rx Mode               = 1
#       Inst RSRP Rx[0]           = -68.94 dBm
#       Inst RSRP Rx[1]           = -180.00 dBm
#       Inst Measured RSRP        = -68.94 dBm
#       Inst RSRQ Rx[0]           = -6.06 dB
#       Inst RSRQ Rx[1]           = -30.00 dB
#       Inst RSRQ                 = -6.06 dB
#       Inst RSSI Rx[0]           = -45.88 dBm
#       Inst RSSI Rx[1]           = -110.00 dBm
#       Inst RSSI                 = -45.88 dBm
#       Residual Frequency Error  = 16712
#       FTL SNR Rx[0]             = 24.40 dB
#       FTL SNR Rx[1]             = -20.00 dB
#       Projected Sir             = 0 dB
#       Post Ic Rsrq              = 4294967295 dB
# """)
#         messages.append(msg)
        
#         msg = ParsedRawMessage(index = 0, packet_type = "0xB825", packet_length=100, name="NR5G RRC Configuration Info", subtitle="", datetime="", packet_text=
#         """2023 Jun  8  08:09:23.441  [DF]  0xB825  NR5G RRC Configuration Info
# Subscription ID = 2
# Misc ID         = 0
# Major.Minor Version               = 2. 0
# Conn Config Info
#    State = IDLE
#    Config Status = true
#    Connectivity Mode = SA
#    Num Active SRB = 0
#    Num Active DRB = 0
#    MN MCG DRB IDs = NONE
#    SN MCG DRB IDs = NONE
#    MN SCG DRB IDs = NONE
#    SN SCG DRB IDs = NONE
#    MN Split DRB IDs = NONE
#    SN Split DRB IDs = NONE
#    LTE Serving Cell Info {
#       Num Bands = 0
#    }
#    Num Contiguous CC Groups = 0
#    Num Active CC = 0
#    Num Active RB = 0""")
#         messages.append(msg)
        
#         msg = ParsedRawMessage(index = 0, packet_type = "0xB173", packet_length=100, name="LTE PDSCH Stat Indication", subtitle="", datetime="", packet_text=
#         """2023 May 31  13:08:18.598  [E5]  0xB173  LTE PDSCH Stat Indication
#             Subscription ID = 1
#             Version      = 48
#             Num Records  = 3
#             Records
#             ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#             |   |        |     |   |      |Num      |       |Transport Blocks                                                                                                                |    |    |     |       |
#             |   |        |     |   |      |Transport|Serving|    |  |   |      |         |     |Discarded|                                   |           |       |   |   |          |        |    |    |Alt  |       |
#             |   |Subframe|Frame|Num|Num   |Blocks   |Cell   |HARQ|  |   |CRC   |         |TB   |reTx     |                                   |Did        |TB Size|   |Num|Modulation|ACK/NACK|PMCH|Area|TBS  |Alt MCS|
#             |#  |Num     |Num  |RBs|Layers|Present  |Index  |ID  |RV|NDI|Result|RNTI Type|Index|Present  |Discarded ReTx                     |Recombining|(bytes)|MCS|RBs|Type      |Decision|ID  |ID  |Index|Enabled|
#             ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#             |  0|       0|  512| 28|     4|        1|  PCELL|   1| 0|  0|  Pass|       SI|    0|     None|                         NO_DISCARD|         No|     47| 11| 28|      QPSK|     ACK|    |    | NONE|  false|
#             |  1|       5|  512|  8|     4|        1|  PCELL|   0| 0|  0|  Pass|       SI|    0|     None|                         NO_DISCARD|         No|     32|  8|  8|      QPSK|     ACK|    |    | NONE|  false|
#             |  2|       0|  514| 28|     4|        1|  PCELL|   1| 0|  0|  Pass|       SI|    0|     None|                         NO_DISCARD|         No|     47| 11| 28|      QPSK|     ACK|    |    | NONE|  false|

#             """)
#         messages.append(msg)
        
#         msg = ParsedRawMessage(index = 0, packet_type = "0xB173", packet_length=100, name="LTE PDSCH Stat Indication", subtitle="", datetime="", packet_text=
#         """2023 Jun  8  21:13:55.447  [C6]  0xB173  LTE PDSCH Stat Indication
#         Subscription ID = 1
#         Version      = 48
#         Num Records  = 1
#         Records
#         ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#         |   |        |     |   |      |Num      |       |Transport Blocks                                                                                                                |    |    |     |       |
#         |   |        |     |   |      |Transport|Serving|    |  |   |      |         |     |Discarded|                                   |           |       |   |   |          |        |    |    |Alt  |       |
#         |   |Subframe|Frame|Num|Num   |Blocks   |Cell   |HARQ|  |   |CRC   |         |TB   |reTx     |                                   |Did        |TB Size|   |Num|Modulation|ACK/NACK|PMCH|Area|TBS  |Alt MCS|
#         |#  |Num     |Num  |RBs|Layers|Present  |Index  |ID  |RV|NDI|Result|RNTI Type|Index|Present  |Discarded ReTx                     |Recombining|(bytes)|MCS|RBs|Type      |Decision|ID  |ID  |Index|Enabled|
#         ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#         |  0|       9|  736|  9|     2|        1|  PCELL|   2| 0|  0|  Pass|        P|    0|     None|                         NO_DISCARD|         No|     13|  3|  9|      QPSK|     ACK|    |    | NONE|  false|
#                     """)
#         messages.append(msg)

#         msg = ParsedRawMessage(index = 0, packet_type = "0xB8A7", packet_length=100, name="NR5G MAC CSF Report", subtitle="", datetime="", packet_text=
#         """2023 Jun  6  18:41:10.040  [0F]  0xB8A7  NR5G MAC CSF Report
#         Subscription ID = 2
#         Misc ID         = 0
#         Major.Minor                    = 2. 3
#         Log Fields Change BMask        = 0x0000
#         Num Records                    = 1
#         Records[0]
#         Timestamp
#             Slot                     = 9
#             Numerology               = 30kHz
#             Frame                    = 642
#         Num CSF Reports             = 1
#         Num CSF Type2 Reports       = 0
#         Reports
#             ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#             |   |       |        |      |          |                    |    |     |    |    |Num |Num |       |       |       |       |       |Quantities                                                                                                                         |
#             |   |       |        |      |          |                    |    |     |    |Num |CSI |CSI |       |       |       |       |       |CSI                                                                                  |RSRP                                         |
#             |   |       |        |      |          |                    |    |     |Num |CSI |P2  |P2  |       |       |       |P2 SB  |P2 SB  |Metrics                                           |Bit Width                         |        |CRI  |     |Diff |       |    |     |
#             |   |       |Resource|      |          |                    |    |     |CSI |P2  |SB  |SB  |       |       |       |Odd    |Even   |   |  |   |        |        |  |   |SB Result     |   |  |       |   |PMI |PMI|  |PMI|        |SSBRI|RSRP |RSRP |       |    |     |
#             |   |Carrier|Carrier |Report|Report    |Report Quantity     |Late|Faked|P1  |WB  |Odd |Even|Report |P1     |P2 WB  |Report |Report |   |  |WB |PMI WB  |PMI WB  |  |Num|   |SB|SB |SB |   |  |Zero   |WB |WB  |WB |  |SB |Resource|Bit  |Bit  |Bit  |Num    |    |SSBRI|
#             |#  |ID     |ID      |ID    |Type      |Bitmask             |CSF |CSF  |Bits|Bits|Bits|Bits|Dropped|Dropped|Dropped|Dropped|Dropped|CRI|RI|CQI|X1      |X2      |LI|SB |#  |ID|CQI|PMI|CRI|RI|Padding|CQI|X1  |X2 |LI|X2 |Set ID  |Width|Width|Width|Results|RSRP|CRI  |
#             ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#             |  0|      0|       0|     0|  PERIODIC|          CRI:RI:CQI|   0|    0|   5|   0|   0|   0|      0|      0|      0|      0|      0|  0| 1| 15|       0|       0| 0|  0|   |  |   |   |  0| 1|      0|  4|   0|  0| 0|  0|        |     |     |     |       |    |     |
#         """)
#         messages.append(msg)

#         msg = ParsedRawMessage(index = 0, packet_type = "0xB8A7", packet_length=100, name="NR5G MAC CSF Report", subtitle="", datetime="", packet_text=
#         """2023 Jun  6  18:41:10.040  [0F]  0xB8A7  NR5G MAC CSF Report
#         Subscription ID = 2
#         Misc ID         = 0
#         Major.Minor                    = 2. 3
#         Log Fields Change BMask        = 0x0000
#         Num Records                    = 1
#         Records[0]
#         Timestamp
#             Slot                     = 9
#             Numerology               = 30kHz
#             Frame                    = 642
#         Num CSF Reports             = 1
#         Num CSF Type2 Reports       = 0
#         Records
#                 ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#                 |   |        |     |   |      |Num      |       |Transport Blocks                                                                                                                |    |    |     |       |
#                 |   |        |     |   |      |Transport|Serving|HARQ|  |   |      |         |     |Discarded|                                   |           |       |   |   |          |        |    |    |Alt  |       |
#                 |   |Subframe|Frame|Num|Num   |Blocks   |Cell   |HARQ|  |   |CRC   |         |TB   |reTx     |                                   |Did        |TB Size|   |Num|Modulation|ACK/NACK|PMCH|Area|TBS  |Alt MCS|
#                 |#  |Num     |Num  |RBs|Layers|Present  |Index  |ID  |RV|NDI|Result|RNTI Type|Index|Present  |Discarded ReTx                     |Recombining|(bytes)|MCS|RBs|Type      |Decision|ID  |ID  |Index|Enabled|
#                 ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#                 |  0|       9|  352| 12|     2|        1|  PCELL|   2| 0|  0|  Pass|        P|    0|     None|                         NO_DISCARD|         No|     18|  5| 12|      QPSK|     ACK|    |    | NONE|  false|
#                 |  1|       9|  352| 12|     2|        1|  PCELL|   2| 0|  0|  Pass|        P|    0|     None|                         NO_DISCARD|         No|     18|  5| 12|      QPSK|     ACK|    |    | NONE|  false|
#         """)
#         messages.append(msg)

#         msg = ParsedRawMessage(index = 0, packet_type = "0xB97F", packet_length=100, name="NR5G ML1 Searcher Measurement", subtitle="", datetime="", packet_text=
#         """ 2023 Jun  6  18:41:01.899  [3E]  0xB97F  NR5G ML1 Searcher Measurement Database Update Ext
#         Subscription ID = 2
#         Misc ID         = 0
#         Major.Minor Version                 = 2. 8
#         System Time
#         Slot Number                      = 0
#         SubFrame Number                  = 3
#         System Frame Number              = 7
#         SCS                              = DEFAULT
#         Num Layers                          = 1
#         SSB Periodicity Serv Cell           = INVALID
#         Frequency Offset                    = 3.901 PPM
#         Timing Offset                       = 36681533
#         Component Carrier List[0]
#         Raster ARFCN                        = 639936
#         Num Cells                           = 1
#         Serving Cell Index                  = 255
#         Serving Cell PCI                    = 65535
#         Serving SSB                         = NA
#         ServingRsrpRx23[0]
#             Serving RSRP Rx23                = NA
#         ServingRsrpRx23[1]
#             Serving RSRP Rx23                = NA
#         Serving RX Beam                     = { NA, NA }
#         Serving RFIC ID                     = NA
#         ServingSubarrayId[0]
#             SubArray ID                      = NA
#         ServingSubarrayId[1]
#             SubArray ID                      = NA
#         Cells
#             -----------------------------------------------------------------------------------------------------------------------------------------
#             |   |      |      |     |            |            |Detected Beams                                                                       |
#             |   |      |      |     |            |            |   |     |RX Beam Info           |NR2NR       |NR2NR       |L2NR        |L2NR        |
#             |   |      |PBCH  |Num  |Cell Quality|Cell Quality|   |SSB  |RX Beam|               |Filtered Tx |Filtered Tx |Filtered Tx |Filtered Tx |
#             |#  |PCI   |SFN   |Beams|RSRP        |RSRQ        |#  |Index|Id     |RSRP           |Beam RSRP L3|Beam RSRQ L3|Beam RSRP L3|Beam RSRQ L3|
#             -----------------------------------------------------------------------------------------------------------------------------------------
#             |  0|     1|   852|    1|     -90.438|     -10.352|  0|    0|     NA|        -90.438|     -90.438|     -10.352|          NA|          NA|
#             |   |      |      |     |            |            |   |     |     NA|        -97.836|            |            |            |            |

#         """)
#         messages.append(msg)

#         msg = ParsedRawMessage(index = 0, packet_type = "0xB887", packet_length=100, name="NR5G MAC PDSCH Status", subtitle="", datetime="", packet_text=
#         """ 2023 Jun  6  18:41:02.041  [73]  0xB887  NR5G MAC PDSCH Status
#         Subscription ID = 2
#         Misc ID         = 0
#         Major.Minor                    = 2. 5
#         Log Fields Change BMask        = 0x0
#         Sub ID                         = 1
#         Num Records                    = 1
#         Records
#         ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#         |   |                     |      |PDSCH Status Info                                                                                                                                                                                                                                                                             |
#         |   |                     |      |       |    |      |    |         |    |       |        |        |     |        |   |   |    |  |HARQ |    |    |   |      |         |        |      |    |   |       |      |      |    |       |       |       |       |      |     |        |     |        |       |       |       |       |
#         |   |                     |      |       |    |      |    |         |    |       |        |        |     |        |   |   |    |  |Or   |    |K1  |   |      |         |        |      |    |   |       |      |      |    |       |       |       |       |      |     |        |     |        |RX     |RX     |RX     |RX     |
#         |   |                     |Num   |       |    |      |    |         |    |       |        |        |     |        |   |   |    |  |MBSFN|    |Or  |   |      |         |        |      |New |   |       |      |      |    |HD     |HARQ   |HD     |HARQ   |      |Is   |        |High |        |Antenna|Antenna|Antenna|Antenna|
#         |   |System Time          |PDSCH |Carrier|Tech|      |Conn|         |Band|Variant|Physical|        |TB   |        |SCS|   |Num |  |Area |RNTI|PMCH|   |Num   |Iteration|CRC     |CRC   |Tx  |   |Discard|Bypass|Bypass|Num |Onload |Onload |Offload|Offload|Did   |IOVec|        |Clock|        |Mapping|Mapping|Mapping|Mapping|
#         |#  |Slot|Numerology|Frame|Status|ID     |Id  |Opcode|ID  |Bandwidth|Type|Id     |cell ID |EARFCN  |Index|TB Size |MU |MCS|Rbs |RV|Id   |Type|ID  |TCI|Layers|Index    |State   |Status|Flag|NDI|Mode   |Decode|HARQ  |ReTx|Timeout|Timeout|Timeout|Timeout|Recomb|Valid|Mod Type|Mode |Num RX  |0      |1      |2      |3      |
#         ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#         |  0|  11|     30kHz|  866|     1|      0|   1|     3|   0|        6|   0|      0|       1|  639936|    0|      11|  1|  5|   1| 0|    0|   8|   1|  0|     1|        0|    PASS|  PASS|   1|  0|      0|     0|     1|   0|      0|      0|      0|      0|     0| true|    QPSK|    0|4x4_MIMO|      0|      0|      0|      0|

#         """)
#         messages.append(msg)

#         msg = ParsedRawMessage(index = 0, packet_type = "0xB825", packet_length=100, name="NR5G RRC Configuration Info", subtitle="", datetime="", packet_text=
#         """ 2023 Jun  6  18:41:02.068  [50]  0xB825  NR5G RRC Configuration Info
#         Subscription ID = 2
#         Misc ID         = 0
#         Major.Minor Version               = 2. 0
#         Conn Config Info
#         State = CONNECTED
#         Config Status = true
#         Connectivity Mode = SA
#         Num Active SRB = 1
#         Num Active DRB = 0
#         MN MCG DRB IDs = NONE
#         SN MCG DRB IDs = NONE
#         MN SCG DRB IDs = NONE
#         SN SCG DRB IDs = NONE
#         MN Split DRB IDs = NONE
#         SN Split DRB IDs = NONE
#         LTE Serving Cell Info {
#             Num Bands = 0
#         }
#         Num Contiguous CC Groups = 1
#         Num Active CC = 1
#         Num Active RB = 1
#         Contiguous CC Info
#             --------------------
#             |Band  |DL BW|UL BW|
#             |Number|Class|Class|
#             --------------------
#             |    48|    A|    A|

#         NR5G Serving Cell Info
#             ----------------------------------------------------------------------------------
#             |  |    |          |          |          |    |    |DL       |UL       |DL  |UL  |
#             |CC|Cell|          |          |          |    |Band|Carrier  |Carrier  |Max |Max |
#             |Id|Id  |DL Arfcn  |UL Arfcn  |SSB Arfcn |Band|Type|Bandwidth|Bandwidth|MIMO|MIMO|
#             ----------------------------------------------------------------------------------
#             | 0|   1|    640666|    640666|    639936|  48|SUB6|    40MHZ|    40MHZ|  NA|   1|
#             | 1|   1|    640666|    640666|    639936|  48|SUB6|    40MHZ|    40MHZ|  NA|   1|

#         Radio Bearer Info
#             ----------------------------------------------------------------------------------------------------------------------------------------------------
#             |  |           |          |DL  |       |            |            |UL  |          |       |            |            |          |UL PDCP  |UL Data   |
#             |RB|Termination|          |RB  |DL ROHC|DL Cipher   |DL Integrity|RB  |          |UL ROHC|UL Cipher   |UL Integrity|UL Primary|Dup      |Split     |
#             |ID|Point      |DL RB Type|Path|Enabled|Algo        |Algo        |Type|UL RB Path|Enabled|Algo        |Algo        |Path      |Activated|Threshold |
#             ----------------------------------------------------------------------------------------------------------------------------------------------------
#             | 1|         NR|       SRB|  NR|  false|          NA|          NA| SRB|        NR|  false|          NA|          NA|      NONE|    false|         0|


#         """)
#         messages.append(msg)
        
#         msg = ParsedRawMessage(index = 0, packet_type = "0xB825", packet_length=100, name="NR5G RRC Configuration Info", subtitle="", datetime="", packet_text=
#         """2023 Jun  6  18:41:24.040  [3E]  0xB825  NR5G RRC Configuration Info
#             Subscription ID = 2
#             Misc ID         = 0
#             Major.Minor Version               = 2. 0
#             Conn Config Info
#             State = IDLE
#             Config Status = true
#             Connectivity Mode = SA
#             Num Active SRB = 0
#             Num Active DRB = 0
#             MN MCG DRB IDs = NONE
#             SN MCG DRB IDs = NONE
#             MN SCG DRB IDs = NONE
#             SN SCG DRB IDs = NONE
#             MN Split DRB IDs = NONE
#             SN Split DRB IDs = NONE
#             LTE Serving Cell Info {
#                 Num Bands = 0
#             }
#             Num Contiguous CC Groups = 0
#             Num Active CC = 0
#             Num Active RB = 0
#         """)
#         messages.append(msg)
        #C:\Users\tm-reddev04\Documents\tmdc\storage\qxdm_mask_files\automation_freqtest.yaml

        conf = parse_config("C:\\Users\\tm-reddev04\\Documents\\tmdc\\storage\\qxdm_mask_files\\automation_freqtest.yaml")
        for message in messages:
            message.packet_config = conf
        json_arr = [{"_packetType": message.packet_type_hex, "_rawPayload": message.packet_text, "_parsedPayload": message.test()} for message in messages]
        base_path = os.path.dirname(os.path.abspath(__file__))
        dt_format = datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S")
        with open(os.path.join(os.path.dirname(base_path), "temp", f"{dt_format}_parsed.json"), "w") as outfile:
            json_obj = json.dumps(json_arr, indent=2)
            outfile.write(json_obj)
            
    test_table_parsing()
    
if __name__ == "__main__":
    test_parsing()