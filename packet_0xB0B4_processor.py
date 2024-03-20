import regex as re
from kpi_utils import table_config, map_entry

class Packet_0xB0B4:
    def __init__(self, packet_text, config, entry):
        self.packet_text = packet_text
        self.config = config
        self.entry = entry
        self.pattern1 = r".*?Subscription ID = (?P<Subs_ID>[\d]+).*?"
        self.pattern2 = r".*?\|Shutdown\s+\|Freeze\s+\|.*?-+.*?\n(?P<table>[\s\S]*)\n\n\n"
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
                row_dict.update(row)
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
            data = table_config(match, self.config['Per RB'], self.config)
            return data
        else:
            print("No data rows found.")