import regex as re
from parser.kpi_utils import simple_map_entry
class Packet_0x1830:
    def extract_info(packet_text,config=None, entry=None):
        pattern = r'.*?0x1830.*?Subscription ID = (?P<subscription_id>\d+).*?Direction = (?P<direction>\w+).*?Result = (?P<result>\w+).*?Call Setup Delay = (?P<call_setup_delay>\d+).*?RAT = (?P<rat>\w+)'
        match = re.search(pattern, packet_text, re.DOTALL)

        if match:
            entry1 = match.groupdict()
            data = simple_map_entry(entry1, config)
            entry.update(data)
            return entry
        else:
            # Return None or an empty dictionary if there is no match
            return None