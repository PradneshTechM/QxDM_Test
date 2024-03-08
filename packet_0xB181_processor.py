import re
from kpi_utils import simple_map_entry
class Packet_0xB181:
    def extract_info(packet_text,config=None, entry=None):
        # pattern = r'.*?(?P<Time>\d+ \w+ \d+\s+\d+:\d+:\d+\.\d+).*?Subscription ID = (?P<Subs_ID>\d+).*?Bearer ID = (?P<Bearer_ID>\d+).*?Bearer State = (?P<Bearer_State>\w+).*?Connection ID = (?P<Connection_ID>\d+).*?qci = (?P<qci>[\da-zA-z\s\(\)]+)\n'
        pattern = r'.*?Subscription ID = (?P<subs_id>[\d]+).*?Number of SubPackets = (?P<number_of_subpackets>[\d]+).*?SubPacket ID = (?P<subpacket_id>[\d]+).*?Idle Mode Reselection Measurements Common.*?SubPacket Size = (?P<subpacket_size>[\da-zA-Z\s]+)\n.*?Serving Cell E-ARFCN = (?P<serving_cell_e_arfcn>[\d]+).*?Serving Cell Physical Cell ID = (?P<serving_cell_physical_cell_id>[\d]+).*?Current UE Mobility State = (?P<current_ue_mobility_state>[a-zA-Z\s]+)\n.*?Priority Categories Evaluated = (?P<priority_categories_evaluated>[a-zA-Z]+)'
        match = re.search(pattern, packet_text, re.DOTALL)

        if match:
            entry1 = match.groupdict()
            data = simple_map_entry(entry1, config)
            entry.update(data)
            return entry
        else:
            # Return None or an empty dictionary if there is no match
            return None