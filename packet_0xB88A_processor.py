import regex as re
from parser.kpi_utils import simple_map_entry
class Packet_0xB88A:
    def extract_info(packet_text,config=None, entry=None):
        # pattern = r'.*?(?P<Time>\d+ \w+ \d+\s+\d+:\d+:\d+\.\d+).*?Subscription ID = (?P<Subs_ID>\d+).*?Bearer ID = (?P<Bearer_ID>\d+).*?Bearer State = (?P<Bearer_State>\w+).*?Connection ID = (?P<Connection_ID>\d+).*?qci = (?P<qci>[\da-zA-z\s\(\)]+)\n'
        pattern = r'.*?Subscription ID = (?P<subs_id>[\d]+).*?Num Attempts = (?P<num_attempts>[\d]+).*?Contention Type = (?P<contention_type>[a-zA-Z_]+).*?Msg1 SCS = (?P<msg1>[\d\.a-zA-Z]+).*?Msg2 SCS = (?P<msg2>[\d\.a-zA-Z]+).*?UL BWP SCS = (?P<ul_bwp_svs>[\d\.a-zA-Z]+)'  # Use re.search to find the first match of the pattern in the packet_text
        match = re.search(pattern, packet_text, re.DOTALL)

        if match:
            entry1 = match.groupdict()
            data = simple_map_entry(entry1, config)
            entry.update(data)
            return entry
        else:
            # Return None or an empty dictionary if there is no match
            return None