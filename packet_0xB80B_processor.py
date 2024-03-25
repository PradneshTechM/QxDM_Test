import regex as re
from kpi_utils import simple_map_entry
class Packet_0xB80B:
    def extract_info(packet_text,config=None, entry=None):
        pattern = r".*?0xB80B.*? --  (?P<msg_subtitle>.*)\nSubscription ID = (?P<subscription_id>\d+).*?nr5g_mm_msg\n\s*(?P<nr5g_mm_msg>.*?(?=\n))"
        match = re.search(pattern, packet_text, re.DOTALL)

        if match:
            entry1 = match.groupdict()
            data = simple_map_entry(entry1, config)
            entry.update(data)
            return entry
        else:
            # Return None or an empty dictionary if there is no match
            return None