import regex as re
from kpi_utils import simple_map_entry
class Packet_0x1831:
    def extract_info(packet_text,config=None, entry=None):
        pattern = r'.*?Subscription ID = (?P<subscription_id>\d+).*?Direction = (?P<Direction>\w+).*?End Cause = (?P<end_cause>[A-Z\s]+)\n.*?Call Setup Delay = (?P<call_setup_delay>\d+).*?RAT = (?P<rat>\w+).*?Client End Cause = (?P<client_end_cause>[A-Z_]+)'
        match = re.search(pattern, packet_text, re.DOTALL)

        if match:
            entry1 = match.groupdict()
            data = simple_map_entry(entry1, config)
            entry.update(data)
            return entry
        else:
            # Return None or an empty dictionary if there is no match
            return None