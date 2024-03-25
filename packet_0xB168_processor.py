import regex as re
from kpi_utils import simple_map_entry
class Packet_0xB168:
    def extract_info(packet_text, config=None, entry=None):

        pattern = r'.*?Subscription ID = (?P<Subs_ID>[\d]+).*?Cell Index = (?P<Cell_Index>[\d]+).*?RACH Procedure Type = (?P<RACH_Type>[a-zA-Z]+).*?RACH Procedure Mode = (?P<RACH_Mode>[a-zA-Z]+).*?RNTI Type = (?P<RNTI_Type>[a-zA-Z_]+).*?Timing Advance Included = (?P<Timing_Advance_Included>[a-zA-Z]+).*?Timing Advance = (?P<Timing_Advance>[\d]+)'
        # Use re.search to find the first match of the pattern in the packet_text
        match = re.search(pattern, packet_text, re.DOTALL)
        if match:
            entry1 = match.groupdict()
            data = simple_map_entry(entry1, config)
            entry.update(data)
            return entry
        else:
            # Return None or an empty dictionary if there is no match
            return None