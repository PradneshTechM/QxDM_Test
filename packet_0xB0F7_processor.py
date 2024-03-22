import regex as re
from parser.kpi_utils import simple_map_entry
class Packet_0xB0F7:
    def extract_info(packet_text,config=None, entry=None):
        pattern = r".*?0xB0F7.*?Subscription ID = (?P<subscription_id>\d+).*?Trans Id = (?P<trans_id>\w+).*?Network Select Mode = (?P<network_select_mode>.*?(?=\n))"
        match = re.search(pattern, packet_text, re.DOTALL)

        if match:
            entry1 = match.groupdict()
            data = simple_map_entry(entry1, config)
            entry.update(data)
            return entry
        else:
            # Return None or an empty dictionary if there is no match
            return None