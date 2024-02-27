import re

class Packet_0xB887:
    def __init__(self,packet_text,config, entry):
        self.packet_text = packet_text
        self.config = config
        self.entry = entry
        self.pattern1 = r'.*?Subscription ID = (?P<Subs_ID>[\d]+).*?'
        self.pattern2 = r'.*?\|.*?[\d]+\|.*?[\d]+.*?\|.*?[\da-zA-Z]+\|.*?[\d]+\|\s*[\d]+\|\s*(?P<carrier_id>[\d]+)\|.*?[\d]+\|.*?[\d]+\|.*?[\d]+\|.*?(?P<Bandwidth>[\d]+)\|.*?[\d]+\|.*?[\d]+\|.*?(?P<Phy_cell_id>[\d]+)\|.*?(?P<EARFCN>[\d]+)\|.*?[\d]+\|.*?(?P<TB_size>[\d]+)\|.*?[\d]+\|.*?(?P<MCS>[\d]+)\|.*?(?P<Num_Rbs>[\d]+)\|.*?[\d]+\|.*?(?P<Area_ID>[\d]+)\|\s*(?P<RNTI_Type>[a-zA-Z\s]+)\|.*?[\d]+\|.*?[\d]+\|.*?[\d]+\|.*?[a-zA-Z]+\|.*?[a-zA-Z]+\|.*?(?P<flag>[\d]+)\|.*?(?P<NDI>[\d]+)\|.*?[\d]+\|.*?[\d]+\|.*?[\d]+\|.*?[\d]+\|.*?[\d]+\|.*?[\d]+\|.*?[\d]+\|.*?[a-zA-Z]+\|.*?[a-zA-Z]+\|.*?[\d]+\|.*?(?P<Num_Rx>[\w]+)\|'
        self.dict = {}

    def extract_info(self):
        self.dict.update(self.entry)
        non_table_capture = self.regular_pattern()
        if non_table_capture:  # Check if non_table_capture is not None
            self.dict.update(non_table_capture)
        else:
            return None
        table_capture = self.table_pattern()
        if table_capture:
            self.dict['records'] = {}  # Initialize the records key as an empty dictionary
            for i, entry in enumerate(table_capture, start=1):
                entry_key = f'record{i}'  # Create a unique key for each entry
                self.dict['records'][entry_key] = entry
        else:
            return None
        return self.dict  # Return the updated dictionary

    def regular_pattern(self):
        match = re.search(self.pattern1, self.packet_text, re.DOTALL)
        if match:
            return match.groupdict()
        else:
            return None

    def table_pattern(self):
        matches = re.finditer(self.pattern2, self.packet_text, re.DOTALL)
        entries = []
        if matches:
            for match in matches:
                entries.append(match.groupdict())
            return entries
        else:
            return None