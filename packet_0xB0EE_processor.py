import re
from parser.kpi_utils import simple_map_entry
class Packet_0xB0EE:
    def extract_info(packet_text,config=None, entry=None):
        # pattern = r'.*?(?P<Time>\d+ \w+ \d+\s+\d+:\d+:\d+\.\d+).*?Subscription ID = (?P<Subs_ID>\d+).*?Bearer ID = (?P<Bearer_ID>\d+).*?Bearer State = (?P<Bearer_State>\w+).*?Connection ID = (?P<Connection_ID>\d+).*?qci = (?P<qci>[\da-zA-z\s\(\)]+)\n'
        pattern = r'Subscription ID = (?P<subs_id>\d+).*?EMM state = (?P<emm_state>\w+).*?PLMN_ID:(?P<plmn>.*?)Guti valid = (?P<guti_valuid>[a-zA-Z]+)'
        match = re.search(pattern, packet_text, re.DOTALL)

        if match:
            entry1 = match.groupdict()
            entry1['plmn'] = entry1['plmn'].replace('\n', '')
            data = simple_map_entry(entry1, config)
            entry.update(data)
            return entry
        else:
            # Return None or an empty dictionary if there is no match
            return None