import regex as re
from parser.kpi_utils import table_config, map_entry
class Packet_0xB115:
    def __init__(self, packet_text, config, entry):
        self.packet_text = packet_text
        self.config = config
        self.entry = entry
        self.pattern1 = r'.*?Subscription ID = (?P<Subs_ID>[\d]+).*?Number of Barred Cells    = (?P<Number_of_Barred_Cells>[\d]+).*?Number of Detected Cells  = (?P<Number_of_Detected_Cells>[\d]+).*?Number of IC Cells.*?= (?P<Number_of_IC_Cells>[\d]+).*?EARFCN.*?=.*?(?P<EARFCN>[\d]+)'
        self.pattern2 = r'.*?Boundary\|Range.*?\|.*?-+.*?\n(?P<table>[\s\S]*)'
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
                copy_dict = self.dict.copy()
                copy_dict.update(row)
                self.result.append(copy_dict)
        return self.result  # Return the updated dictionary

    def regular_pattern(self):
        match = re.search(self.pattern1, self.packet_text, re.DOTALL)
        if match:
            entry = match.groupdict()
            data = map_entry(entry, self.config)
            return data
        else:
            return None

    def table_pattern(self):
        match = re.search(self.pattern2, self.packet_text, re.DOTALL)
        if match:
            data = table_config(match, self.config['Detected Cells:'], self.config)
            return data
        else:
            print("No data rows found.")