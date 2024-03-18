import re
from parser.kpi_utils import simple_map_entry
class Packet_0xB16D:
    def extract_info(packet_text,config=None, entry=None):
        # pattern = r'.*?(?P<Time>\d+ \w+ \d+\s+\d+:\d+:\d+\.\d+).*?Subscription ID = (?P<Subs_ID>\d+).*?Bearer ID = (?P<Bearer_ID>\d+).*?Bearer State = (?P<Bearer_State>\w+).*?Connection ID = (?P<Connection_ID>\d+).*?qci = (?P<qci>[\da-zA-z\s\(\)]+)\n'
        pattern = r".*?Subscription ID = (?P<subs_id>[\d]+).*?Tx Report Records\[0\].*?Chan Type = (?P<chan_type>[a-zA-Z]+).*?Cell Index = (?P<cell_index>[\d]+).*?Total Tx Power = (?P<total_tx_power>[\da-zA-Z\s]+)\n.*?Transport Block Size = (?P<transport_block_size>[\d]+).*?HARQ ID = (?P<harq_id>[\d]+).*?Retransmission Index = (?P<retransmission_index>[\d]+).*?Modulation Type = (?P<modulation_type>[\d\sa-zA-Z]+)\n.*? Number of Resource Blocks = (?P<number_of_resource_blocks>[\d]+).*?MCS Index = (?P<mcs_index>[\d]+).*?Num Antenna = (?P<num_antenna>[\d]+)"
        match = re.search(pattern, packet_text, re.DOTALL)

        if match:
            entry1 = match.groupdict()
            data = simple_map_entry(entry1, config)
            entry.update(data)
            return entry
        else:
            # Return None or an empty dictionary if there is no match
            return None