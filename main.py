from enum import Enum
import re
import logging
import sys
import traceback
import json
import datetime
from typing import List, Tuple, Any, Dict

from parser.packet_0xB195_processor import Packet_0xB195
from parser.packet_0xB172_processor import Packet_0xB172
from parser.packet_0xB16D_processor import Packet_0xB16D
from parser.packet_0xB063_processor import Packet_0xB063
from parser.packet_0xB16B_processor import Packet_0xB16B
from parser.packet_0xB126_processor import Packet_0xB126
from parser.packet_0xB130_processor import Packet_0xB130
from parser.packet_0xB132_processor import Packet_0xB132
from parser.packet_0xB14D_processor import Packet_0xB14D
from parser.packet_0xB0EE_processor import Packet_0xB0EE
from parser.packet_0xB808_processor import Packet_0xB808
from parser.packet_0xB809_processor import Packet_0xB809
from parser.packet_0xB0E2_processor import Packet_0xB0E2
from parser.packet_0xB192_processor import Packet_0xB192
from parser.packet_0xB186_processor import Packet_0xB186
from parser.packet_0xB181_processor import Packet_0xB181
from parser.packet_0xB17E_processor import Packet_0xB17E
from parser.packet_0xB179_processor import Packet_0xB179
from parser.packet_0xB176_processor import Packet_0xB176
from parser.packet_0xB173_processor import Packet_0xB173
from parser.packet_0xB88A_processor import Packet_0xB88A
from parser.packet_0xB828_processor import Packet_0xB828
from parser.packet_0xB970_processor import Packet_0xB970
from parser.packet_0xB887_processor import Packet_0xB887
from parser.packet_0xB0F7_processor import Packet_0xB0F7
from parser.packet_0x156A_processor import Packet_0x156A
from parser.packet_0xB800_processor import Packet_0xB800
from parser.packet_0xB80B_processor import Packet_0xB80B
from parser.packet_0xB0C1_processor import Packet_0xB0C1
from parser.packet_0x156E_processor import Packet_0x156E
from parser.packet_0xB0E4_processor import Packet_0xB0E4
from parser.packet_0xB0EC_processor import Packet_0xB0EC
from parser.packet_0x1832_processor import Packet_0x1832
from parser.packet_0xB0C2_processor import Packet_0xB0C2
from parser.packet_0x1830_processor import Packet_0x1830
from parser.packet_0x1831_processor import Packet_0x1831
from parser.packet_0xB167_processor import Packet_0xB167
from parser.packet_0x1569_processor import Packet_0x1569
from parser.packet_0xB8D8_processor import Packet_0xB8D8
from parser.packet_0xB823_processor import Packet_0xB823
from parser.packet_0xB0E5_processor import Packet_0xB0E5
from parser.packet_0xB822_processor import Packet_0xB822
from parser.packet_0xB115_processor import Packet_0xB115
from parser.packet_0xB166_processor import Packet_0xB166
from parser.packet_0xB168_processor import Packet_0xB168
from parser.packet_0xB169_processor import Packet_0xB169
from parser.packet_0xB16A_processor import Packet_0xB16A
from parser.packet_0xB80A_processor import Packet_0xB80A
from parser.packet_0xB801_processor import Packet_0xB801
from parser.packet_0xB825_processor import Packet_0xB825
from parser.packet_0xB97F_processor import Packet_0xB97F
from parser.packet_0xB8A7_processor import Packet_0xB8A7
from parser.packet_0xB827_processor import Packet_0xB827
from parser.packet_0xB18F_processor import Packet_0xB18F
from parser.packet_0xB821_processor import Packet_0xB821
from parser.packet_0xB0C0_processor import Packet_0xB0C0
from parser.packet_0xB113_processor import Packet_0xB113
from parser.packet_0xB171_processor import Packet_0xB171
from parser.packet_0xB18E_processor import Packet_0xB18E
from parser.packet_0xB196_processor import Packet_0xB196
from parser.packet_0xB883_processor import Packet_0xB883
from parser.packet_0xB884_processor import Packet_0xB884
from parser.packet_0xB889_processor import Packet_0xB889
from parser.packet_0x17F2_processor import Packet_0x17F2
from parser.packet_0x1D4D_processor import Packet_0x1D4D
from parser.packet_0xB16F_processor import Packet_0xB16F
from parser.packet_0xB0E3_processor import Packet_0xB0E3
from parser.packet_0xB16E_processor import Packet_0xB16E
from parser.packet_0xB139_processor import Packet_0xB139
from parser.packet_0xB060_processor import Packet_0xB060
from parser.packet_0xB0A5_processor import Packet_0xB0A5
from parser.packet_0xB0A1_processor import Packet_0xB0A1
from parser.packet_0xB06E_processor import Packet_0xB06E
from parser.packet_0xB062_processor import Packet_0xB062
from parser.packet_0xB1DA_processor import Packet_0xB1DA
from parser.packet_0xB081_processor import Packet_0xB081
from parser.packet_0xB13C_processor import Packet_0xB13C
from parser.packet_0xB16C_processor import Packet_0xB16C
from parser.packet_0xB064_processor import Packet_0xB064
from parser.packet_0xB0EF_processor import Packet_0xB0EF
from parser.packet_0xB0B5_processor import Packet_0xB0B5
from parser.packet_0xB0B4_processor import Packet_0xB0B4
from parser.packet_0xB0B1_processor import Packet_0xB0B1
from parser.packet_0x1568_processor import Packet_0x1568
from parser.packet_0xB061_processor import Packet_0xB061
from parser.packet_0xB840_processor import Packet_0xB840
from parser.packet_0xB841_processor import Packet_0xB841
from parser.packet_0xB873_processor import Packet_0xB873
from parser.packet_0xB111_processor import Packet_0xB111

config_file = open('parser/input.json')
config = json.load(config_file)

config_file2 = open('parser/P2.json')
config2 = json.load(config_file2)

config_file3 = open('parser/P3.json')
config3 = json.load(config_file3)

config_file4 = open('parser/P4.json')
config4 = json.load(config_file4)

config_file5 = open('parser/P5.json')
config5 = json.load(config_file5)

class ParsedRawMessage:
    VERSION = 2

    INT_REGEX = r'^[-+]?\d+$'
    FLOAT_REGEX = r'^[-+]?[0-9]*\.[0-9]+([eE][-+]?[0-9]+)?$'

    packet_config = None

    def __init__(self, index: int, packet_type: Any, packet_length: int, name: str, full_name: str, subtitle: str, datetime: str,
                 packet_text: str, timestamp: datetime):
        self.index = index
        if isinstance(packet_type, int):
            self.packet_type = packet_type
            self.packet_type_hex = hex(self.packet_type)
        else:
            self.packet_type_hex = packet_type
            self.packet_type = int(self.packet_type_hex, 16)
        self.packet_length = packet_length
        self.name = name
        self.full_name = full_name
        self.subtitle = subtitle
        self.datetime = datetime
        self.packet_text = packet_text
        self.timestamp = timestamp

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
            parsedPayload = self.parse_payload()
        except:
            traceback.print_exc()
            logging.info(self.index)
            sys.stdout.flush()
            sys.stderr.flush()
            return None, None
        
        def serialize(payload):
            metadata = {
                "Packet Type": self.packet_type_hex[0:2] + self.packet_type_hex[2:].upper(),
                "Packet Name": self.full_name,
                "Script Version": ParsedRawMessage.VERSION,
            }
            
            if payload != None:
                if "__Raw_Data" in payload:
                    if (payload["__Raw_Data"] == True or payload["__Raw_Data"] == 'True'):
                        metadata["Raw Payload"] = self.packet_text
                    del payload["__Raw_Data"]
                if "__cell" in payload:
                    payload["Cell"] = payload["__cell"]
                    del payload["__cell"]
                if "__packet_message" in payload:
                    payload["Packet Type"] = payload["__packet_message"]
                    del payload["__packet_message"]
                payload["Time"] = self.timestamp
                
            return payload, metadata
        
        arr = []
        if isinstance(parsedPayload, list):
            for payload in parsedPayload:
                arr.append(serialize(payload))
        else:
            arr.append(serialize(parsedPayload))
        
        return arr
                
        

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
            if packet_name == '0xB0E5':
                print("0xB0E5")
                return Packet_0xB0E5.extract_info(packet_text, config['0xB0E5  LTE NAS ESM Bearer Context Info'], entry)
            elif packet_name == "0x156E":
                print("0x156E")
                return Packet_0x156E.extract_info(packet_text, config['0x156E  IMS SIP Message'],entry)
            elif packet_name == "0x156A":
                print("0x156A")
                return Packet_0x156A.extract_info(packet_text, config['0x156A  IMS RTCP'],entry)
            elif packet_name == "0xB0C1":
                print("0xB0C1")
                return Packet_0xB0C1.extract_info(packet_text, config['0xB0C1  LTE RRC MIB Message Log Packet'],entry)
            elif packet_name == "0xB0F7":
                print("0xB0F7")
                return Packet_0xB0F7.extract_info(packet_text, config['0xB0F7  LTE NAS EMM RRC Service Request'],entry)
            elif packet_name == "0xB80B":
                print("0xB80B")
                return Packet_0xB80B.extract_info(packet_text, config['0xB80B  NR5G NAS MM5G Plain OTA Outgoing Msg'],entry)
            elif packet_name == "0xB800":
                print("0xB800")
                return Packet_0xB800.extract_info(packet_text, config['0xB800  NR5G NAS SM5G Plain OTA Incoming Msg'],entry)
            elif packet_name =="0xB0EC":
                print("0xB0EC")
                return Packet_0xB0EC.extract_info(packet_text, config["0xB0EC  LTE NAS EMM Plain OTA Incoming Message"],entry)
            elif packet_name =="0xB0E4":
                print("0xB0E4")
                return Packet_0xB0E4.extract_info(packet_text, config["0xB0E4  LTE NAS ESM Bearer Context State"],entry)
            elif packet_name =="0xB0C2":
                print("0xB0C2")
                return Packet_0xB0C2.extract_info(packet_text, config["0xB0C2  LTE RRC Serving Cell Info Log Pkt"],entry)
            elif packet_name == "0x1832":
                print("0x1832")
                return Packet_0x1832.extract_info(packet_text, config["0x1832  IMS Registration"],entry)
            elif packet_name == '0xB822':
                print("0xB822")
                return Packet_0xB822.extract_info(packet_text, config['NR5G RRC MIB Info'], entry)
            elif packet_name == '0xB115':
                print("0xB115")
                return Packet_0xB115(packet_text, config['0xB115  LTE LL1 SSS Results'], entry).extract_info()
            elif packet_name == "0x1831":
                print("0x1831")
                return Packet_0x1831.extract_info(packet_text, config["0x1831  IMS VoLTE Session End"],entry)
            elif packet_name == "0x1830":
                print("0x1830")
                return Packet_0x1830.extract_info(packet_text, config["0x1830  IMS VoLTE Session Setup"],entry)
            elif packet_name == '0xB166':
                print("0xB166")
                return Packet_0xB166.extract_info(packet_text, config['0xB166  LTE PRACH Configuration'], entry)
            elif packet_name == '0xB168':
                print("0xB168")
                return Packet_0xB168.extract_info(packet_text, config['0xB168  LTE Random Access Response (MSG2) Report'], entry)
            elif packet_name == '0xB169':
                print("0xB169")
                return Packet_0xB169.extract_info(packet_text, config['0xB169  LTE UE Identification Message (MSG3) Report'], entry)
            elif packet_name == '0xB16A':
                print("0xB16A")
                return Packet_0xB16A.extract_info(packet_text, config['0xB16A  LTE Contention Resolution Message (MSG4) Report'], entry)
            elif packet_name == '0xB8D8':
                print("0xB8D8")
                return Packet_0xB8D8.extract_info(packet_text, config['0xB8D8  NR5G LL1 LOG SERVING SNR'],entry)
            elif packet_name == '0xB167':
                print("0xB167")
                return Packet_0xB167.extract_info(packet_text, config["0xB167  LTE Random Access Request (MSG1) Report"],entry)
            elif packet_name == "0x1569":
                print("0x1569")
                return Packet_0x1569.extract_info(packet_text, config['0x1569  IMS RTP Packet Loss'], entry)
            elif packet_name == '0xB823':
                print("0xB823")
                return Packet_0xB823.extract_info(packet_text, config['0xB823  NR5G RRC Serving Cell Info'], entry)
            elif packet_name == '0xB887':
                print('0xB887')
                return Packet_0xB887(packet_text, config['0xB887  NR5G MAC PDSCH Status'], entry).extract_info()
            elif packet_name == '0xB801':
                print('0xB801')
                return Packet_0xB801.extract_info(packet_text, config["0xB801  NR5G NAS SM5G Plain OTA Outgoing Msg"], entry)
            elif packet_name == '0xB80A':
                print('0xB80A')
                return Packet_0xB80A.extract_info(packet_text, config["0xB80A  NR5G NAS MM5G Plain OTA Incoming Msg"], entry)
            elif packet_name == '0xB825':
                print('0xB825')
                return Packet_0xB825.extract_info(packet_text, config["0xB825  NR5G RRC Configuration Info"], entry)
            elif packet_name == "0xB97F":
                print("0xB97F")
                return Packet_0xB97F(packet_text, config['0xB97F  NR5G ML1 Searcher Measurement Database Update Ext'], entry).extract_info()
                # entry,table_lines = Packet_0xB825.extract_info(packet_text, config["0xB825 -- PCC -- NSA"], entry)
                # return _tables(table_lines, entry)
            elif packet_name == '0xB8A7':
                print('0xB8A7')
                return Packet_0xB8A7(packet_text, config['0xB8A7  NR5G MAC CSF Report'], entry).extract_info()
            elif packet_name == '0xB827':
                print('0xB827')
                return Packet_0xB827(packet_text, config['0xB827  NR5G RRC PLMN Search Request'], entry).extract_info()
            elif packet_name == '0xB18F':
                print('0xB18F')
                return Packet_0xB18F(packet_text, config['0xB18F  LTE ML1 AdvRx IC Cell List'], entry).extract_info()
            elif packet_name == '0xB821':
                print('0xB821')
                return Packet_0xB821.extract_info(packet_text, config['0xB821  NR5G RRC OTA Packet'], entry)
            elif packet_name == '0xB0C0':
                print('0xB0C0')
                return Packet_0xB0C0.extract_info(packet_text, config['0xB0C0   LTE RRC OTA Packet'], entry)
            elif packet_name == '0xB113':
                print('0xB113')
                return Packet_0xB113(packet_text, config['0xB113  LTE LL1 PSS Results'], entry).extract_info()
            elif packet_name == '0xB171':
                print('0xB171')
                return Packet_0xB171(packet_text, config['0xB171  LTE SRS Power Control Report'], entry).extract_info()
            elif packet_name == '0xB18E':
                print('0xB18E')
                return Packet_0xB18E(packet_text, config['0xB18E  LTE ML1 System Scan Results'], entry).extract_info()
            elif packet_name == '0xB196':
                print('0xB196')
                return Packet_0xB196(packet_text, config['0xB196  LTE ML1 Cell Measurement Results'], entry).extract_info()
            elif packet_name == '0xB88A':
                print('0xB88A')
                return Packet_0xB88A.extract_info(packet_text, config2['0xB88A  NR5G MAC RACH Attempt'], entry)
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
                return Packet_0xB808.extract_info(packet_text, config2['0xB808  NR5G NAS MM5G Security Protected OTA Incoming Msg'], entry)
            elif packet_name == '0xB809':
                print('0xB809')
                return Packet_0xB809.extract_info(packet_text, config2['0xB809  NR5G NAS MM5G Security Protected OTA Outgoing Msg'], entry)
            elif packet_name == '0xB16E':
                print('0xB16E')
                return Packet_0xB16E(packet_text, config2['0xB16E  LTE PUSCH Power Control'], entry).extract_info()
            elif packet_name == '0xB139':
                print('0xB139')
                return Packet_0xB139(packet_text, config2['0xB139  LTE LL1 PUSCH Tx Report'], entry).extract_info()
            # elif packet_name == '0xB060':
            #     print('0xB060')
            #     return Packet_0xB060(packet_text, config2['0xB060  LTE MAC Configuration'], entry).extract_info()
            elif packet_name == '0xB0EE':
                print('0xB0EE')
                return Packet_0xB0EE.extract_info(packet_text, config3['0xB0EE  LTE NAS EMM State'], entry)
            elif packet_name == '0xB14D':
                print('0xB14D')
                return Packet_0xB14D.extract_info(packet_text, config3['0xB14D  LTE LL1 PUCCH CSF'], entry)
            # elif packet_name == '0xB132':
            #     print('0xB132')
            #     return Packet_0xB132(packet_text, config3['0xB132  LTE LL1 PDSCH Decoding Results'], entry).extract_info()
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
            elif packet_name == '0xB16D':
                print('0xB16D')
                return Packet_0xB16D.extract_info(packet_text, config4['0xB16D  LTE GM TX Report'], entry)
            elif packet_name == '0xB172':
                print('0xB172')
                return Packet_0xB172(packet_text, config4['0xB172  LTE Uplink PKT Build Indication'], entry).extract_info()
            elif packet_name == '0xB195':
                print('0xB195')
                return Packet_0xB195.extract_info(packet_text, config4['0xB195  LTE ML1 Connected Neighbor Meas Request/Response'], entry)
            elif packet_name == '0xB840':
                print('0xB840')
                return Packet_0xB840.extract_info(packet_text, config4['0xB840  NR5G PDCP DL Data Pdu'], entry)
            elif packet_name == '0xB841':
                print('0xB841')
                return Packet_0xB841.extract_info(packet_text, config4['0xB841  NR5G PDCP DL Control Pdu'], entry)
            elif packet_name == '0xB873':
                print('0xB873')
                return Packet_0xB873.extract_info(packet_text, config4['0xB873  NR5G L2 UL BSR'], entry)
            elif packet_name == '0xB111':
                print('0xB111')
                return Packet_0xB111(packet_text, config5['0xB111  LTE LL1 Rx Agc Log'], entry).extract_info()
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
