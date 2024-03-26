import regex as re
from parser.kpi_utils import table_config, map_entry
class Packet_0xB132:
    def __init__(self, packet_text, config, entry):
        self.packet_text = packet_text
        self.config = config
        self.entry = entry
        self.pattern1 = r'Subscription ID = (?P<subs_id>\d+).*?Cell Id = (?P<cell_id>[\d]+).*?EARFCN = (?P<earfcn>[\d]+).*?System BW = (?P<system_bw>[\d]+).*?Num HARQ = (?P<num_harq>[\d]+).*?UE Category = (?P<ue_category>[\d]+).*?TX Mode = (?P<tx_mode>[\w]+).*?Num eNb Tx Ant = (?P<num_enb_Tx_Ant>[\d]+)'
        self.pattern2 = r'.*?TB Info Record\[0\].*?TB Top.*?Enable.*?\|Enable.*?\|.*?-+\n(?P<table>.*?)(?=\n.*?(?:TB Config|TB|TB Log Extend|CB|TB Info Record\[1\]))'
        self.pattern3 = r'.*?TB Info Record\[0\].*?TB Top.*?TB Config.*?Value.*?\|Rate.*?\|.*?-+\n(?P<table>.*?)(?=\n.*?(?:TB|TB Log Extend|CB|TB Info Record\[1\]))'
        self.dict = {}
        self.result = []

    def extract_info(self):
        self.dict.update(self.entry)
        non_table_capture = self.regular_pattern()
        table_capture = self.table_pattern()
        table_capture2 = self.table_pattern2()
        if non_table_capture:  # Check if non_table_capture is not None
            self.dict.update(non_table_capture)
        if table_capture:
            for row in table_capture:
                row_dict = self.dict.copy()
                row_dict.update(row)
                self.result.append(row_dict)
        if table_capture2:
            for row in table_capture2:
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
            data = table_config(match, self.config['TB Info Record[0]'], self.config)
            return data
        else:
            return None

    def table_pattern2(self):
        match = re.search(self.pattern3, self.packet_text, re.DOTALL)
        if match:
            data = table_config(match, self.config['TB Config'], self.config)
            return data
        else:
            return None
