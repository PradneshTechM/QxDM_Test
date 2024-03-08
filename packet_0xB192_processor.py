import re
from kpi_utils import table_config, map_entry
class Packet_0xB192:
    def __init__(self, packet_text, config, entry):
        self.packet_text = packet_text
        self.config = config
        self.entry = entry
        self.pattern1 = r'.*?Subscription ID = (?P<subs_id>[\d]+).*?Number of SubPackets = (?P<number_of_subpackets>[\d]+).*?Idle Mode Neighbor Cell Measurement Request.*?SubPacket Size = (?P<subpacket_size>[\d\sa-zA-Z]+)\n.*?E-ARFCN = (?P<e_arfcn>[\d]+).*?Num Cells = (?P<num_cells>[\d]+).*?Num Rx Ant = (?P<num_rx_ant>[\d]+).*?Neighbor Cells.*?Neighbor Cell Meas Result.*?SubPacket Size = (?P<sub_packet_size_1>[\d\sa-zA-z]+)\n.*?E-ARFCN = (?P<e_arfcn_1>[\d]+).*?Num Cells = (?P<num_cells_1>[\d]+).*?Duplexing Mode = (?P<duplexing_mode_1>[a-zA-Z]+).*?Serving Cell Index = (?P<serving_cell_index>[a-zA-Z]+)'
        self.pattern2 = r'.*?Enable.*?\|Enable.*?\|.*?-+.*?\n(?P<table>[\s\S]*).*?SubPacket ID'
        self.pattern3 = r'.*?\(dBm\).*?\|\(dBm\).*?\|.*?-+.*?\n(?P<table>[\s\S]*)'
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
            data = table_config(match, self.config['Neighbor Cells'], self.config)
            return data
        else:
            print("No data rows found.")

    def table_pattern2(self):
        match = re.search(self.pattern3, self.packet_text, re.DOTALL)
        if match:
            data = table_config(match, self.config['Neighbor Cells2'], self.config)
            return data
        else:
            print("No data rows found.")