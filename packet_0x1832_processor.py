import regex as re
from kpi_utils import simple_map_entry
class Packet_0x1832:
    def extract_info(packet_text,config=None, entry=None):
        pattern = r'.*?Subscription ID = (?P<subscription_id>\d+).*?Registration Type = (?P<registration_type>\w+-\w+).*?Result = (?P<result>\w+)\n'
        match = re.search(pattern, packet_text, re.DOTALL)

        if match:
            entry1 = match.groupdict()
            data = simple_map_entry(entry1, config)
            entry.update(data)
            return entry
        else:
            # Return None or an empty dictionary if there is no match
            return None