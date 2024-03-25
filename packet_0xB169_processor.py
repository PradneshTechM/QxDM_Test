import regex as re
from kpi_utils import simple_map_entry
class Packet_0xB169:
    def extract_info(packet_text, config=None, entry=None):

        pattern = r'.*?Subscription ID = (?P<Subs_ID>[\d]+).*?Modulation Type = (?P<Modulation>[a-zA-Z]+).*?Cell Index = (?P<Cell_Index>[\d]+).*?MCS = (?P<MCS>[\d]+).*?CQI = (?P<CQI>[\da-zA-Z]+).*?HARQ ID = (?P<HARQ_ID>[\d]+)'
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