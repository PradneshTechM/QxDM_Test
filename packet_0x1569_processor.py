import regex as re
from parser.kpi_utils import simple_map_entry
class Packet_0x1569:
    def extract_info(packet_text,config=None, entry=None):
        pattern = r'.*?0x1569.*?Subscription ID = (?P<subscription_id>\d+).*?Sequence Number = (?P<sequence_number>\d+).*?SSRC = (?P<ssrc>\d+).*?codecType = (?P<codec_type>[\w-]+).*?LossType = (?P<loss_type>[A-Z\s]+)\n.*?Total Packets Count = (?P<total_packets_count>\d+)'
        match = re.search(pattern, packet_text, re.DOTALL)

        if match:
            entry1 = match.groupdict()
            data = simple_map_entry(entry1, config)
            entry.update(data)
            return entry
        else:
            # Return None or an empty dictionary if there is no match
            return None