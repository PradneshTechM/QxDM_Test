import re
from parser.kpi_utils import table_config, map_entry

class Packet_0xB130:
    def __init__(self, packet_text, config, entry):
        self.packet_text = packet_text
        self.config = config
        self.entry = entry
        self.pattern1 = r'.*?Subscription ID = (?P<Subs_ID>[\d]+).*?Carrier Index = (?P<carrier_index>[a-zA-Z]+)'
        self.pattern2 = r".*?\|Count.*?\|Normal.*?\|.*?-+.*?\n(?P<table>[\s\S]*)"
        self.dict = {}
        self.result = []

    def extract_info(self):
        self.dict.update(self.entry)
        non_table_capture = self.regular_pattern()
        table_capture = self.table_pattern()
        if non_table_capture:  # Check if non_table_capture is not None
            self.dict.update(non_table_capture)
        if table_capture:
            for row in table_capture:
                row_dict = self.dict.copy()
                row.update(row_dict)
                if '__cell' in row:
                    row['__cell'] = row.pop('Carrier Index')
                row.pop('Subs ID')
                row_dict.update(row)
                if 'Carrier Index' in row_dict:
                    row_dict.pop('Carrier Index')
                self.result.append(row_dict)
        return self.result  # Return the updated dictionary

    def regular_pattern(self):
        match = re.search(self.pattern1, self.packet_text, re.DOTALL)
        if match:
            data = match.groupdict()
            modified_entry = map_entry(data, self.config)
            return modified_entry
        else:
            return None


    def table_pattern(self):
        match = re.search(self.pattern2, self.packet_text, re.DOTALL)
        if match:
            data = table_config(match, self.config['Hyopthesis'], self.config)
            return data
        else:
            print("No data rows found.")