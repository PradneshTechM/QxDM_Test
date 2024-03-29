import regex as re
from kpi_utils import simple_map_entry
class Packet_0xB17E:
    def extract_info(packet_text,config=None, entry=None):
        # pattern = r'.*?(?P<Time>\d+ \w+ \d+\s+\d+:\d+:\d+\.\d+).*?Subscription ID = (?P<Subs_ID>\d+).*?Bearer ID = (?P<Bearer_ID>\d+).*?Bearer State = (?P<Bearer_State>\w+).*?Connection ID = (?P<Connection_ID>\d+).*?qci = (?P<qci>[\da-zA-z\s\(\)]+)\n'
        pattern = r'.*?Subscription ID = (?P<subs_id>[\d]+).*?E-ARFCN = (?P<e_arfcn>[\d]+).*?Physical Cell ID = (?P<physical_cell_id>[\d]+).*?Previous UE Mobility State =(?P<previous_ue_mobility_state>[a-zA-Z\s]+)\n.*?Current UE Mobility State =(?P<current_ue_mobility_state>[a-zA-Z\s]+)\n.*?Camp Time = (?P<camp_time>[a-zA-Z\s\d]+)\n'
        match = re.search(pattern, packet_text, re.DOTALL)

        if match:
            entry1 = match.groupdict()
            data = simple_map_entry(entry1, config)
            entry.update(data)
            return entry
        else:
            # Return None or an empty dictionary if there is no match
            return None