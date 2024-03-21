import regex as re
from  kpi_utils import table_config, map_entry

class Packet_0xB827:
    def __init__(self, packet_text, config, entry):
        self.packet_text = packet_text
        self.config = config
        self.entry = entry
        self.pattern1 = r'.*?Subscription ID = (?P<Subs_ID>[\d]+).*?Source RAT = (?P<Source_RAT>[a-zA-Z]+).*?Network Select Mode = (?P<Network_Select_Mode>[a-zA-Z]+).*?Scan Scope = (?P<Scan_Scope>[a-zA-Z]+).*?Guard Timer = (?P<Guard_Timer>[a-zA-Z0-9\s]+)\n.*?Num RATs = (?P<Num_RATs>[\d]+)'
        self.pattern2 = r'.*?Band Cap 385_448.*?\|Band Cap 449_512.*?\|.*?-+.*?\n(?P<table>[\s\S]*).*?NR5G Arfcn Counts'
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
            data = table_config(match, self.config['PLMN Search Request.RAT List'], self.config)
            return data
        else:
            print("No data rows found.")