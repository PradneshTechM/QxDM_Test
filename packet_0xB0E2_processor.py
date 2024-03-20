import regex as re
from kpi_utils import simple_map_entry
class Packet_0xB0E2:
    def extract_info(packet_text,config=None, entry=None):
        # pattern = r'.*?(?P<Time>\d+ \w+ \d+\s+\d+:\d+:\d+\.\d+).*?Subscription ID = (?P<Subs_ID>\d+).*?Bearer ID = (?P<Bearer_ID>\d+).*?Bearer State = (?P<Bearer_State>\w+).*?Connection ID = (?P<Connection_ID>\d+).*?qci = (?P<qci>[\da-zA-z\s\(\)]+)\n'
        pattern = r'.*?Subscription ID = (?P<subs_id>[\d]+).*?eps_bearer_id_or_skip_id = (?P<eps_bearer_id_or_skip_id>[\da-zA-Z\s\(\)]+)\n.*?prot_disc = (?P<prot_disc>[\da-zA-Z\s\(\)]+)\n.*?trans_id = (?P<trans_id>[\da-zA-Z\s\(\)]+)\n'
        match = re.search(pattern, packet_text, re.DOTALL)

        if match:
            entry1 = match.groupdict()
            data = simple_map_entry(entry1, config)
            entry.update(data)
            return entry
        else:
            # Return None or an empty dictionary if there is no match
            return None