import regex as re
from kpi_utils import simple_map_entry
class Packet_0xB16A:
    def extract_info(packet_text,config=None, entry= None):
        pattern = r'.*?Subscription ID = (?P<Subs_ID>[\d]+).*?SFN = (?P<SFN>[\d]+).*?Sub-fn = (?P<Sub_fn>[\d]+).*?Contention Result = (?P<Contention_Result>[a-zA-Z]+).*?UL ACK Timing SFN = (?P<UL_ACK_Timing_SFN>[\d]+).*?UL ACK Timing Sub-fn = (?P<UL_ACK_Timing_Sub_fn>[\d]+)'

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