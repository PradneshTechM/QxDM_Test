from enum import Enum
import re


class ValidationType(Enum):
    FIRST_NUMBER_EXACT = 1
    FIRST_NUMBER_ONE_OF = 2
    ANY_SUBSTRING = 3
    EMPTY_MESSAGE = 4
    CHECK_SAVED = 5
    CONCAT_AND_COMPARE = 6
    COLLECTION = 7
    CONVERT_TO_INT_FIRST = 8
    CHECK_DEVICE_SPECS = 9   # could be merged with CHECK_SAVED ?
    STRING_DOES_NOT_MATCH = 10
    STRING_MATCH_ONE_OF = 11


# specifies whether the field is a value or a collection of values
class FieldType(Enum):
    VALUE = 1
    COLLECTION = 2


class Field:
    def __init__(self, field_name: str, regex: str, search_2: str,
                 field_type: FieldType, get_value: str,
                 validation_type: ValidationType):
        self.field_name = field_name
        self.regex = regex
        self.search_2 = search_2
        self.field_type = field_type
        self.get_value = get_value

        self.validation_type = validation_type


class ValidatedMessage:
    def print():
        pass

    def write_to_file():
        pass


class ParsedField:
    def __init__(self, field: Field, value: str, found: bool = True):
        self.field_name = field.field_name
        self.field_type = field.field_type
        self.get_value = field.get_value
        self.value = value
        self.found = found

    def __str__(self):
        return 'field_name: ' + self.field_name + '\nvalue: ' + self.value \
                + '\nfound: ' + str(self.found)


class ParsedMessage:
    def __init__(self, name: str, subtitle: str, datetime: bool):
        self.name = name
        self.subtitle = subtitle
        self.datetime = datetime
        self.fields = []

    def add_parsed_field(self, field: ParsedField):
        self.fields.append(field)

    def validate(self) -> ValidatedMessage:
        '''validates the message and returns a ValidatedMessage'''

        # compare each ParsedField against the validation rules for that field

        # update ValidatedMessage with results
        return ValidatedMessage()

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


class Message:
    def __init__(self, packet_type: str, subtitle: str, fields: [Field],
                 must_match_field: bool):
        '''
        must_match_field: boolean used to indicate that a message MUST contain
            the first field, otherwise, message should not be added. Used to
            handle cases like 'LTE NAS EMM State' message which should have
            specific field and value: 'EMM state = EMM_REGISTERED_INITIATED'
        '''
        self.packet_type = packet_type
        self.subtitle = subtitle
        self.fields = fields
        self.must_match_field = must_match_field

    def is_same_message_type(self, subtitle: str, packet_type: str,
                             packet_text: str) -> bool:
        if self.packet_type == packet_type and self.must_match_field:
            for line in packet_text.split('\r\n'):
                if self.fields[0].field_name == line:
                    return True
            return False
        else:
            return self.subtitle and subtitle == self.subtitle

    def parse(self, name: str, datetime: str,
              packet_text: str) -> ParsedMessage:
        '''parses the message and returns a ParsedMessage'''
        parsed_message = ParsedMessage(name, self.subtitle, datetime)

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
