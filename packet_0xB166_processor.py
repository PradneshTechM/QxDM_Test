import regex as re
from kpi_utils import simple_map_entry
class Packet_0xB166:
    def extract_info(packet_text, config=None, entry=None):
        pattern = r'.*?Subscription ID = (?P<Subs_ID>[\d]+).*?Cell Index = (?P<Cell_Index>[\d]+).*?Logical Root Seq Index = (?P<Logical_Root_Seq_Index>[\d]+).*?PRACH Config = (?P<PRACH_Config>[\d]+).*?Preamble Format = (?P<Preamble_Format>[\d]+).*?Duplex Mode = (?P<Duplex_Mode>[a-zA-Z]+).*?High Speed Flag = (?P<High_Speed_Flag>[\d]+).*?PRACH Frequency Offset = (?P<PRACH_Frequency_Offset>[\d]+).*?Max Transmissions MSG3 = (?P<Max_Transmissions_MSG3>[\d]+).*?Cyclic Shift Zone Length = (?P<Cyclic_Shift_Zone_Length>[\d]+).*?RA Response Window Size = (?P<RA_Response_Window_Size>[\d]+)'  # Use re.search to find the first match of the pattern in the packet_text
        match = re.search(pattern, packet_text, re.DOTALL)
        if match:
            entry1 = match.groupdict()
            data = simple_map_entry(entry1, config)
            entry.update(data)
            return entry
        else:
            # Return None or an empty dictionary if there is no match
            return None