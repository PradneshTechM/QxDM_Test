from enum import Enum, auto
import re
import logging
import sys
import traceback
from typing import List, Tuple, Any


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
    VERSION = 1
    
    INT_REGEX = r'^[-+]?\d+$'
    FLOAT_REGEX = r'^[-+]?[0-9]*\.[0-9]+([eE][-+]?[0-9]+)?$'
    
    def __init__(self, index: int, packet_type: str, packet_length: int, name: str, subtitle: str, datetime: str, packet_text: str):
        self.index = index
        self.packet_type = packet_type
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
        header, parsed = self.parse_payload()
        print(header)
        print(parsed)
        logging.info(header)
        logging.info(parsed)
        sys.stdout.flush()
        sys.stderr.flush()
        return header, parsed
        
    def to_json(self):
        header, parsedPayload = self.parse_payload()
        return {
            "_index": self.index,
            "_packetType": hex(int(self.packet_type)),
            "_packetTypeInt": int(self.packet_type),
            "_name": self.name,
            "_datetime": self.datetime,
            "_length": self.packet_length,
            "_subtitle": self.subtitle if self.subtitle else "",
            "_rawPayload": self.packet_text,
            "_parserVersion": ParsedRawMessage.VERSION,
            **header, **parsedPayload
        }
    
    def parse_payload(self):
        payload = {}
        header = {}
        
        #################################
        # HELPER METHODS
        #################################
        
        # remove extra whitespaces
        def _clean(val: str):
            val = re.sub(r'[^\S\n]+', ' ', val).strip()
            return val
        
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
                        _obj[key] = val
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
                    
        # START PARSING
        def _PARSE(lines: list[str], _obj: dict):
            # parse payloads that are encoded in hex
            if _hex_payload(lines):
               return 
            # else parse class/struct type data and generic key-value pairs
            return _struct_or_generic_parse(lines, _obj)
        
        # start here
    
        # remove empty (only whitespace) lines
        raw_lines = [s for s in self.packet_text.splitlines() if s.strip() != ""]
            
        # parse payload      
        # skip first line, because first line content is main content 
        # (packet type, length, etc), and is already parsed  
        # also skip 2nd line because it is payload header
        _PARSE(raw_lines[2:], payload)
                    
        # parse payload header
        if len(raw_lines) >= 2:
            _key_value_parse([raw_lines[1]], header)
          
        return header, payload


class Message:
    def __init__(self, description: str, packet_type: str, subtitle: str,
                 fields: [Field], must_match_field: bool, saved_values: dict):
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
# msg = ParsedRawMessage(index = 0, packet_type = "0xAAAA", packet_length=100, name="Packet", subtitle="subtitle", datetime="", packet_text=
# """2023 May 23  07:32:52.592  [EC]  0x1FF0  Diagnostic Response Status  --  Invalid Command Error Response
# Cmd Code: 19
# Data = { 
#    0x4B, 0x12, 0x33, 0x08, 0x01, 0x01, 0x00, 0x00
# }""")

# msg.test()