import regex as re
from parser.kpi_utils import simple_map_entry
class Packet_0x156A:
    def extract_info(packet_text,config=None, entry=None):
        pattern = r".*?0x156A.*?Subscription ID = (?P<subscription_id>\d+).*?Direction = (?P<Direction>.*?(?=\n)).*?Rat Type = (?P<rat_type>\w+).*?Type = (?P<Type>.*?(?=\n)).*?Codec Type = (?P<codec_type>.*?(?=\n)).*?"
        match = re.search(pattern, packet_text, re.DOTALL)

        if match:
            entry1 = match.groupdict()
            data = simple_map_entry(entry1, config)
            entry.update(data)
            return entry
        else:
            # Return None or an empty dictionary if there is no match
            return None