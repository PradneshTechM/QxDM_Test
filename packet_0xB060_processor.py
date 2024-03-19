import re
from kpi_utils import table_config, map_entry

class Packet_0xB060:
    def __init__(self, packet_text, config, entry):
        self.packet_text = packet_text
        self.config = config
        self.entry = entry
        self.pattern1 = r'.*?Subscription ID = (?P<Subs_ID>[\d]+).*?Number of SubPackets = (?P<no_sub_packets>[\d]+).*?SubPacket ID = (?P<subpacket_id>[\d]+).*?SubPacket Size = (?P<subpacket_size>.*?(?=\n)).*?Sub Id = (?P<DL_Config_V2_Sub_Id>[\d]+).*?Num Active Stag = (?P<DL_Config_V2_Num_Active_Stag>[\d]+).*?UL Config V2\n.*?Sub Id = (?P<UL_Config_V2_Sub_Id>[\d]+).*?SR resource present = (?P<SR_resource_present>.*?(?=\n)).*?SR periodicity = (?P<SR_periodicity>.*?(?=\n)).*?BSR timer = (?P<BSR_timer>[\w]+).*?SPS Number of Tx release = (?P<SPS_no>[\d]+).*?Retx BSR timer = (?P<timer>.*?(?=\n)).*?'
        self.pattern2 = r".*?\|Present\|\(ms\)\s+\|.*?-+.*?\n(?P<table>[\s\S]*)\n\n.*?SubPacket ID = .*?SubPacket - \( UL Config Subpacket \).*?"
        self.pattern3 = r'.*?\|Msg3\|\(ms\)\|.*?-+.*?\n(?P<table>[\s\S]*)\n\n.*?SubPacket - \( LC Config Subpacket \).*?'

        self.dict = {}
        self.result = []

    def extract_info(self):
        self.dict.update(self.entry)
        non_table_capture = self.regular_pattern()
        table_capture1 = self.table_pattern1()
        table_capture2 = self.table_pattern2()
        if non_table_capture:  # Check if non_table_capture is not None
            self.dict.update(non_table_capture)
        if table_capture1:
            for row in table_capture1:
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


    def table_pattern1(self):
        match = re.search(self.pattern2, self.packet_text, re.DOTALL)
        if match:
            data = table_config(match, self.config['Scell Tag Info'], self.config)
            return data
        else:
            print("No data rows found.")

    def table_pattern2(self):
        match = re.search(self.pattern3, self.packet_text, re.DOTALL)
        if match:
            data = table_config(match, self.config['Cell Rach Info'], self.config)
            return data
        else:
            print("No data rows found.")

